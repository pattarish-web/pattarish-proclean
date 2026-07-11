import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { google } from "googleapis";
import { getConfig } from "../src/config/env.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const headersDir = path.join(__dirname, "../../../shared/sheets/headers");
const TABS = [
  "customers",
  "staff",
  "jobs",
  "checkins",
  "qc_photos",
  "affiliate",
  "payments",
];

const sa = JSON.parse(getConfig().sheets.serviceAccountJson);
const auth = new google.auth.GoogleAuth({
  credentials: sa,
  scopes: [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
  ],
});
const sheets = google.sheets({ version: "v4", auth });
const drive = google.drive({ version: "v3", auth });

console.log("email", sa.client_email);

// Create spreadsheet file via Drive
const created = await drive.files.create({
  requestBody: {
    name: "Sangkan Office Ops",
    mimeType: "application/vnd.google-apps.spreadsheet",
  },
  fields: "id,name,webViewLink",
});
const spreadsheetId = created.data.id;
console.log("created_via_drive", spreadsheetId);

const meta = await sheets.spreadsheets.get({ spreadsheetId });
const first = meta.data.sheets[0];
const requests = [];

// Rename first sheet to customers
requests.push({
  updateSheetProperties: {
    properties: { sheetId: first.properties.sheetId, title: "customers" },
    fields: "title",
  },
});
// Add remaining tabs
for (const title of TABS.slice(1)) {
  requests.push({ addSheet: { properties: { title } } });
}
await sheets.spreadsheets.batchUpdate({
  spreadsheetId,
  requestBody: { requests },
});

for (const tab of TABS) {
  const headerLine = readFileSync(
    path.join(headersDir, `${tab}.csv`),
    "utf8"
  )
    .trim()
    .split(/\r?\n/)[0];
  const headers = headerLine.split(",");
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: `${tab}!A1`,
    valueInputOption: "RAW",
    requestBody: { values: [headers] },
  });
  console.log("headers", tab);
}

console.log("url", `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`);
console.log("GOOGLE_SHEETS_ID=" + spreadsheetId);
