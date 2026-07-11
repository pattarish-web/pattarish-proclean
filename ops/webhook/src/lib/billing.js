/**
 * Billing + credit ledger for Sangkan Office LINE payments.
 * Transfer + slip → admin confirm. Affiliate 10% from full package (amount_thb).
 */
import { PACKAGES } from "../config/packages.js";
import { getConfig } from "../config/env.js";
import {
  appendRow,
  newId,
  readTable,
  updateRow,
} from "./sheets.js";
import { push, pushOwners, textMsg } from "./line.js";
import { billFlex, pendingPaymentAdminFlex } from "./flex.js";

/**
 * Apply affiliate credit to a bill amount.
 * Net payable floors at 0; unused credit remains for next period.
 */
export function applyCreditToBill(billThb, creditThb) {
  const bill = Math.max(0, Number(billThb) || 0);
  const credit = Math.max(0, Number(creditThb) || 0);
  const used = Math.min(bill, credit);
  return {
    payable: bill - used,
    creditRemaining: credit - used,
    creditUsed: used,
  };
}

function bankTransferText() {
  const info = getConfig().bankTransferInfo || "";
  return info.trim() || "โอน PromptPay / บัญชีบริษัท ตามที่แอดมินแจ้ง";
}

/**
 * Create a bill, reserve credit, push Flex to customer + notify admin.
 * @param {{ customerId: string, type?: "deposit"|"subscription"|"topup", amountThb?: number, note?: string, adminUserId?: string }} opts
 */
export async function createBill(opts) {
  const {
    customerId,
    type = "subscription",
    amountThb,
    note = "",
    adminUserId = "",
  } = opts;

  const customers = await readTable("customers");
  const customer = customers.find((c) => c.id === customerId);
  if (!customer) throw new Error("Customer not found");

  const pkg = String(customer.package || "").toUpperCase();
  const packagePrice = PACKAGES[pkg]?.price || 0;

  let amount = Number(amountThb);
  if (!Number.isFinite(amount) || amount < 0) {
    if (type === "deposit") {
      amount = Number(customer.deposit_thb) || 500;
    } else if (type === "subscription") {
      amount = packagePrice;
      if (!amount) throw new Error("Customer has no package price");
    } else {
      throw new Error("amountThb required for topup");
    }
  }

  // Prevent duplicate open bills of same type
  const payments = await readTable("payments");
  const open = payments.find(
    (p) =>
      p.customer_id === customerId &&
      p.type === type &&
      p.status === "pending"
  );
  if (open) {
    throw new Error(`Already has pending ${type} bill: ${open.id}`);
  }

  let creditApplied = 0;
  let depositApplied = 0;
  let creditBalance = Number(customer.billing_credit_thb) || 0;
  let remaining = amount;

  if (type === "subscription") {
    // Apply paid deposit first (Early Bird)
    if (String(customer.deposit_status).toLowerCase() === "paid") {
      depositApplied = Math.min(remaining, Number(customer.deposit_thb) || 0);
      remaining -= depositApplied;
    }
    const creditResult = applyCreditToBill(remaining, creditBalance);
    creditApplied = creditResult.creditUsed;
    remaining = creditResult.payable;
    creditBalance = creditResult.creditRemaining;
  }

  const payable = Math.max(0, remaining);
  const paymentId = newId("PAY");

  // Reserve credit immediately (restore on reject)
  if (creditApplied > 0) {
    await updateRow(
      "customers",
      (r) => r.id === customerId,
      { billing_credit_thb: creditBalance }
    );
  }

  const row = {
    id: paymentId,
    customer_id: customerId,
    type,
    amount_thb: amount,
    credit_applied_thb: creditApplied,
    deposit_applied_thb: depositApplied,
    payable_thb: payable,
    method: "transfer",
    slip_url: "",
    status: "pending",
    confirmed_by: "",
    confirmed_at: "",
    note: note || (adminUserId ? `created_by:${adminUserId}` : ""),
    created_at: new Date().toISOString(),
  };
  await appendRow("payments", row);

  const typeLabel =
    type === "deposit"
      ? "มัดจำ Early Bird"
      : type === "subscription"
        ? "ค่าบริการรายเดือน"
        : "เติมเงิน";

  if (customer.line_user_id) {
    await push(customer.line_user_id, [
      billFlex({
        paymentId,
        companyName: customer.company_name || customerId,
        typeLabel,
        packageId: pkg,
        amount,
        creditApplied,
        depositApplied,
        payable,
        bankInfo: bankTransferText(),
      }),
      textMsg(
        payable > 0
          ? `โอน ฿${payable.toLocaleString("th-TH")} แล้วส่งรูปสลิปในแชทนี้ได้เลย\nรหัสบิล: ${paymentId}`
          : `ยอดสุทธิ ฿0 (ใช้เครดิต/มัดจำครบ) — แอดมินจะยืนยันปิดบิล ${paymentId}`
      ),
    ]);
  }

  await pushOwners(
    textMsg(
      `ออกบิลแล้ว: ${paymentId}\n${customer.company_name || customerId} · ${typeLabel}\nยอดเต็ม ฿${amount.toLocaleString("th-TH")} → โอน ฿${payable.toLocaleString("th-TH")}`
    )
  );

  // Zero payable: still needs admin confirm to close + affiliate
  if (payable === 0) {
    await pushOwners(
      pendingPaymentAdminFlex({
        paymentId,
        companyName: customer.company_name || customerId,
        payable: 0,
        typeLabel,
        note: "ยอด 0 — กดยืนยันเพื่อปิดบิล",
      })
    );
  }

  return {
    paymentId,
    amount,
    creditApplied,
    depositApplied,
    payable,
    type,
  };
}

/**
 * Attach slip (LINE message id or URL) to the customer's latest pending bill.
 */
export async function attachSlip({ customerId, slipUrl, lineUserId }) {
  const payments = await readTable("payments");
  const pending = payments
    .filter(
      (p) => p.customer_id === customerId && p.status === "pending"
    )
    .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
  const bill = pending[0];
  if (!bill) throw new Error("No pending bill to attach slip");

  await updateRow(
    "payments",
    (p) => p.id === bill.id,
    { slip_url: slipUrl }
  );

  const customers = await readTable("customers");
  const customer = customers.find((c) => c.id === customerId);
  const typeLabel =
    bill.type === "deposit"
      ? "มัดจำ"
      : bill.type === "subscription"
        ? "รายเดือน"
        : "เติมเงิน";

  await pushOwners([
    textMsg(
      `สลิปใหม่จาก ${customer?.company_name || customerId}\nบิล ${bill.id} · ${typeLabel}\nยอดโอน ฿${Number(bill.payable_thb).toLocaleString("th-TH")}\nslip: ${slipUrl}`
    ),
    pendingPaymentAdminFlex({
      paymentId: bill.id,
      companyName: customer?.company_name || customerId,
      payable: Number(bill.payable_thb) || 0,
      typeLabel,
      note: "ตรวจสลิปในแชทลูกค้าแล้วกดยืนยัน/ปฏิเสธ",
    }),
  ]);

  return { paymentId: bill.id };
}

/**
 * Confirm payment: update deposit/subscription, apply affiliate from full package amount.
 */
export async function confirmPayment({
  paymentId,
  adminUserId = "",
  applyAffiliateFn,
}) {
  const payments = await readTable("payments");
  const bill = payments.find((p) => p.id === paymentId);
  if (!bill) throw new Error("Payment not found");
  if (bill.status !== "pending") {
    throw new Error(`Payment already ${bill.status}`);
  }

  const customers = await readTable("customers");
  const customer = customers.find((c) => c.id === bill.customer_id);
  if (!customer) throw new Error("Customer not found");

  const payable = Number(bill.payable_thb) || 0;
  const packageAmount = Number(bill.amount_thb) || 0;
  const depositApplied = Number(bill.deposit_applied_thb) || 0;
  const now = new Date().toISOString();

  await updateRow(
    "payments",
    (p) => p.id === paymentId,
    {
      status: "confirmed",
      confirmed_by: adminUserId,
      confirmed_at: now,
    }
  );

  const customerPatch = {};
  if (bill.type === "deposit") {
    customerPatch.deposit_status = "paid";
  }
  if (bill.type === "subscription") {
    if (depositApplied > 0 && String(customer.deposit_status).toLowerCase() === "paid") {
      customerPatch.deposit_status = "applied";
    }
    if (["booked", "lead"].includes(String(customer.status).toLowerCase())) {
      customerPatch.status = "active";
    }
  }
  if (Object.keys(customerPatch).length) {
    await updateRow(
      "customers",
      (r) => r.id === customer.id,
      customerPatch
    );
  }

  // Affiliate from full package (amount_thb), even if payable is ฿0 after credit/deposit
  let affiliateResult = null;
  if (
    bill.type === "subscription" &&
    packageAmount > 0 &&
    typeof applyAffiliateFn === "function"
  ) {
    affiliateResult = await applyAffiliateFn({
      referredCustomerId: customer.id,
      paymentThb: packageAmount,
      paymentDate: now.slice(0, 10),
    });
  }

  const creditLeft = Number(
    (await readTable("customers")).find((c) => c.id === customer.id)
      ?.billing_credit_thb || 0
  );

  if (customer.line_user_id) {
    await push(
      customer.line_user_id,
      textMsg(
        `ชำระสำเร็จ บิล ${paymentId}\nยอดที่โอน ฿${payable.toLocaleString("th-TH")}\nเครดิตคงเหลือ ฿${creditLeft.toLocaleString("th-TH")}`
      )
    );
  }

  await pushOwners(
    textMsg(
      `ยืนยันชำระแล้ว: ${paymentId}\n${customer.company_name || customer.id} · ฿${payable.toLocaleString("th-TH")}` +
        (affiliateResult?.credit
          ? `\nAffiliate +฿${affiliateResult.credit} → ${affiliateResult.referrerId}`
          : "")
    )
  );

  return { paymentId, payable, affiliateResult };
}

/**
 * Reject payment and restore reserved credit.
 */
export async function rejectPayment({ paymentId, adminUserId = "", reason = "" }) {
  const payments = await readTable("payments");
  const bill = payments.find((p) => p.id === paymentId);
  if (!bill) throw new Error("Payment not found");
  if (bill.status !== "pending") {
    throw new Error(`Payment already ${bill.status}`);
  }

  const creditApplied = Number(bill.credit_applied_thb) || 0;
  if (creditApplied > 0) {
    const customers = await readTable("customers");
    const customer = customers.find((c) => c.id === bill.customer_id);
    if (customer) {
      const prev = Number(customer.billing_credit_thb) || 0;
      await updateRow(
        "customers",
        (r) => r.id === customer.id,
        { billing_credit_thb: prev + creditApplied }
      );
    }
  }

  await updateRow(
    "payments",
    (p) => p.id === paymentId,
    {
      status: "rejected",
      confirmed_by: adminUserId,
      confirmed_at: new Date().toISOString(),
      note: [bill.note, reason ? `rejected:${reason}` : "rejected"]
        .filter(Boolean)
        .join(" | "),
    }
  );

  const customers = await readTable("customers");
  const customer = customers.find((c) => c.id === bill.customer_id);
  if (customer?.line_user_id) {
    await push(
      customer.line_user_id,
      textMsg(
        `สลิป/บิล ${paymentId} ยังไม่ผ่าน${reason ? ` (${reason})` : ""}\nกรุณาส่งสลิปใหม่ หรือพิมพ์ 「บิล」 เพื่อดูยอดอีกครั้ง`
      )
    );
  }

  return { paymentId, creditRestored: creditApplied };
}

export async function listPendingPayments(limit = 10) {
  const payments = await readTable("payments");
  return payments
    .filter((p) => p.status === "pending")
    .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)))
    .slice(0, limit);
}
