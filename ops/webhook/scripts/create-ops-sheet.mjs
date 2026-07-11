import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { google } from "googleapis";
import { getConfig } from "../src/config/env.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const headersDir = path.join(__dirname, "../../../shared/sheets/headers");

function loadSa() {
  const raw = getConfig().sheets.serviceAccountJson;
  const json = raw.trim().startsWith("{")
    ? JSON.parse(raw)
    : JSON.parse(Buffer.from(raw, "base64").toString("utf8"));
  return json;
}

const TABS = [
  "customers",
  "staff",
  "jobs",
  "checkins",
  "qc_photos",
  "affiliate",
  "payments",
];

async function main() {
  const sa = loadSa();
  const auth = new google.auth.GoogleAuth({
    credentials: sa,
    scopes: [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive.file",
    ],
  });
  const sheets = google.sheets({ version: "v4", auth });
  const drive = google.drive({ version: "v3", auth });

  const existingId = getConfig().sheets.spreadsheetId;
  let spreadsheetId = existingId;

  if (!spreadsheetId) {
    const created = await sheets.spreadsheets.create({
      requestBody: {
        properties: { title: "Sangkan Office Ops" },
        sheets: TABS.map((title) => ({ properties: { title } })),
      },
    });
    spreadsheetId = created.data.spreadsheetId;
    console.log("created", spreadsheetId);
  } else {
    console.log("using_existing", spreadsheetId);
  }

  // Ensure tabs exist
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const have = new Set(
    (meta.data.sheets || []).map((s) => s.properties.title)
  );
  const add = TABS.filter((t) => !have.has(t)).map((title) => ({
    addSheet: { properties: { title } },
  }));
  // drop default Sheet1 if present and unused
  if (have.has("Sheet1") && !TABS.includes("Sheet1")) {
    const sheet1 = meta.data.sheets.find((s) => s.properties.title === "Sheet1");
    if (sheet1) {
      add.push({ deleteSheet: { sheetId: sheet1.properties.sheetId } });
    }
  }
  if (add.length) {
    await sheets.spreadsheets.batchUpdate({
      spreadsheetId,
      requestBody: { requests: add },
    });
  }

  for (const tab of TABS) {
    const csvPath = path.join(headersDir, `${tab}.csv`);
    const headerLine = readFileSync(csvPath, "utf8").trim().split(/\r?\n/)[0];
    const headers = headerLine.split(",");
    await sheets.spreadsheets.values.update({
      spreadsheetId,
      range: `${tab}!A1`,
      valueInputOption: "RAW",
      requestBody: { values: [headers] },
    });
    console.log("headers", tab, headers.length);
  }

  // Make file readable/writable by link is not ideal; print share email instead
  console.log("client_email", sa.client_email);
  console.log("url", `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`);
  console.log("GOOGLE_SHEETS_ID=" + spreadsheetId);
}

main().catch((err) => {
  console.error("FAIL", err.message || err);
  if (err.errors) console.error(JSON.stringify(err.errors, null, 2));
  process.exit(1);
});
