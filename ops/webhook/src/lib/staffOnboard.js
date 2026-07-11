import { getConfig } from "../config/env.js";
import {
  appendRow,
  newId,
  readTable,
  updateRow,
} from "./sheets.js";
import { linkRichMenu, pushOwners, reply, textMsg } from "./line.js";

function todayBangkok() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Bangkok",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

/** Any staff row with this LINE id (any status). */
export async function findAnyStaffByLineId(lineUserId) {
  const rows = await readTable("staff");
  return rows.find((r) => r.line_user_id === lineUserId) || null;
}

/**
 * Upsert staff and switch Rich Menu to staff.
 * @returns {Promise<{ id: string, name: string, created: boolean }>}
 */
export async function upsertStaff({ lineUserId, name, zone = "", salary = "" }) {
  if (!lineUserId || !/^U[0-9a-fA-F]{32}$/i.test(lineUserId)) {
    throw new Error("LINE User ID ไม่ถูกต้อง (ต้องขึ้นต้นด้วย U)");
  }
  const displayName = (name || "แม่บ้าน").trim() || "แม่บ้าน";
  const existing = await findAnyStaffByLineId(lineUserId);
  if (existing) {
    await updateRow(
      "staff",
      (r) => r.line_user_id === lineUserId,
      {
        name: displayName,
        status: "active",
        training_status: existing.training_status || "pending",
      }
    );
    try {
      await linkRichMenu(lineUserId, "staff");
    } catch (err) {
      console.warn("linkRichMenu staff:", err.message);
    }
    return { id: existing.id, name: displayName, created: false };
  }

  const id = newId("ST");
  await appendRow("staff", {
    id,
    name: displayName,
    line_user_id: lineUserId,
    salary,
    zone,
    status: "active",
    training_status: "pending",
    created_at: todayBangkok(),
  });
  try {
    await linkRichMenu(lineUserId, "staff");
  } catch (err) {
    console.warn("linkRichMenu staff:", err.message);
  }
  return { id, name: displayName, created: true };
}

/**
 * Global text commands that work for any role.
 * @returns {Promise<boolean>} true if handled
 */
export async function handleStaffOnboardCommands(event, userId) {
  if (event.type !== "message" || event.message?.type !== "text") return false;
  const raw = event.message.text.trim();
  const cfg = getConfig();
  const joinCode = cfg.staffJoinCode;

  // Show own LINE user id
  if (/^(รหัสของฉัน|myid|my id|userid)$/i.test(raw)) {
    await reply(
      event.replyToken,
      textMsg(
        `LINE User ID ของคุณ:\n${userId}\n\nส่งให้แอดมินเพื่อเพิ่มเป็นแม่บ้าน\nหรือพิมพ์: สมัครแม่บ้าน ${joinCode || "<รหัส>"} ชื่อของคุณ`
      )
    );
    await pushOwners(
      textMsg(`มีคนขอรหัส LINE\nID: ${userId}`)
    );
    return true;
  }

  // Self-register with shared secret
  const join = raw.match(/^สมัครแม่บ้าน\s+(\S+)(?:\s+(.+))?$/u);
  if (join) {
    const code = join[1];
    const name = (join[2] || "").trim();
    if (!joinCode) {
      await reply(
        event.replyToken,
        textMsg("ยังไม่ได้ตั้งรหัสสมัครแม่บ้าน (STAFF_JOIN_CODE)")
      );
      return true;
    }
    if (code !== joinCode) {
      await reply(event.replyToken, textMsg("รหัสสมัครไม่ถูกต้อง"));
      return true;
    }
    if (cfg.line.ownerUserIds.includes(userId)) {
      await reply(
        event.replyToken,
        textMsg("บัญชีนี้เป็นแอดมินอยู่แล้ว ไม่ต้องสมัครแม่บ้าน")
      );
      return true;
    }
    const result = await upsertStaff({ lineUserId: userId, name });
    await reply(
      event.replyToken,
      textMsg(
        result.created
          ? `สมัครแม่บ้านสำเร็จ\nรหัส: ${result.id}\nชื่อ: ${result.name}\nเมนูแม่บ้านพร้อมใช้งานแล้ว`
          : `อัปเดตสถานะแม่บ้านแล้ว\nรหัส: ${result.id}\nชื่อ: ${result.name}`
      )
    );
    await pushOwners(
      textMsg(
        `แม่บ้านใหม่สมัครเอง\n${result.name} · ${result.id}\n${userId}`
      )
    );
    return true;
  }

  return false;
}

/** Admin-only: เพิ่มแม่บ้าน Uxxx ชื่อ */
export async function handleAdminAddStaffCommand(event) {
  if (event.type !== "message" || event.message?.type !== "text") return false;
  const raw = event.message.text.trim();
  const m = raw.match(/^เพิ่มแม่บ้าน\s+(U[0-9a-fA-F]+)\s*(.*)$/u);
  if (!m) return false;
  const lineUserId = m[1];
  const name = (m[2] || "").trim();
  try {
    const result = await upsertStaff({ lineUserId, name });
    await reply(
      event.replyToken,
      textMsg(
        result.created
          ? `เพิ่มแม่บ้านแล้ว\n${result.name} · ${result.id}\n${lineUserId}\nสลับเมนูแม่บ้านให้แล้ว`
          : `มีในระบบแล้ว — อัปเดตเป็น active\n${result.name} · ${result.id}`
      )
    );
    // Notify the staff if possible
    try {
      const { push } = await import("./line.js");
      await push(
        lineUserId,
        textMsg(
          `คุณถูกเพิ่มเป็นแม่บ้านของ Sangkan Office แล้ว\nเปิดเมนูใหม่ หรือพิมพ์ 「คิววันนี้」`
        )
      );
    } catch (err) {
      console.warn("notify new staff:", err.message);
    }
  } catch (err) {
    await reply(event.replyToken, textMsg(`เพิ่มไม่สำเร็จ: ${err.message}`));
  }
  return true;
}
