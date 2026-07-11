import { getConfig } from "../../config/env.js";
import { distanceMeters } from "../../lib/geo.js";
import { downloadLineImage, uploadPowImage } from "../../lib/drive.js";
import { jobListFlex } from "../../lib/flex.js";
import { reply, push, pushOwners, textMsg } from "../../lib/line.js";
import {
  appendRow,
  findStaffByLineId,
  newId,
  readTable,
  updateRow,
} from "../../lib/sheets.js";

function todayBangkok() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Bangkok",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

function pendingJobsForStaff(jobs, staffId) {
  const date = todayBangkok();
  return jobs.filter(
    (j) =>
      j.staff_id === staffId &&
      j.date === date &&
      !["done", "cancelled"].includes(String(j.status).toLowerCase())
  );
}

export async function listTodayJobsForStaffLineId(lineUserId) {
  const staff = await findStaffByLineId(lineUserId);
  if (!staff) throw new Error("ยังไม่ได้ลงทะเบียนแม่บ้าน");
  const jobs = pendingJobsForStaff(await readTable("jobs"), staff.id);
  const customers = await readTable("customers");
  const byId = Object.fromEntries(customers.map((c) => [c.id, c]));
  return jobs.map((j) => ({
    id: j.id,
    time_slot: j.time_slot || "",
    status: j.status || "",
    label: byId[j.customer_id]?.company_name || j.customer_id || j.id,
  }));
}

async function resolveJobId(staff, jobId) {
  const jobs = await readTable("jobs");
  if (jobId) {
    const job = jobs.find((j) => j.id === jobId);
    if (!job) throw new Error("ไม่พบงานนี้");
    return job;
  }
  const pending = pendingJobsForStaff(jobs, staff.id);
  if (!pending.length) throw new Error("วันนี้ยังไม่มีงาน");
  if (pending.length > 1) {
    throw new Error("วันนี้มีหลายงาน กรุณาเลือกจากหน้างานวันนี้ก่อน");
  }
  return pending[0];
}

export async function handleStaffEvent(event, userId) {
  const staff = await findStaffByLineId(userId);
  if (!staff) {
    if (event.replyToken) {
      await reply(
        event.replyToken,
        textMsg("บัญชีนี้ยังไม่ได้เป็นแม่บ้าน ติดต่อเจ้าของกิจการนะคะ")
      );
    }
    return;
  }

  if (event.type === "postback") {
    const data = new URLSearchParams(event.postback?.data || "");
    const action = data.get("action");
    if (action === "staff_today") {
      await sendTodayQueue(event.replyToken, staff);
      return;
    }
    if (action === "staff_issue") {
      const kind = data.get("kind") || "other";
      await pushOwners(
        textMsg(
          `แม่บ้านแจ้งปัญหา: ${staff.name}\nประเภท: ${kindLabel(kind)}\n${userId}`
        )
      );
      await reply(
        event.replyToken,
        textMsg("แจ้งเจ้าของแล้วค่ะ จะโทรกลับให้นะคะ")
      );
      return;
    }
    if (action === "staff_photo_tag") {
      await tagLastPhoto(event, staff, data.get("tag"));
      return;
    }
    if (action === "staff_guide") {
      await reply(event.replyToken, guideMessage());
      return;
    }
  }

  if (event.type === "message" && event.message?.type === "image") {
    await handleStaffImage(event, staff, userId);
    return;
  }

  if (event.type === "message" && event.message?.type === "text") {
    const raw = event.message.text.trim();
    const t = raw.toLowerCase();
    if (
      t.includes("งานวันนี้") ||
      t.includes("คิว") ||
      t === "งาน" ||
      t.includes("วันนี้")
    ) {
      await sendTodayQueue(event.replyToken, staff);
      return;
    }
    if (
      t.includes("ถึงที่") ||
      t.includes("เช็คอิน") ||
      t.includes("ถึงแล้ว") ||
      t.includes("มาถึง")
    ) {
      await reply(event.replyToken, checkinUriMessage());
      return;
    }
    if (
      t.includes("ส่งรูป") ||
      t.includes("รูปงาน") ||
      t.includes("ถ่ายรูป")
    ) {
      await reply(event.replyToken, powHelpMessage());
      return;
    }
    if (t.includes("ส่งงานเสร็จ") || t === "เสร็จแล้ว" || t === "เสร็จ") {
      await completeTodayJob(event.replyToken, staff);
      return;
    }
    if (t.includes("ปัญหา") || t.includes("เข้าไม่ได้") || t.includes("ช่วย")) {
      await reply(event.replyToken, issueTemplate());
      return;
    }
    if (t.includes("คู่มือ")) {
      await reply(event.replyToken, guideMessage());
      return;
    }
  }

  if (event.replyToken) {
    await reply(event.replyToken, [
      textMsg(
        `สวัสดีคุณ${staff.name} ค่ะ\n\nใช้เมนูด้านล่างได้เลย\n① งานวันนี้  ② ถึงที่แล้ว\n③ ส่งรูปงาน  ④ มีปัญหา`
      ),
    ]);
  }
}

function kindLabel(kind) {
  return (
    {
      no_access: "เข้าไม่ได้",
      reschedule: "ลูกค้าเลื่อน",
      other: "อื่นๆ",
    }[kind] || kind
  );
}

async function handleStaffImage(event, staff, userId) {
  const messageId = event.message.id;
  const jobs = pendingJobsForStaff(await readTable("jobs"), staff.id);
  const job = jobs[0] || null;
  const jobId = job?.id || "";
  const date = job?.date || todayBangkok();
  const customers = await readTable("customers");
  const customer = job
    ? customers.find((c) => c.id === job.customer_id)
    : null;
  const customerName =
    customer?.company_name ||
    customer?.contact_name ||
    job?.customer_id ||
    "ไม่ระบุลูกค้า";
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  let driveUrl = `line-msg:${messageId}`;
  let uploadNote = "";

  try {
    const { buffer, mimeType } = await downloadLineImage(messageId);
    const ext = mimeType.includes("png") ? "png" : "jpg";
    const uploaded = await uploadPowImage({
      buffer,
      mimeType,
      filename: `${stamp}.${ext}`,
      date,
      staffName: staff.name || staff.id || "แม่บ้าน",
      customerName,
    });
    driveUrl = uploaded.viewUrl;
    uploadNote = `\nโฟลเดอร์: ${uploaded.pathHint}\nDrive: ${uploaded.openUrl}`;
  } catch (err) {
    console.warn("pow drive upload:", err.message);
    uploadNote = `\n(ยังอัป Drive ไม่ได้: ${err.message})`;
  }

  const photoId = newId("QC");
  await appendRow("qc_photos", {
    id: photoId,
    job_id: jobId,
    type: "pending",
    drive_url: driveUrl,
    timestamp: new Date().toISOString(),
  });

  await reply(event.replyToken, {
    type: "template",
    altText: "รูปนี้เป็นรูปอะไร",
    template: {
      type: "buttons",
      text: "บันทึกรูปแล้ว — รูปนี้เป็นอะไรคะ? (ส่งได้หลายรูป)",
      actions: [
        {
          type: "postback",
          label: "รูปก่อนทำ",
          data: `action=staff_photo_tag&tag=before&pid=${photoId}&job=${jobId}`,
          displayText: "รูปก่อนทำความสะอาด",
        },
        {
          type: "postback",
          label: "รูปหลังทำ",
          data: `action=staff_photo_tag&tag=after&pid=${photoId}&job=${jobId}`,
          displayText: "รูปหลังทำความสะอาด",
        },
        {
          type: "postback",
          label: "รูปเพิ่มเติม",
          data: `action=staff_photo_tag&tag=extra&pid=${photoId}&job=${jobId}`,
          displayText: "รูปเพิ่มเติม",
        },
      ],
    },
  });
  await pushOwners(
    textMsg(
      `แม่บ้าน ${staff.name} ส่งรูป (รอแท็ก)${uploadNote}\nงาน: ${jobId || "—"}\n${userId}`
    )
  );
}

async function tagLastPhoto(event, staff, tag) {
  const data = new URLSearchParams(event.postback?.data || "");
  const photoId = data.get("pid") || "";
  const jobId = data.get("job") || "";
  const type =
    tag === "after" ? "after" : tag === "extra" ? "extra" : "before";
  const patch = { type };
  if (jobId) patch.job_id = jobId;
  const ok = await updateRow("qc_photos", (r) => r.id === photoId, patch);
  const label =
    type === "before" ? "ก่อนทำ" : type === "after" ? "หลังทำ" : "เพิ่มเติม";
  await reply(
    event.replyToken,
    textMsg(
      ok
        ? `บันทึกเป็นรูป${label}แล้วค่ะ ส่งรูปต่อได้เรื่อยๆ หรือพิมพ์ 「ส่งงานเสร็จ」`
        : "อัปเดตรูปไม่สำเร็จ ลองส่งรูปใหม่อีกครั้งนะคะ"
    )
  );
  await pushOwners(
    textMsg(
      `แม่บ้าน ${staff.name} แท็กรูปเป็น「${label}」\nงาน: ${jobId || "—"} · ${photoId}`
    )
  );
}

async function completeTodayJob(replyToken, staff) {
  try {
    const job = await resolveJobId(staff, "");
    await updateRow(
      "jobs",
      (j) => j.id === job.id,
      { status: "done", checkout_at: new Date().toISOString() }
    );
    const photos = (await readTable("qc_photos")).filter(
      (p) => p.job_id === job.id && /^https?:\/\//i.test(p.drive_url || "")
    );
    const before = photos.filter((p) => p.type === "before");
    const after = photos.filter((p) => p.type === "after");
    const extra = photos.filter((p) => p.type === "extra");

    const customers = await readTable("customers");
    const customer = customers.find((c) => c.id === job.customer_id);
    if (customer?.line_user_id) {
      const msgs = [
        textMsg(
          `แม่บ้านทำความสะอาดเรียบร้อยแล้วค่ะ (${job.date || todayBangkok()})\nรูปก่อน ${before.length} / หลัง ${after.length} / เพิ่มเติม ${extra.length}`
        ),
      ];
      // LINE allows limited images per reply/push — send up to 4
      for (const p of [...before, ...after, ...extra].slice(0, 4)) {
        msgs.push({
          type: "image",
          originalContentUrl: p.drive_url,
          previewImageUrl: p.drive_url,
        });
      }
      if (photos.length > 4) {
        const links = photos
          .slice(4)
          .map((p, i) => `${i + 5}. ${p.drive_url}`)
          .join("\n");
        msgs.push(textMsg(`รูปเพิ่มเติม:\n${links}`));
      }
      await push(customer.line_user_id, msgs);
    }

    const linkLines = photos
      .map((p, i) => `${i + 1}. [${p.type}] ${p.drive_url}`)
      .join("\n");
    await pushOwners(
      textMsg(
        `แม่บ้าน ${staff.name} ส่งงานเสร็จ\nงาน ${job.id}\nรูปทั้งหมด ${photos.length} ใบ\n${linkLines || "(ยังไม่มีลิงก์ Drive)"}`
      )
    );
    await reply(
      replyToken,
      textMsg(
        `บันทึกส่งงานเสร็จแล้ว ขอบคุณค่ะ\nส่งรูปไว้ ${photos.length} ใบใน Google Drive`
      )
    );
  } catch (err) {
    await reply(replyToken, textMsg(err.message));
  }
}

async function sendTodayQueue(replyToken, staff) {
  const date = todayBangkok();
  const jobs = (await readTable("jobs")).filter(
    (j) => j.staff_id === staff.id && j.date === date
  );
  const customers = await readTable("customers");
  const byId = Object.fromEntries(customers.map((c) => [c.id, c]));
  if (!jobs.length) {
    await reply(replyToken, textMsg("วันนี้ยังไม่มีงานที่ได้รับมอบหมายค่ะ"));
    return;
  }
  const lines = jobs.map((j) => {
    const name = byId[j.customer_id]?.company_name || j.customer_id;
    return `• ${j.time_slot || "—"} ${name}\n  สถานะ: ${thaiStatus(j.status)}`;
  });
  await reply(replyToken, [
    textMsg(`งานวันนี้ (${date})\n\n${lines.join("\n\n")}`),
    jobListFlex(`งานวันนี้ ${date}`, jobs, byId),
  ]);
}

function thaiStatus(status) {
  const s = String(status || "").toLowerCase();
  if (s === "checked_in") return "ถึงที่แล้ว";
  if (s === "done") return "เสร็จแล้ว";
  if (s === "cancelled") return "ยกเลิก";
  return "รอทำ";
}

function guideMessage() {
  return textMsg(
    `วิธีทำงานสั้นๆ
1) กด「งานวันนี้」ดูว่าไปที่ไหน
2) ถึงที่แล้วกด「ถึงที่แล้ว」
3) ถ่ายรูปก่อน–หลัง ส่งในแชท
4) พิมพ์「ส่งงานเสร็จ」
ถ้าเข้าไม่ได้ กด「มีปัญหา」`
  );
}

function issueTemplate() {
  return {
    type: "template",
    altText: "มีปัญหา",
    template: {
      type: "buttons",
      text: "เกิดอะไรขึ้นคะ?",
      actions: [
        {
          type: "postback",
          label: "เข้าไม่ได้",
          data: "action=staff_issue&kind=no_access",
          displayText: "เข้าออฟฟิศไม่ได้",
        },
        {
          type: "postback",
          label: "ลูกค้าเลื่อน",
          data: "action=staff_issue&kind=reschedule",
          displayText: "ลูกค้าขอเลื่อน",
        },
        {
          type: "postback",
          label: "อื่นๆ",
          data: "action=staff_issue&kind=other",
          displayText: "ปัญหาอื่นๆ",
        },
      ],
    },
  };
}

function checkinUriMessage() {
  const { liff, publicBaseUrl } = getConfig();
  const uri = liff.checkinId
    ? `https://liff.line.me/${liff.checkinId}`
    : `${publicBaseUrl}/liff/checkin`;
  return {
    type: "template",
    altText: "ถึงที่แล้ว",
    template: {
      type: "buttons",
      text: "กดปุ่มเพื่อยืนยันว่าถึงที่ทำงานแล้ว (เปิดตำแหน่งด้วยนะคะ)",
      actions: [{ type: "uri", label: "ถึงที่แล้ว", uri }],
    },
  };
}

function powHelpMessage() {
  const { liff, publicBaseUrl } = getConfig();
  const uri = liff.powId
    ? `https://liff.line.me/${liff.powId}`
    : `${publicBaseUrl}/liff/pow`;
  return {
    type: "template",
    altText: "ส่งรูปงาน",
    template: {
      type: "buttons",
      text: "ส่งรูปได้หลายใบในแชทนี้ ระบบเก็บเข้า Google Drive ให้ จากนั้นพิมพ์ ส่งงานเสร็จ",
      actions: [
        { type: "uri", label: "ดูวิธีส่งรูป", uri },
        {
          type: "message",
          label: "ส่งงานเสร็จ",
          text: "ส่งงานเสร็จ",
        },
      ],
    },
  };
}

function powUriMessage() {
  return powHelpMessage();
}

export async function staffCheckin({ jobId, staffLineUserId, lat, lng }) {
  const staff = await findStaffByLineId(staffLineUserId);
  if (!staff) throw new Error("ยังไม่ได้ลงทะเบียนแม่บ้าน");

  const job = await resolveJobId(staff, jobId);

  const customers = await readTable("customers");
  const customer = customers.find((c) => c.id === job.customer_id);
  if (!customer?.lat || !customer?.lng) {
    throw new Error("ยังไม่มีพิกัดลูกค้าในระบบ ติดต่อแอดมิน");
  }

  const dist = distanceMeters(
    Number(lat),
    Number(lng),
    Number(customer.lat),
    Number(customer.lng)
  );
  const radius = getConfig().gpsRadiusM;
  const valid = dist <= radius ? "Y" : "N";

  await appendRow("checkins", {
    id: newId("CHK"),
    job_id: job.id,
    staff_id: staff.id,
    lat,
    lng,
    distance_m: Math.round(dist),
    valid,
    timestamp: new Date().toISOString(),
  });

  if (valid === "Y") {
    await updateRow(
      "jobs",
      (j) => j.id === job.id,
      {
        status: "checked_in",
        checkin_at: new Date().toISOString(),
        staff_id: staff.id,
      }
    );
  }

  return { valid, distance_m: Math.round(dist), radius_m: radius, job_id: job.id };
}

export async function staffUploadPow({
  jobId,
  staffLineUserId,
  beforeUrl,
  afterUrl,
  complete = false,
}) {
  const staff = await findStaffByLineId(staffLineUserId);
  if (!staff) throw new Error("ยังไม่ได้ลงทะเบียนแม่บ้าน");

  const job = await resolveJobId(staff, jobId);

  if (beforeUrl) {
    await appendRow("qc_photos", {
      id: newId("QC"),
      job_id: job.id,
      type: "before",
      drive_url: beforeUrl,
      timestamp: new Date().toISOString(),
    });
  }
  if (afterUrl) {
    await appendRow("qc_photos", {
      id: newId("QC"),
      job_id: job.id,
      type: "after",
      drive_url: afterUrl,
      timestamp: new Date().toISOString(),
    });
  }

  if (complete) {
    await updateRow(
      "jobs",
      (j) => j.id === job.id,
      { status: "done", checkout_at: new Date().toISOString() }
    );
    const customers = await readTable("customers");
    const customer = customers.find((c) => c.id === job.customer_id);
    if (customer?.line_user_id) {
      const msgs = [
        textMsg(`แม่บ้านทำความสะอาดเรียบร้อยแล้วค่ะ (${job.date || todayBangkok()})`),
      ];
      const isHttp = (u) => /^https?:\/\//i.test(u || "");
      if (isHttp(beforeUrl)) {
        msgs.push({
          type: "image",
          originalContentUrl: beforeUrl,
          previewImageUrl: beforeUrl,
        });
      }
      if (isHttp(afterUrl)) {
        msgs.push({
          type: "image",
          originalContentUrl: afterUrl,
          previewImageUrl: afterUrl,
        });
      }
      await push(customer.line_user_id, msgs);
    }
    await pushOwners(textMsg(`งานเสร็จ: ${job.id} โดย ${staff.name}`));
  }

  return { ok: true, job_id: job.id };
}

export async function handleStaffAlias(action, event, userId) {
  const staff = await findStaffByLineId(userId);
  if (!staff) return;
  if (action === "today") await sendTodayQueue(event.replyToken, staff);
  if (action === "guide") await reply(event.replyToken, guideMessage());
  if (action === "issue") await reply(event.replyToken, issueTemplate());
  if (action === "checkin") await reply(event.replyToken, checkinUriMessage());
  if (action === "pow") await reply(event.replyToken, powHelpMessage());
}
