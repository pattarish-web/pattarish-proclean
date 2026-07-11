/**
 * Early Warning: jobs whose start time + 15 minutes passed without check-in.
 * Run via: npm run early-warning
 * Or GitHub Actions cron.
 */
import { readTable, updateRow } from "../lib/sheets.js";
import { pushOwners, textMsg } from "../lib/line.js";

function bangkokParts(date = new Date()) {
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Bangkok",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const parts = Object.fromEntries(
    fmt.formatToParts(date).map((p) => [p.type, p.value])
  );
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    hour: Number(parts.hour),
    minute: Number(parts.minute),
  };
}

function minutesNow(parts) {
  return parts.hour * 60 + parts.minute;
}

function parseSlotMinutes(timeSlot) {
  if (!timeSlot || !String(timeSlot).includes(":")) return null;
  const [h, m] = String(timeSlot).split(":").map(Number);
  if (Number.isNaN(h)) return null;
  return h * 60 + (m || 0);
}

export async function runEarlyWarning() {
  const now = bangkokParts();
  const nowMin = minutesNow(now);
  const jobs = await readTable("jobs");
  const customers = await readTable("customers");
  const byId = Object.fromEntries(customers.map((c) => [c.id, c]));

  const due = jobs.filter((j) => {
    if (j.date !== now.date) return false;
    if (["checked_in", "done", "cancelled"].includes(j.status)) return false;
    if (j.warned_at) return false;
    const start = parseSlotMinutes(j.time_slot);
    if (start === null) return false;
    return nowMin >= start + 15;
  });

  if (!due.length) {
    console.log("Early Warning: no jobs due");
    return { warned: 0 };
  }

  for (const j of due) {
    const c = byId[j.customer_id];
    const name = c?.company_name || j.customer_id;
    await pushOwners(
      textMsg(
        `Early Warning\nยังไม่เช็คอินเกิน 15 นาทีหลังเวลานัด\nงาน: ${j.id}\nลูกค้า: ${name}\nนัด: ${j.date} ${j.time_slot}\nประเภท: ${j.type}`
      )
    );
    await updateRow(
      "jobs",
      (row) => row.id === j.id,
      { warned_at: new Date().toISOString() }
    );
  }

  console.log(`Early Warning: sent ${due.length}`);
  return { warned: due.length };
}

const isMain =
  process.argv[1] &&
  (process.argv[1].endsWith("earlyWarning.js") ||
    process.argv[1].includes("earlyWarning"));

if (isMain) {
  runEarlyWarning().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
