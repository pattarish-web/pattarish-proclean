import { Readable } from "node:stream";
import { google } from "googleapis";
import { getConfig } from "../config/env.js";

function parseServiceAccount() {
  const raw = getConfig().sheets.serviceAccountJson;
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return JSON.parse(Buffer.from(raw, "base64").toString("utf8"));
  }
}

let _drive = null;
let _authMode = null;

/**
 * Prefer user OAuth for My Drive uploads (SA has no storage quota on personal Drive).
 * Fall back to service account (works for Shared Drives / Workspace).
 */
async function driveClient() {
  if (_drive) return _drive;
  const cfg = getConfig();
  const oauth = cfg.driveOAuth;

  if (oauth?.clientId && oauth?.clientSecret && oauth?.refreshToken) {
    const auth = new google.auth.OAuth2(
      oauth.clientId,
      oauth.clientSecret,
      "http://localhost"
    );
    auth.setCredentials({ refresh_token: oauth.refreshToken });
    _drive = google.drive({ version: "v3", auth });
    _authMode = "oauth";
    return _drive;
  }

  const creds = parseServiceAccount();
  if (!creds) throw new Error("GOOGLE_SERVICE_ACCOUNT_JSON missing");
  const auth = new google.auth.GoogleAuth({
    credentials: creds,
    scopes: ["https://www.googleapis.com/auth/drive"],
  });
  _drive = google.drive({ version: "v3", auth });
  _authMode = "service_account";
  return _drive;
}

export function driveAuthMode() {
  return _authMode;
}

export function drivePublicViewUrl(fileId) {
  return `https://drive.google.com/uc?export=view&id=${fileId}`;
}

export function driveOpenUrl(fileId) {
  return `https://drive.google.com/file/d/${fileId}/view`;
}

/** Safe folder/file label for Google Drive. */
export function sanitizeDriveName(name, fallback = "unknown") {
  const cleaned = String(name || "")
    .replace(/[\\/:*?"<>|]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 80);
  return cleaned || fallback;
}

async function findChildFolder(drive, parentId, name) {
  const q = [
    `'${parentId}' in parents`,
    `name = '${name.replace(/'/g, "\\'")}'`,
    `mimeType = 'application/vnd.google-apps.folder'`,
    `trashed = false`,
  ].join(" and ");
  const res = await drive.files.list({
    q,
    fields: "files(id,name)",
    pageSize: 5,
    supportsAllDrives: true,
    includeItemsFromAllDrives: true,
  });
  return res.data.files?.[0] || null;
}

async function ensureFolder(drive, parentId, name) {
  const safe = sanitizeDriveName(name);
  const existing = await findChildFolder(drive, parentId, safe);
  if (existing) return existing.id;
  const created = await drive.files.create({
    requestBody: {
      name: safe,
      mimeType: "application/vnd.google-apps.folder",
      parents: [parentId],
    },
    fields: "id,name",
    supportsAllDrives: true,
  });
  return created.data.id;
}

/**
 * Ensure nested folders: root / date / staff / customer
 * @returns {Promise<string>} leaf folder id
 */
export async function ensurePowFolderPath({ date, staffName, customerName }) {
  const rootId = getConfig().driveFolderId;
  if (!rootId) {
    throw new Error("GOOGLE_DRIVE_FOLDER_ID missing");
  }
  const drive = await driveClient();
  const dateId = await ensureFolder(drive, rootId, date || "no-date");
  const staffId = await ensureFolder(
    drive,
    dateId,
    staffName || "staff-unknown"
  );
  const customerId = await ensureFolder(
    drive,
    staffId,
    customerName || "customer-unknown"
  );
  return customerId;
}

/**
 * Upload image into dated/staff/customer folder under shared root.
 * Path: {GOOGLE_DRIVE_FOLDER_ID}/{YYYY-MM-DD}/{staffName}/{customerName}/{file}
 */
export async function uploadPowImage({
  buffer,
  filename,
  mimeType = "image/jpeg",
  date,
  staffName,
  customerName,
}) {
  const folderId = await ensurePowFolderPath({
    date,
    staffName,
    customerName,
  });
  const drive = await driveClient();
  const safeName = sanitizeDriveName(filename, `photo-${Date.now()}.jpg`);
  let created;
  try {
    created = await drive.files.create({
      requestBody: {
        name: safeName,
        parents: [folderId],
      },
      media: {
        mimeType,
        body: Readable.from(buffer),
      },
      fields: "id,name,webViewLink,parents",
      supportsAllDrives: true,
    });
  } catch (err) {
    const msg = String(err?.message || err);
    if (
      _authMode === "service_account" &&
      /storageQuotaExceeded|Service Accounts do not have storage quota/i.test(
        msg
      )
    ) {
      throw new Error(
        "Service Account อัปโหลดขึ้น My Drive ส่วนตัวไม่ได้ — ตั้ง GOOGLE_DRIVE_REFRESH_TOKEN (รัน scripts/drive-oauth-setup.mjs) หรือใช้ Shared Drive"
      );
    }
    throw err;
  }
  const fileId = created.data.id;
  try {
    await drive.permissions.create({
      fileId,
      requestBody: { role: "reader", type: "anyone" },
      supportsAllDrives: true,
    });
  } catch (err) {
    console.warn("drive public permission:", err.message);
  }
  return {
    fileId,
    name: created.data.name,
    folderId,
    viewUrl: drivePublicViewUrl(fileId),
    openUrl: driveOpenUrl(fileId),
    webViewLink: created.data.webViewLink || driveOpenUrl(fileId),
    pathHint: `${date}/${staffName}/${customerName}`,
    authMode: _authMode,
  };
}

/** Download image bytes from a LINE message id. */
export async function downloadLineImage(messageId) {
  const token = getConfig().line.channelAccessToken;
  const res = await fetch(
    `https://api-data.line.me/v2/bot/message/${messageId}/content`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  if (!res.ok) {
    throw new Error(`ดาวน์โหลดรูปจาก LINE ไม่สำเร็จ (${res.status})`);
  }
  const mimeType = res.headers.get("content-type") || "image/jpeg";
  const buffer = Buffer.from(await res.arrayBuffer());
  return { buffer, mimeType };
}
