#!/usr/bin/env node
/**
 * Upload PNG content onto existing RICH_MENU_ID_* from .env
 * (does not recreate menus — keeps current IDs / links)
 */
import { readFile, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getConfig } from "../src/config/env.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const modulesRoot = path.join(__dirname, "../../modules");
const API = "https://api-data.line.me/v2/bot/richmenu";

const MENUS = [
  { role: "customer", idKey: "customer" },
  { role: "staff", idKey: "staff" },
  { role: "admin", idKey: "admin" },
];

async function exists(p) {
  try {
    await access(p);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  const cfg = getConfig();
  const token = cfg.line.channelAccessToken;
  if (!token) throw new Error("Missing LINE_CHANNEL_ACCESS_TOKEN");

  for (const { role, idKey } of MENUS) {
    const richMenuId = cfg.richMenuIds[idKey];
    if (!richMenuId) {
      console.warn(`SKIP ${role}: missing RICH_MENU_ID_${idKey.toUpperCase()}`);
      continue;
    }
    const pngPath = path.join(modulesRoot, role, "rich-menu.png");
    if (!(await exists(pngPath))) {
      console.warn(`SKIP ${role}: missing ${pngPath}`);
      continue;
    }
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
      throw new Error(`${role} upload failed: ${await res.text()}`);
    }
    console.log(`updated ${role} -> ${richMenuId} (${buf.length} bytes)`);
  }
  console.log("\nDone. Re-open the LINE chat (or switch menu) to refresh the image.");
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
