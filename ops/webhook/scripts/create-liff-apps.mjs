import { getConfig } from "../src/config/env.js";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const cfg = getConfig();
const base = cfg.publicBaseUrl.replace(/\/$/, "");
const token = cfg.line.channelAccessToken;

const apps = [
  { key: "LIFF_BOOKING_ID", description: "Sangkan booking", path: "/liff/booking" },
  { key: "LIFF_CHECKIN_ID", description: "Sangkan checkin", path: "/liff/checkin" },
  { key: "LIFF_POW_ID", description: "Sangkan pow", path: "/liff/pow" },
];

const created = {};
for (const app of apps) {
  const res = await fetch("https://api.line.me/liff/v1/apps", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      view: { type: "full", url: `${base}${app.path}` },
      description: app.description,
      features: { ble: false, qrCode: false },
      permanentLinkPattern: "concat",
      scope: ["profile", "openid"],
      botPrompt: "normal",
    }),
  });
  const body = await res.json();
  if (!res.ok) {
    console.error("FAIL", app.key, res.status, JSON.stringify(body));
    process.exit(1);
  }
  created[app.key] = body.liffId;
  console.log(app.key, body.liffId);
}

const envPath = path.join(path.dirname(fileURLToPath(import.meta.url)), "../.env");
let text = readFileSync(envPath, "utf8");
for (const [k, v] of Object.entries(created)) {
  if (text.includes(`${k}=`)) {
    text = text.replace(new RegExp(`${k}=.*`), `${k}=${v}`);
  } else {
    text += `${k}=${v}\n`;
  }
}
writeFileSync(envPath, text.endsWith("\n") ? text : text + "\n", "utf8");
console.log("env_updated");
