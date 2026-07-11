import * as line from "@line/bot-sdk";
import { getConfig } from "../config/env.js";

let _client = null;

export function lineClient() {
  if (_client) return _client;
  const { line: cfg } = getConfig();
  _client = new line.messagingApi.MessagingApiClient({
    channelAccessToken: cfg.channelAccessToken,
  });
  return _client;
}

export function lineMiddleware() {
  const { line: cfg } = getConfig();
  return line.middleware({
    channelSecret: cfg.channelSecret,
  });
}

export async function reply(token, messages) {
  const list = Array.isArray(messages) ? messages : [messages];
  await lineClient().replyMessage({
    replyToken: token,
    messages: list,
  });
}

export async function push(userId, messages) {
  const list = Array.isArray(messages) ? messages : [messages];
  await lineClient().pushMessage({
    to: userId,
    messages: list,
  });
}

export async function pushOwners(messages) {
  const { line: cfg } = getConfig();
  for (const id of cfg.ownerUserIds) {
    try {
      await push(id, messages);
    } catch (err) {
      console.error("push owner failed", id, err.message);
    }
  }
}

export async function linkRichMenu(userId, roleKey) {
  const { richMenuIds } = getConfig();
  const menuId = richMenuIds[roleKey];
  if (!menuId) return;
  await lineClient().linkRichMenuIdToUser(userId, menuId);
}

/** Hide per-user rich menu (e.g. before choosing Sangkan Office). */
export async function unlinkRichMenu(userId) {
  await lineClient().unlinkRichMenuIdFromUser(userId);
}

export function textMsg(text) {
  return { type: "text", text };
}
