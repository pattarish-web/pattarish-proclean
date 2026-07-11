import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { google } from "googleapis";
import { getConfig } from "../src/config/env.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const headersDir = path.join(__dirname, "../../shared/sheets/headers");
const TABS = [
  "customers",
  "staff",
  "jobs",
  "checkins",
  "qc_photos",
  "affiliate",
  "payments",
];

const cfg = getConfig();
const sa = JSON.parse(cfg.sheets.serviceAccountJson);
const spreadsheetId = cfg.sheets.spreadsheetId;
if (!spreadsheetId) throw new Error("GOOGLE_SHEETS_ID missing");

const auth = new google.auth.GoogleAuth({
  credentials: sa,
  scopes: ["https://www.googleapis.com/auth/spreadsheets"],
});
const sheets = google.sheets({ version: "v4", auth });

console.log("spreadsheetId", spreadsheetId);
console.log("as", sa.client_email);

const meta = await sheets.spreadsheets.get({ spreadsheetId });
const existing = new Map(
  (meta.data.sheets || []).map((s) => [s.properties.title, s.properties.sheetId])
);
console.log("existing_tabs", [...existing.keys()].join(", ") || "(none)");

const requests = [];
for (const title of TABS) {
  if (!existing.has(title)) {
    requests.push({ addSheet: { properties: { title } } });
  }
}

// Optional: rename default Sheet1 / ชีต1 -> customers if customers missing
const defaultNames = ["Sheet1", "ชีต1"];
const defaultTitle = defaultNames.find((n) => existing.has(n));
if (!existing.has("customers") && defaultTitle) {
  requests.length = 0;
  requests.push({
    updateSheetProperties: {
      properties: { sheetId: existing.get(defaultTitle), title: "customers" },
      fields: "title",
    },
  });
  for (const title of TABS.slice(1)) {
    if (!existing.has(title)) {
      requests.push({ addSheet: { properties: { title } } });
    }
  }
}

if (requests.length) {
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });
  console.log("tabs_updated", requests.length);
}

for (const tab of TABS) {
  const headerLine = readFileSync(path.join(headersDir, `${tab}.csv`), "utf8")
    .trim()
    .split(/\r?\n/)[0];
  const headers = headerLine.split(",");
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: `${tab}!A1`,
    valueInputOption: "RAW",
    requestBody: { values: [headers] },
  });
  console.log("headers_ok", tab, headers.length);
}

console.log("DONE");
console.log("url", `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`);
