import { packagesFlex, serviceChooserFlex, SERVICE_URLS, billFlex } from "../../lib/flex.js";
import { reply, push, textMsg, pushOwners, linkRichMenu, unlinkRichMenu } from "../../lib/line.js";
import {
  appendRow,
  findCustomerByLineId,
  newId,
  readTable,
  updateRow,
} from "../../lib/sheets.js";
import { getConfig } from "../../config/env.js";
import { isPromoActive, promoStatusLine, todayBangkok } from "../../config/promo.js";
import { PACKAGES } from "../../config/packages.js";
import { attachSlip } from "../../lib/billing.js";

function bookingLiffUrl() {
  const { liff, publicBaseUrl } = getConfig();
  if (liff.bookingId) return `https://liff.line.me/${liff.bookingId}`;
  return `${publicBaseUrl}/liff/booking`;
}

function welcomeMessages() {
  return [
    textMsg(
      "สวัสดีครับ จาก Sangkan Clean\nกรุณาเลือกบริการที่สนใจด้านล่าง — จะได้ไม่สับสนระหว่าง Big Clean / แม่บ้านประจำ / ออฟฟิศรายเดือน"
    ),
    serviceChooserFlex(),
  ];
}

async function hideOfficeMenu(userId) {
  try {
    await unlinkRichMenu(userId);
  } catch (err) {
    console.warn("unlinkRichMenu:", err.message);
  }
}

async function showOfficeMenu(userId) {
  try {
    await linkRichMenu(userId, "customer");
  } catch (err) {
    console.warn("linkRichMenu customer:", err.message);
  }
}

async function replyServiceChoice(replyToken, service, userId) {
  if (service === "office") {
    await showOfficeMenu(userId);
    await reply(replyToken, [
      textMsg(
        "Sangkan Office — ทำความสะอาดออฟฟิศพรีเมียม โซนอุดมสุข\nเมนูด้านล่างพร้อมแล้ว — เลือกแพ็คเกจได้เลย\nพิมพ์ 「เมนูหลัก」 หากอยากกลับไปเลือกบริการอื่น"
      ),
      packagesFlex(),
    ]);
    return;
  }

  if (service === "bigclean") {
    await hideOfficeMenu(userId);
    await reply(replyToken, [
      textMsg(
        "Big Cleaning — งานทำความสะอาดใหญ่ครั้งคราว\nดูรายละเอียดได้จากปุ่มด้านล่าง หรือพิมพ์รายละเอียดสถานที่/วันเวลา แล้วแอดมินจะติดต่อกลับ"
      ),
      {
        type: "template",
        altText: "Big Cleaning",
        template: {
          type: "buttons",
          text: "Big Cleaning โดย Sangkan Clean",
          actions: [
            {
              type: "uri",
              label: "ดูหน้า Big Clean",
              uri: SERVICE_URLS.bigclean,
            },
            {
              type: "message",
              label: "ขอคุยแอดมิน",
              text: "สนใจ Big Cleaning ขอคุยแอดมิน",
            },
            {
              type: "postback",
              label: "เมนูหลัก",
              data: "action=choose_service&service=menu",
              displayText: "เมนูหลัก",
            },
          ],
        },
      },
    ]);
    await pushOwners(textMsg(`ลูกค้าสนใจ Big Cleaning\n${userId}`));
    return;
  }

  if (service === "maid") {
    await hideOfficeMenu(userId);
    await reply(replyToken, [
      textMsg(
        "แม่บ้านประจำ — จ้างแม่บ้านรายเดือนตามแพ็คเกจปกติของ Sangkan Clean\nดูรายละเอียดได้จากปุ่มด้านล่าง หรือพิมพ์ความต้องการ แล้วแอดมินจะติดต่อกลับ"
      ),
      {
        type: "template",
        altText: "แม่บ้านประจำ",
        template: {
          type: "buttons",
          text: "แม่บ้านประจำ โดย Sangkan Clean",
          actions: [
            {
              type: "uri",
              label: "ดูหน้าแม่บ้าน",
              uri: SERVICE_URLS.maid,
            },
            {
              type: "message",
              label: "ขอคุยแอดมิน",
              text: "สนใจแม่บ้านประจำ ขอคุยแอดมิน",
            },
            {
              type: "postback",
              label: "เมนูหลัก",
              data: "action=choose_service&service=menu",
              displayText: "เมนูหลัก",
            },
          ],
        },
      },
    ]);
    await pushOwners(textMsg(`ลูกค้าสนใจแม่บ้านประจำ\n${userId}`));
    return;
  }

  // menu / unknown → chooser (hide Office rich menu)
  await hideOfficeMenu(userId);
  await reply(replyToken, welcomeMessages());
}

export async function handleCustomerEvent(event, userId) {
  const type = event.type;

  if (type === "postback") {
    const data = new URLSearchParams(event.postback?.data || "");
    const action = data.get("action");
    if (action === "choose_service") {
      await replyServiceChoice(event.replyToken, data.get("service"), userId);
      return;
    }
    if (action === "select_package") {
      const pkg = data.get("package");
      if (!PACKAGES[pkg]) {
        await reply(event.replyToken, textMsg("แพ็คเกจไม่ถูกต้อง"));
        return;
      }
      await reply(event.replyToken, [
        textMsg(
          `เลือก ${PACKAGES[pkg].name} (฿${PACKAGES[pkg].price.toLocaleString("th-TH")}/เดือน)\nกดปุ่มด้านล่างเพื่อกรอกข้อมูลจอง Early Bird`
        ),
        {
          type: "template",
          altText: "จอง Early Bird",
          template: {
            type: "buttons",
            text: `จองแพ็คเกจ ${pkg}`,
            actions: [
              {
                type: "uri",
                label: "เปิดฟอร์มจอง",
                uri: `${bookingLiffUrl()}?package=${pkg}`,
              },
            ],
          },
        },
      ]);
      return;
    }
    if (action === "help_reschedule") {
      await reply(
        event.replyToken,
        textMsg("พิมพ์วันเวลาที่ต้องการเลื่อนมาได้เลย แอดมินจะติดต่อกลับ")
      );
      return;
    }
    if (action === "help_complaint") {
      await reply(
        event.replyToken,
        textMsg("รบกวนอธิบายปัญหาสั้นๆ ได้เลย ทีมงานจะเร่งแก้ไข")
      );
      await pushOwners(
        textMsg(`ร้องเรียนจากลูกค้า ${userId}: รอข้อความถัดไป`)
      );
      return;
    }
  }

  if (type === "message" && event.message?.type === "text") {
    const text = event.message.text.trim();
    const cmd = text.toLowerCase();

    if (
      ["เมนูหลัก", "บริการ", "เลือกบริการ", "menu", "สวัสดี", "hello", "hi"].some(
        (k) => cmd.includes(k)
      )
    ) {
      await hideOfficeMenu(userId);
      await reply(event.replyToken, welcomeMessages());
      return;
    }
    if (
      ["big clean", "bigclean", "บิ๊กคลีน", "บิ๊กคลีนนิ่ง", "big cleaning"].some(
        (k) => cmd.includes(k)
      )
    ) {
      await replyServiceChoice(event.replyToken, "bigclean", userId);
      return;
    }
    if (
      ["แม่บ้านประจำ", "แม่บ้านรายเดือน", "จ้างแม่บ้าน"].some((k) =>
        cmd.includes(k)
      ) ||
      (cmd.includes("แม่บ้าน") && !cmd.includes("สมัครแม่บ้าน"))
    ) {
      await replyServiceChoice(event.replyToken, "maid", userId);
      return;
    }
    if (
      ["sangkan office", "ออฟฟิศ", "office", "early bird"].some((k) =>
        cmd.includes(k)
      )
    ) {
      await replyServiceChoice(event.replyToken, "office", userId);
      return;
    }
    if (["แพ็คเกจ", "package", "packages"].some((k) => cmd.includes(k))) {
      await reply(event.replyToken, [
        textMsg("แพ็คเกจด้านล่างเป็นของ Sangkan Office (ออฟฟิศรายเดือน)"),
        packagesFlex(),
      ]);
      return;
    }
    if (["จอง", "early", "book"].some((k) => cmd.includes(k))) {
      await reply(event.replyToken, [
        textMsg("จอง Early Bird — Sangkan Office"),
        packagesFlex(),
        textMsg("เลือกแพ็คเกจจากด้านบน แล้วกรอกฟอร์มจองได้เลย"),
      ]);
      return;
    }
    if (["คิว", "นัด", "schedule"].some((k) => cmd.includes(k))) {
      await sendNextJob(event.replyToken, userId);
      return;
    }
    if (["รายงาน", "รูป", "pow", "proof"].some((k) => cmd.includes(k))) {
      await sendLatestPow(event.replyToken, userId);
      return;
    }
    if (["ชวน", "affiliate", "เพื่อน"].some((k) => cmd.includes(k))) {
      await sendAffiliate(event.replyToken, userId);
      return;
    }
    if (["บิล", "ชำระ", "โอน", "เครดิต"].some((k) => cmd.includes(k))) {
      await sendBillStatus(event.replyToken, userId);
      return;
    }
    if (["ช่วย", "help", "เลื่อน", "ร้อง"].some((k) => cmd.includes(k))) {
      await reply(event.replyToken, helpTemplate());
      return;
    }
    if (cmd.includes("ขอคุยแอดมิน") || cmd.includes("คุยแอดมิน")) {
      await reply(
        event.replyToken,
        textMsg("รับทราบครับ แอดมินจะติดต่อกลับโดยเร็ว")
      );
      await pushOwners(textMsg(`ลูกค้าขอคุยแอดมิน\n${userId}\n${text}`));
      return;
    }

    // Unknown text while already a customer — short tip, don't reset to chooser
    const existing = await findCustomerByLineId(userId);
    if (existing && event.replyToken) {
      await reply(
        event.replyToken,
        textMsg(
          "พิมพ์ 「บิล」 「เครดิต」 「คิว」 「รายงาน」 「ชวน」 หรือ 「เมนูหลัก」ได้ครับ\nถ้าโอนแล้ว ส่งรูปสลิปในแชทนี้ได้เลย"
        )
      );
      return;
    }
  }

  // Slip image → attach to pending bill
  if (type === "message" && event.message?.type === "image") {
    const customer = await findCustomerByLineId(userId);
    if (!customer) {
      if (event.replyToken) {
        await reply(
          event.replyToken,
          textMsg("ยังไม่พบบิลค้าง — พิมพ์ 「จอง」 หรือรอแอดมินออกบิลก่อน")
        );
      }
      return;
    }
    try {
      const slipUrl = `line-message:${event.message.id}`;
      const result = await attachSlip({
        customerId: customer.id,
        slipUrl,
        lineUserId: userId,
      });
      if (event.replyToken) {
        await reply(
          event.replyToken,
          textMsg(
            `รับสลิปแล้ว ผูกกับบิล ${result.paymentId}\nแอดมินจะตรวจสอบและยืนยันให้ครับ`
          )
        );
      }
    } catch (err) {
      if (event.replyToken) {
        await reply(
          event.replyToken,
          textMsg(
            err.message.includes("No pending")
              ? "ยังไม่มีบิลค้างรอสลิป — พิมพ์ 「บิล」 เพื่อดูสถานะ หรือรอแอดมินออกบิล"
              : `บันทึกสลิปไม่สำเร็จ: ${err.message}`
          )
        );
      }
    }
    return;
  }

  if (type === "follow") {
    if (event.replyToken) {
      await hideOfficeMenu(userId);
      await reply(event.replyToken, welcomeMessages());
    }
    return;
  }

  if (type === "message" && event.replyToken) {
    await hideOfficeMenu(userId);
    await reply(event.replyToken, welcomeMessages());
  }
}

async function sendBillStatus(replyToken, userId) {
  const customer = await findCustomerByLineId(userId);
  if (!customer) {
    await reply(replyToken, textMsg("ยังไม่พบข้อมูลลูกค้า — พิมพ์ 「จอง」 เพื่อสมัคร"));
    return;
  }
  const credit = Number(customer.billing_credit_thb) || 0;
  const payments = await readTable("payments");
  const pending = payments
    .filter((p) => p.customer_id === customer.id && p.status === "pending")
    .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));

  const msgs = [
    textMsg(
      `เครดิต Affiliate คงเหลือ: ฿${credit.toLocaleString("th-TH")}\nมัดจำ: ${customer.deposit_status || "—"} (฿${customer.deposit_thb || 0})`
    ),
  ];

  if (pending.length) {
    const bill = pending[0];
    const pkg = String(customer.package || "").toUpperCase();
    const typeLabel =
      bill.type === "deposit"
        ? "มัดจำ Early Bird"
        : bill.type === "subscription"
          ? "ค่าบริการรายเดือน"
          : "เติมเงิน";
    msgs.push(
      billFlex({
        paymentId: bill.id,
        companyName: customer.company_name || customer.id,
        typeLabel,
        packageId: pkg,
        amount: Number(bill.amount_thb) || 0,
        creditApplied: Number(bill.credit_applied_thb) || 0,
        depositApplied: Number(bill.deposit_applied_thb) || 0,
        payable: Number(bill.payable_thb) || 0,
        bankInfo: getConfig().bankTransferInfo,
      })
    );
    msgs.push(
      textMsg(
        Number(bill.payable_thb) > 0
          ? "โอนตามยอดแล้วส่งรูปสลิปในแชทนี้ได้เลย"
          : "ยอด 0 — รอแอดมินยืนยันปิดบิล"
      )
    );
  } else {
    msgs.push(
      textMsg("ไม่มีบิลค้างตอนนี้ — เมื่อถึงรอบชำระ แอดมินจะส่งบิลมาให้")
    );
  }

  await reply(replyToken, msgs);
}
function helpTemplate() {
  return {
    type: "template",
    altText: "ช่วยเหลือ",
    template: {
      type: "buttons",
      text: "ต้องการความช่วยเหลือด้านไหน?",
      actions: [
        {
          type: "postback",
          label: "เลื่อนวัน",
          data: "action=help_reschedule",
          displayText: "ขอเลื่อนวัน",
        },
        {
          type: "postback",
          label: "ร้องเรียน",
          data: "action=help_complaint",
          displayText: "ต้องการร้องเรียน",
        },
        {
          type: "postback",
          label: "เมนูหลัก",
          data: "action=choose_service&service=menu",
          displayText: "เมนูหลัก",
        },
        { type: "message", label: "คุยแอดมิน", text: "ขอคุยแอดมิน" },
      ],
    },
  };
}

async function sendNextJob(replyToken, userId) {
  const customer = await findCustomerByLineId(userId);
  if (!customer) {
    await reply(replyToken, textMsg("ยังไม่พบข้อมูลลูกค้า — พิมพ์ 「จอง」 เพื่อสมัคร"));
    return;
  }
  const jobs = await readTable("jobs");
  const today = new Date().toISOString().slice(0, 10);
  const mine = jobs
    .filter(
      (j) =>
        j.customer_id === customer.id &&
        j.date >= today &&
        !["cancelled", "done"].includes(j.status)
    )
    .sort((a, b) => `${a.date}${a.time_slot}`.localeCompare(`${b.date}${b.time_slot}`));
  if (!mine.length) {
    await reply(
      replyToken,
      textMsg("ยังไม่มีคิวนัดถัดไป แอดมินจะแจ้งเมื่อจัดตารางแล้ว")
    );
    return;
  }
  const j = mine[0];
  const typeLabel =
    j.type === "combo_mini_deep"
      ? "Mini Deep + โอโซน"
      : j.type === "combo_full_big"
        ? "Full Big Clean"
        : "ทำความสะอาดทั่วไป";
  await reply(
    replyToken,
    textMsg(
      `คิวถัดไป\nวันที่ ${j.date} เวลา ${j.time_slot || "—"}\nประเภท: ${typeLabel}\nรหัสงาน: ${j.id}`
    )
  );
}

async function sendLatestPow(replyToken, userId) {
  const customer = await findCustomerByLineId(userId);
  if (!customer) {
    await reply(replyToken, textMsg("ยังไม่พบข้อมูลลูกค้า"));
    return;
  }
  const jobs = await readTable("jobs");
  const photos = await readTable("qc_photos");
  const myJobs = jobs
    .filter((j) => j.customer_id === customer.id)
    .sort((a, b) => String(b.date).localeCompare(String(a.date)));
  for (const j of myJobs) {
    const before = photos.find((p) => p.job_id === j.id && p.type === "before");
    const after = photos.find((p) => p.job_id === j.id && p.type === "after");
    if (before || after) {
      const msgs = [
        textMsg(`รายงาน PoW งาน ${j.id} (${j.date})`),
      ];
      if (before?.drive_url) {
        msgs.push({
          type: "image",
          originalContentUrl: before.drive_url,
          previewImageUrl: before.drive_url,
        });
      }
      if (after?.drive_url) {
        msgs.push({
          type: "image",
          originalContentUrl: after.drive_url,
          previewImageUrl: after.drive_url,
        });
      }
      if (!before?.drive_url && !after?.drive_url) {
        msgs.push(textMsg("มีรายการรูปแต่ยังไม่มี URL"));
      }
      await reply(replyToken, msgs);
      return;
    }
  }
  await reply(replyToken, textMsg("ยังไม่มีรายงานรูปก่อน–หลัง"));
}

async function sendAffiliate(replyToken, userId) {
  const customer = await findCustomerByLineId(userId);
  if (!customer) {
    await reply(replyToken, textMsg("สมัครเป็นลูกค้าก่อน แล้วจะได้รหัสชวนเพื่อน"));
    return;
  }
  const code = customer.affiliate_code || customer.id;
  const credit = Number(customer.billing_credit_thb || 0);
  const { affiliatePct, promoEndDate, promoPhase } = getConfig();
  const earning = isPromoActive()
    ? `ช่วงโปรเฟส ${promoPhase} (ถึง ${promoEndDate}): ได้เครดิต ${affiliatePct}% ของราคาแพ็คเต็มทุกงวดที่เพื่อนใช้บริการ`
    : `โปรเฟส ${promoPhase} หมดแล้ว — ตอนนี้ไม่สะสมเครดิตใหม่จากเพื่อน (รอเฟส 2)`;
  await reply(
    replyToken,
    textMsg(
      `รหัส Affiliate ของคุณ: ${code}\nชวนเพื่อนใช้รหัสนี้ตอนจอง\n${earning}\nเครดิตคงเหลือ: ฿${credit.toLocaleString("th-TH")} (ใช้หักบิลได้ ไม่หมดอายุ)\n${promoStatusLine()}`
    )
  );
}

/** LIFF / API: create booking */
export async function createBooking(payload) {
  const {
    lineUserId,
    companyName,
    contactName,
    package: pkg,
    address,
    lat,
    lng,
    depositThb = 500,
    referredByCode = "",
  } = payload;

  if (!PACKAGES[pkg]) throw new Error("Invalid package");
  if (!lineUserId || !companyName) throw new Error("Missing fields");

  if (!isPromoActive()) {
    throw new Error(
      `โปร Early Bird เฟส 1 หมดอายุแล้ว (${getConfig().promoEndDate}) — เครดิตเดิมยังใช้ได้ · เฟส 2 จะเปิดให้จองใหม่ภายหลัง`
    );
  }

  const existing = await findCustomerByLineId(lineUserId);
  const id = existing?.id || newId("CUS");
  const affiliateCode =
    existing?.affiliate_code || `SO${pkg}${id.replace(/\W/g, "").slice(-6)}`;

  const row = {
    id,
    company_name: companyName,
    contact_name: contactName || "",
    line_user_id: lineUserId,
    package: pkg,
    address: address || "",
    lat: lat ?? "",
    lng: lng ?? "",
    affiliate_code: affiliateCode,
    referred_by_code: referredByCode || "",
    deposit_thb: depositThb,
    deposit_status: "pending",
    status: "booked",
    billing_credit_thb: existing?.billing_credit_thb || 0,
    created_at: new Date().toISOString(),
    notes: `Early Bird phase ${getConfig().promoPhase}`,
  };

  if (existing) {
    await updateRow("customers", (r) => r.line_user_id === lineUserId, row);
  } else {
    await appendRow("customers", row);
  }

  const p = PACKAGES[pkg];
  await push(lineUserId, [
    textMsg(
      `รับจอง Early Bird แล้ว\nบริษัท: ${companyName}\nแพ็คเกจ: ${p.name} ฿${p.price.toLocaleString("th-TH")}/เดือน\nมัดจำ: ฿${depositThb} (สถานะ: รอชำระ)\nรหัสชวนเพื่อนของคุณ: ${affiliateCode}\n${promoStatusLine()}`
    ),
  ]);
  await pushOwners(
    textMsg(
      `จองใหม่: ${companyName} · ${pkg} · มัดจำ ฿${depositThb} · ${lineUserId}`
    )
  );

  return { id, affiliateCode, package: pkg };
}

/** Apply affiliate credit when referred customer pays (phase 1 promo window only; balance never expires). */
export async function applyAffiliateOnPayment({
  referredCustomerId,
  paymentThb,
  paymentDate,
}) {
  const { affiliatePct } = getConfig();
  const onDate = (paymentDate || todayBangkok()).slice(0, 10);

  if (!isPromoActive(onDate)) {
    console.info(
      "affiliate skipped: promo ended",
      onDate,
      getConfig().promoEndDate
    );
    return { skipped: true, reason: "promo_ended" };
  }

  const customers = await readTable("customers");
  const referred = customers.find((c) => c.id === referredCustomerId);
  if (!referred?.referred_by_code) return null;

  const referrer = customers.find(
    (c) => c.affiliate_code === referred.referred_by_code
  );
  if (!referrer) return null;

  const credit = Math.round((Number(paymentThb) * affiliatePct) / 100);
  if (credit <= 0) return null;

  const prev = Number(referrer.billing_credit_thb || 0);
  await updateRow(
    "customers",
    (r) => r.id === referrer.id,
    { billing_credit_thb: prev + credit }
  );
  await appendRow("affiliate", {
    id: newId("AFF"),
    code: referrer.affiliate_code,
    referrer_customer_id: referrer.id,
    referred_customer_id: referred.id,
    payment_thb: paymentThb,
    credit_thb: credit,
    payment_date: onDate,
    applied_to_bill: "N",
    created_at: new Date().toISOString(),
  });

  if (referrer.line_user_id) {
    await push(
      referrer.line_user_id,
      textMsg(
        `ได้รับเครดิต Affiliate ฿${credit.toLocaleString("th-TH")} จากราคาแพ็คเต็มของเพื่อน (${affiliatePct}%)\nเครดิตสะสม: ฿${(prev + credit).toLocaleString("th-TH")} (ไม่หมดอายุ)`
      )
    );
  }
  return { referrerId: referrer.id, credit };
}

export async function handleCustomerPostbackAlias(action, event, userId) {
  const map = {
    packages: () =>
      reply(event.replyToken, [
        textMsg("แพ็คเกจ Sangkan Office (ออฟฟิศรายเดือน)"),
        packagesFlex(),
      ]),
    book: () =>
      reply(event.replyToken, [
        packagesFlex(),
        textMsg("เลือกแพ็คเกจแล้วเปิดฟอร์มจอง"),
      ]),
    next_job: () => sendNextJob(event.replyToken, userId),
    pow: () => sendLatestPow(event.replyToken, userId),
    affiliate: () => sendAffiliate(event.replyToken, userId),
    bill: () => sendBillStatus(event.replyToken, userId),
    help: () => reply(event.replyToken, helpTemplate()),
  };
  if (map[action]) await map[action]();
}
