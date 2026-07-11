import { HIRE_THRESHOLDS, PACKAGES } from "../../config/packages.js";
import { thresholdFlex, jobListFlex } from "../../lib/flex.js";
import { reply, pushOwners, textMsg } from "../../lib/line.js";
import { readTable } from "../../lib/sheets.js";
import { handleAdminAddStaffCommand } from "../../lib/staffOnboard.js";
import {
  createBill,
  confirmPayment,
  rejectPayment,
  listPendingPayments,
} from "../../lib/billing.js";
import { applyAffiliateOnPayment } from "../customer/index.js";

function todayBangkok() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Bangkok",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

export function computeThreshold(customers) {
  const booked = customers.filter((c) =>
    ["booked", "active"].includes(String(c.status).toLowerCase())
  );
  const counts = { S: 0, M: 0, L: 0 };
  let revenue = 0;
  for (const c of booked) {
    const pkg = String(c.package || "").toUpperCase();
    if (counts[pkg] !== undefined) {
      counts[pkg] += 1;
      revenue += PACKAGES[pkg]?.price || 0;
    }
  }
  const hireReady =
    counts.L >= HIRE_THRESHOLDS.L ||
    counts.M >= HIRE_THRESHOLDS.M ||
    counts.S >= HIRE_THRESHOLDS.S ||
    revenue >= HIRE_THRESHOLDS.revenueMin;

  const lines = [
    `เกณฑ์: L≥${HIRE_THRESHOLDS.L} หรือ M≥${HIRE_THRESHOLDS.M} หรือ S≥${HIRE_THRESHOLDS.S} หรือ ≥฿${HIRE_THRESHOLDS.revenueMin.toLocaleString("th-TH")}`,
  ];
  return { counts, revenue, hireReady, lines, booked };
}

export async function handleAdminEvent(event, userId) {
  if (await handleAdminAddStaffCommand(event)) return;

  if (event.type === "postback") {
    const data = new URLSearchParams(event.postback?.data || "");
    const action = data.get("action");

    if (action === "billing_confirm") {
      try {
        const result = await confirmPayment({
          paymentId: data.get("payment_id"),
          adminUserId: userId,
          applyAffiliateFn: applyAffiliateOnPayment,
        });
        if (event.replyToken) {
          await reply(
            event.replyToken,
            textMsg(
              `ยืนยันแล้ว ${result.paymentId}\nยอด ฿${Number(result.payable).toLocaleString("th-TH")}`
            )
          );
        }
      } catch (err) {
        if (event.replyToken) {
          await reply(event.replyToken, textMsg(`ยืนยันไม่สำเร็จ: ${err.message}`));
        }
      }
      return;
    }

    if (action === "billing_reject") {
      try {
        await rejectPayment({
          paymentId: data.get("payment_id"),
          adminUserId: userId,
          reason: "สลิปไม่ผ่าน",
        });
        if (event.replyToken) {
          await reply(event.replyToken, textMsg("ปฏิเสธบิลแล้ว — แจ้งลูกค้าแล้ว"));
        }
      } catch (err) {
        if (event.replyToken) {
          await reply(event.replyToken, textMsg(`ปฏิเสธไม่สำเร็จ: ${err.message}`));
        }
      }
      return;
    }

    if (action === "admin_threshold") {
      await sendThreshold(event.replyToken);
      return;
    }
    if (action === "admin_today") {
      await sendTodayJobs(event.replyToken);
      return;
    }
    if (action === "admin_warning") {
      await sendWarningSummary(event.replyToken);
      return;
    }
    if (action === "admin_new_customers") {
      await sendNewCustomers(event.replyToken);
      return;
    }
    if (action === "admin_staff") {
      await sendStaffStatus(event.replyToken);
      return;
    }
    if (action === "admin_billing" || action === "admin_payments") {
      await sendPendingPayments(event.replyToken);
      return;
    }
    if (action === "admin_test_warn") {
      await pushOwners(
        textMsg(`[ทดสอบ] Early Warning จากแอดมิน ${userId} · ${new Date().toISOString()}`)
      );
      await reply(event.replyToken, textMsg("ส่งข้อความทดสอบไปยังเจ้าของแล้ว"));
      return;
    }
    if (action === "admin_bill_customer") {
      const customerId = data.get("customer_id");
      const type = data.get("type") || "subscription";
      try {
        const result = await createBill({
          customerId,
          type,
          adminUserId: userId,
        });
        if (event.replyToken) {
          await reply(
            event.replyToken,
            textMsg(
              `ออกบิล ${result.paymentId}\nโอน ฿${result.payable.toLocaleString("th-TH")} (เครดิต −฿${result.creditApplied})`
            )
          );
        }
      } catch (err) {
        if (event.replyToken) {
          await reply(event.replyToken, textMsg(`ออกบิลไม่สำเร็จ: ${err.message}`));
        }
      }
      return;
    }
  }

  if (event.type === "message" && event.message?.type === "text") {
    const raw = event.message.text.trim();
    const t = raw.toLowerCase();

    // ออกบิล CUS-xxx [deposit|subscription]
    const billMatch = raw.match(
      /^ออกบิล\s+(\S+)(?:\s+(มัดจำ|deposit|รายเดือน|subscription))?$/i
    );
    if (billMatch) {
      const customerId = billMatch[1];
      const kind = (billMatch[2] || "subscription").toLowerCase();
      const type =
        kind === "มัดจำ" || kind === "deposit" ? "deposit" : "subscription";
      try {
        const result = await createBill({
          customerId,
          type,
          adminUserId: userId,
        });
        await reply(
          event.replyToken,
          textMsg(
            `ออกบิลแล้ว ${result.paymentId}\nประเภท ${type}\nยอดโอน ฿${result.payable.toLocaleString("th-TH")}`
          )
        );
      } catch (err) {
        await reply(event.replyToken, textMsg(`ออกบิลไม่สำเร็จ: ${err.message}`));
      }
      return;
    }

    // ยืนยันชำระ PAY-xxx
    const confirmMatch = raw.match(/^ยืนยัน(?:ชำระ)?\s+(\S+)/i);
    if (confirmMatch) {
      try {
        const result = await confirmPayment({
          paymentId: confirmMatch[1],
          adminUserId: userId,
          applyAffiliateFn: applyAffiliateOnPayment,
        });
        await reply(
          event.replyToken,
          textMsg(`ยืนยันแล้ว ${result.paymentId} · ฿${result.payable}`)
        );
      } catch (err) {
        await reply(event.replyToken, textMsg(err.message));
      }
      return;
    }

    // ปฏิเสธ PAY-xxx
    const rejectMatch = raw.match(/^ปฏิเสธ\s+(\S+)(?:\s+(.+))?$/i);
    if (rejectMatch) {
      try {
        await rejectPayment({
          paymentId: rejectMatch[1],
          adminUserId: userId,
          reason: rejectMatch[2] || "สลิปไม่ผ่าน",
        });
        await reply(event.replyToken, textMsg("ปฏิเสธแล้ว"));
      } catch (err) {
        await reply(event.replyToken, textMsg(err.message));
      }
      return;
    }

    if (t.includes("ยอด") || t.includes("threshold") || t.includes("จอง")) {
      await sendThreshold(event.replyToken);
      return;
    }
    if (t.includes("งานวันนี้") || t.includes("today")) {
      await sendTodayJobs(event.replyToken);
      return;
    }
    if (t.includes("warning") || t.includes("เตือน")) {
      await sendWarningSummary(event.replyToken);
      return;
    }
    if (t.includes("ลูกค้าใหม่") || t.includes("new")) {
      await sendNewCustomers(event.replyToken);
      return;
    }
    if (t.includes("แม่บ้าน") || t.includes("staff")) {
      await sendStaffStatus(event.replyToken);
      return;
    }
    if (
      t.includes("บิลค้าง") ||
      t.includes("สลิป") ||
      t.includes("ชำระ") ||
      t.includes("payment")
    ) {
      await sendPendingPayments(event.replyToken);
      return;
    }
    if (t.includes("ทดสอบ")) {
      await pushOwners(textMsg(`[ทดสอบ] ${new Date().toISOString()}`));
      await reply(event.replyToken, textMsg("ส่งทดสอบแล้ว"));
      return;
    }
  }

  if (event.replyToken) {
    await reply(
      event.replyToken,
      textMsg(
        "แดชบอร์ด: 「ยอดจอง」 「งานวันนี้」 「เตือน」 「ลูกค้าใหม่」 「แม่บ้าน」 「บิลค้าง」 「ทดสอบ」\n" +
          "ออกบิล: 「ออกบิล CUS-xxx」 หรือ 「ออกบิล CUS-xxx มัดจำ」\n" +
          "ยืนยัน: 「ยืนยัน PAY-xxx」 · ปฏิเสธ: 「ปฏิเสธ PAY-xxx」"
      )
    );
  }
}

async function sendThreshold(replyToken) {
  const customers = await readTable("customers");
  const stats = computeThreshold(customers);
  await reply(replyToken, thresholdFlex(stats));
}

async function sendTodayJobs(replyToken) {
  const date = todayBangkok();
  const jobs = (await readTable("jobs")).filter((j) => j.date === date);
  const customers = await readTable("customers");
  const byId = Object.fromEntries(customers.map((c) => [c.id, c]));
  const checked = jobs.filter((j) =>
    ["checked_in", "done"].includes(j.status)
  ).length;
  await reply(replyToken, [
    textMsg(`งานวันนี้ ${date}: เช็คอิน/เสร็จ ${checked}/${jobs.length}`),
    jobListFlex("งานวันนี้", jobs, byId),
  ]);
}

async function sendWarningSummary(replyToken) {
  const jobs = await readTable("jobs");
  const date = todayBangkok();
  const risky = jobs.filter(
    (j) =>
      j.date === date &&
      !["checked_in", "done", "cancelled"].includes(j.status) &&
      j.warned_at
  );
  if (!risky.length) {
    await reply(replyToken, textMsg("วันนี้ยังไม่มีรายการที่เคยถูก Early Warning"));
    return;
  }
  const lines = risky.map(
    (j) => `• ${j.time_slot} ${j.id} (${j.type}) warned ${j.warned_at}`
  );
  await reply(replyToken, textMsg(`Early Warning วันนี้\n${lines.join("\n")}`));
}

async function sendNewCustomers(replyToken) {
  const customers = await readTable("customers");
  const recent = [...customers]
    .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)))
    .slice(0, 8);
  if (!recent.length) {
    await reply(replyToken, textMsg("ยังไม่มีลูกค้าในระบบ"));
    return;
  }
  const text = recent
    .map(
      (c) =>
        `• ${c.company_name || c.id} · ${c.package} · ${c.status} · มัดจำ ${c.deposit_status}`
    )
    .join("\n");
  await reply(replyToken, textMsg(`ลูกค้าใหม่ล่าสุด\n${text}`));
}

async function sendStaffStatus(replyToken) {
  const staff = await readTable("staff");
  if (!staff.length) {
    await reply(
      replyToken,
      textMsg("ยังไม่มีแม่บ้านในระบบ (จะเพิ่มตอนเดือนจ้าง)")
    );
    return;
  }
  const text = staff
    .map((s) => `• ${s.name} · ${s.status} · zone ${s.zone || "—"}`)
    .join("\n");
  await reply(replyToken, textMsg(`สถานะแม่บ้าน\n${text}`));
}

async function sendPendingPayments(replyToken) {
  const pending = await listPendingPayments(15);
  if (!pending.length) {
    await reply(replyToken, textMsg("ไม่มีบิลค้างรอตรวจ"));
    return;
  }
  const customers = await readTable("customers");
  const byId = Object.fromEntries(customers.map((c) => [c.id, c]));
  const lines = pending.map((p) => {
    const name = byId[p.customer_id]?.company_name || p.customer_id;
    const slip = p.slip_url ? "มีสลิป" : "รอสลิป";
    return `• ${p.id} · ${name} · ${p.type} · ฿${p.payable_thb} · ${slip}`;
  });
  await reply(
    replyToken,
    textMsg(
      `บิลค้าง ${pending.length} รายการ\n${lines.join("\n")}\n\nยืนยัน: 「ยืนยัน PAY-…」\nปฏิเสธ: 「ปฏิเสธ PAY-…」`
    )
  );
}

export async function handleAdminAlias(action, event, userId) {
  const map = {
    threshold: () => sendThreshold(event.replyToken),
    today: () => sendTodayJobs(event.replyToken),
    warning: () => sendWarningSummary(event.replyToken),
    new_customers: () => sendNewCustomers(event.replyToken),
    staff: () => sendStaffStatus(event.replyToken),
    billing: () => sendPendingPayments(event.replyToken),
    payments: () => sendPendingPayments(event.replyToken),
    test_warn: async () => {
      await pushOwners(textMsg(`[ทดสอบ] ${new Date().toISOString()}`));
      await reply(event.replyToken, textMsg("ส่งทดสอบแล้ว"));
    },
  };
  if (map[action]) await map[action]();
}
