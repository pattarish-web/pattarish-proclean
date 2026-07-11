#!/usr/bin/env node
/**
 * One-shot bootstrap after secrets are in ops/webhook/.env
 *
 * Does: health check → upload rich menus → print LIFF/Webhook URLs to configure
 *
 * Usage:
 *   cd ops/webhook
 *   node scripts/bootstrap-connect.mjs
 */
import { getConfig } from "../src/config/env.js";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");

function must(name, val) {
  if (!val || !String(val).trim()) {
    throw new Error(`Missing ${name} in .env`);
  }
}

function run(cmd, args) {
  console.log(`\n> ${cmd} ${args.join(" ")}`);
  const r = spawnSync(cmd, args, {
    cwd: root,
    stdio: "inherit",
    shell: process.platform === "win32",
  });
  if (r.status !== 0) process.exit(r.status || 1);
}

async function main() {
  const cfg = getConfig();
  must("LINE_CHANNEL_SECRET", cfg.line.channelSecret);
  must("LINE_CHANNEL_ACCESS_TOKEN", cfg.line.channelAccessToken);
  must("LINE_OWNER_USER_ID", cfg.line.ownerUserIds.join(","));
  must("GOOGLE_SHEETS_ID", cfg.sheets.spreadsheetId);
  must("GOOGLE_SERVICE_ACCOUNT_JSON", cfg.sheets.serviceAccountJson);
  must("PUBLIC_BASE_URL", cfg.publicBaseUrl);
  if (cfg.publicBaseUrl.includes("localhost")) {
    console.warn(
      "WARN: PUBLIC_BASE_URL is localhost — set the deployed HTTPS URL before LIFF/Webhook."
    );
  }

  console.log("Secrets present. Uploading rich menus…");
  run("npm", ["run", "richmenu:images"]);
  run("npm", ["run", "richmenu:upload"]);

  const base = cfg.publicBaseUrl.replace(/\/$/, "");
  console.log(`
============================================================
Next (LINE Developers console) — paste these URLs:

Webhook URL:
  ${base}/webhook

LIFF endpoints (create 3 apps, size Full):
  Booking  → ${base}/liff/booking
  Check-in → ${base}/liff/checkin
  PoW      → ${base}/liff/pow

Then put LIFF IDs back into .env:
  LIFF_BOOKING_ID=...
  LIFF_CHECKIN_ID=...
  LIFF_POW_ID=...

Redeploy / restart so LIFF IDs inject into HTML.
Health check: ${base}/health
============================================================
`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
