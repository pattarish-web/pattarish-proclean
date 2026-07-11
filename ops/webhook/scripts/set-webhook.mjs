import { getConfig } from "../src/config/env.js";

const cfg = getConfig();
const base = (process.argv[2] || cfg.publicBaseUrl).replace(/\/$/, "");
const endpoint = `${base}/webhook`;
const token = cfg.line.channelAccessToken;

console.log("endpoint", endpoint);

const put = await fetch("https://api.line.me/v2/bot/channel/webhook/endpoint", {
  method: "PUT",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ endpoint }),
});
console.log("set_status", put.status, await put.text());

const test = await fetch("https://api.line.me/v2/bot/channel/webhook/test", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ endpoint }),
});
const testBody = await test.json();
console.log("test_status", test.status, JSON.stringify(testBody));
