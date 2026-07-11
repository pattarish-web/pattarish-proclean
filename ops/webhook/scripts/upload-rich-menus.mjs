#!/usr/bin/env node
/**
 * Create LINE Rich Menus from ops/modules/{role}/rich-menu.json
 * and upload PNG images from ops/modules/{role}/rich-menu.png
 *
 * Usage (from ops/webhook):
 *   node scripts/upload-rich-menus.mjs
 *
 * Requires LINE_CHANNEL_ACCESS_TOKEN in env or .env
 * Prints IDs to paste into .env as RICH_MENU_ID_*
 */
import { readFile, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getConfig } from "../src/config/env.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const modulesRoot = path.join(__dirname, "../../modules");
const API = "https://api-data.line.me/v2/bot/richmenu";
const API_JSON = "https://api.line.me/v2/bot/richmenu";

const MENUS = [
  { role: "customer", envKey: "RICH_MENU_ID_CUSTOMER" },
  { role: "staff", envKey: "RICH_MENU_ID_STAFF" },
  { role: "admin", envKey: "RICH_MENU_ID_ADMIN" },
];

async function exists(p) {
  try {
    await access(p);
    return true;
  } catch {
    return false;
  }
}

async function createRichMenu(token, body) {
  const res = await fetch(API_JSON, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(`create richmenu failed: ${JSON.stringify(data)}`);
  }
  return data.richMenuId;
}

async function uploadImage(token, richMenuId, pngPath) {
  const buf = await readFile(pngPath);
  const res = await fetch(`${API}/${richMenuId}/content`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "image/png",
    },
    body: buf,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`upload image failed (${richMenuId}): ${text}`);
  }
}

async function main() {
  const { line } = getConfig();
  const token = line.channelAccessToken;
  if (!token) {
    console.error("Missing LINE_CHANNEL_ACCESS_TOKEN in .env");
    process.exit(1);
  }

  console.log("Uploading rich menus…\n");
  const results = [];

  for (const { role, envKey } of MENUS) {
    const jsonPath = path.join(modulesRoot, role, "rich-menu.json");
    const pngPath = path.join(modulesRoot, role, "rich-menu.png");
    if (!(await exists(jsonPath))) {
      console.warn(`SKIP ${role}: missing ${jsonPath}`);
      continue;
    }
    if (!(await exists(pngPath))) {
      console.warn(
        `SKIP ${role}: missing ${pngPath} — run scripts/generate-rich-menu-images.py first`
      );
      continue;
    }
    const body = JSON.parse(await readFile(jsonPath, "utf8"));
    const id = await createRichMenu(token, body);
    await uploadImage(token, id, pngPath);
    console.log(`${role.padEnd(10)} ${envKey}=${id}`);
    results.push({ envKey, id });
  }

  if (!results.length) {
    console.error("\nNo menus uploaded.");
    process.exit(1);
  }

  console.log("\nPaste into ops/webhook/.env:\n");
  for (const { envKey, id } of results) {
    console.log(`${envKey}=${id}`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
