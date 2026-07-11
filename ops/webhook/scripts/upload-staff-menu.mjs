#!/usr/bin/env node
/** Upload only the staff rich menu (new id) and print env line. */
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getConfig } from "../src/config/env.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const role = "staff";
const modulesRoot = path.join(__dirname, "../../modules");
const token = getConfig().line.channelAccessToken;
const body = JSON.parse(
  await readFile(path.join(modulesRoot, role, "rich-menu.json"), "utf8")
);
const create = await fetch("https://api.line.me/v2/bot/richmenu", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(body),
});
const created = await create.json();
if (!create.ok) {
  console.error(created);
  process.exit(1);
}
const png = await readFile(path.join(modulesRoot, role, "rich-menu.png"));
const up = await fetch(
  `https://api-data.line.me/v2/bot/richmenu/${created.richMenuId}/content`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "image/png",
    },
    body: png,
  }
);
if (!up.ok) {
  console.error(await up.text());
  process.exit(1);
}
console.log(`RICH_MENU_ID_STAFF=${created.richMenuId}`);
