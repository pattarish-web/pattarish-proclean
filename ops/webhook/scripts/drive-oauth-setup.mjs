/**
 * One-time OAuth setup so PoW photos upload as YOUR Google user
 * (Service Accounts cannot store files in personal My Drive).
 *
 * Usage (from ops/webhook):
 *   node scripts/drive-oauth-setup.mjs
 *
 * Opens a browser, you sign in with the Google account that owns the Drive folder,
 * then refresh token is appended to .env
 */
import { createServer } from "node:http";
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { google } from "googleapis";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const envPath = path.join(root, ".env");
const secretCandidates = [
  path.join(root, "../../google_ads/client_secret.json"),
  path.join(root, "client_secret.json"),
];

function loadEnvFile() {
  const out = {};
  if (!existsSync(envPath)) return out;
  for (const raw of readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq <= 0) continue;
    out[line.slice(0, eq).trim()] = line.slice(eq + 1).trim();
  }
  return out;
}

function loadClient() {
  const env = loadEnvFile();
  let clientId = env.GOOGLE_DRIVE_CLIENT_ID || process.env.GOOGLE_DRIVE_CLIENT_ID;
  let clientSecret =
    env.GOOGLE_DRIVE_CLIENT_SECRET || process.env.GOOGLE_DRIVE_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    for (const p of secretCandidates) {
      if (!existsSync(p)) continue;
      const json = JSON.parse(readFileSync(p, "utf8"));
      const installed = json.installed || json.web;
      if (installed?.client_id && installed?.client_secret) {
        clientId = installed.client_id;
        clientSecret = installed.client_secret;
        console.log("Using OAuth client from", p);
        break;
      }
    }
  }

  if (!clientId || !clientSecret) {
    throw new Error(
      "Missing GOOGLE_DRIVE_CLIENT_ID / GOOGLE_DRIVE_CLIENT_SECRET (or google_ads/client_secret.json)"
    );
  }
  return { clientId, clientSecret };
}

// Full drive scope needed to nest under an existing shared folder.
const SCOPES = ["https://www.googleapis.com/auth/drive"];
const REDIRECT = "http://localhost:53682/oauth2callback";

const { clientId, clientSecret } = loadClient();
const oauth2 = new google.auth.OAuth2(clientId, clientSecret, REDIRECT);

const authUrl = oauth2.generateAuthUrl({
  access_type: "offline",
  prompt: "consent",
  scope: SCOPES,
});

console.log("\n1) เปิดลิงก์นี้ในเบราว์เซอร์ (ล็อกอินบัญชีที่ถือโฟลเดอร์ Drive):\n");
console.log(authUrl);
console.log("\n2) รอ callback ที่", REDIRECT, "...\n");

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, REDIRECT);
    if (url.pathname !== "/oauth2callback") {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    const code = url.searchParams.get("code");
    const err = url.searchParams.get("error");
    if (err) {
      res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
      res.end(`OAuth error: ${err}`);
      server.close();
      process.exit(1);
    }
    if (!code) {
      res.writeHead(400);
      res.end("Missing code");
      return;
    }

    const { tokens } = await oauth2.getToken(code);
    if (!tokens.refresh_token) {
      res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
      res.end(
        "ไม่ได้ refresh_token — ลองถอนสิทธิ์แอปใน https://myaccount.google.com/permissions แล้วรันใหม่"
      );
      server.close();
      process.exit(1);
    }

    const lines = [
      "",
      "# Drive upload as your Google user (PoW photos)",
      `GOOGLE_DRIVE_CLIENT_ID=${clientId}`,
      `GOOGLE_DRIVE_CLIENT_SECRET=${clientSecret}`,
      `GOOGLE_DRIVE_REFRESH_TOKEN=${tokens.refresh_token}`,
      "",
    ].join("\n");

    appendFileSync(envPath, lines, "utf8");
    console.log("Saved GOOGLE_DRIVE_* to", envPath);

    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(
      "<h1>สำเร็จ</h1><p>บันทึก refresh token แล้ว ปิดหน้านี้ได้ แล้วรีสตาร์ท webhook</p>"
    );
    server.close();
    process.exit(0);
  } catch (e) {
    console.error(e);
    res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
    res.end(String(e.message || e));
    server.close();
    process.exit(1);
  }
});

server.listen(53682, "127.0.0.1", () => {
  console.log("Listening on", REDIRECT);
  import("node:child_process").then(({ exec }) => {
    const cmd =
      process.platform === "win32"
        ? `start "" "${authUrl}"`
        : process.platform === "darwin"
          ? `open "${authUrl}"`
          : `xdg-open "${authUrl}"`;
    exec(cmd, () => {});
  });
});
