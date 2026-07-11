/**
 * Generate monthly jobs for a customer from package rules.
 * Combo is EXTRA (not replacing routine).
 *
 * Usage:
 *   node src/jobs/generateJobs.js --customer CUS-xxx --year 2026 --month 8
 */
import { PACKAGES, JOB_TYPES } from "../config/packages.js";
import { appendRow, newId, readTable } from "../lib/sheets.js";

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--customer") out.customerId = argv[++i];
    if (argv[i] === "--year") out.year = Number(argv[++i]);
    if (argv[i] === "--month") out.month = Number(argv[++i]);
    if (argv[i] === "--staff") out.staffId = argv[++i];
    if (argv[i] === "--dry-run") out.dryRun = true;
  }
  return out;
}

function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

/** Pick N weekdays (Mon-Fri) spread across month */
function pickRoutineDates(year, month, count) {
  const dim = daysInMonth(year, month);
  const weekdays = [];
  for (let d = 1; d <= dim; d++) {
    const dt = new Date(year, month - 1, d);
    const dow = dt.getDay();
    if (dow >= 1 && dow <= 5) weekdays.push(d);
  }
  if (count >= weekdays.length) return weekdays;
  const step = weekdays.length / count;
  const picked = [];
  for (let i = 0; i < count; i++) {
    picked.push(weekdays[Math.min(weekdays.length - 1, Math.floor(i * step))]);
  }
  return [...new Set(picked)].slice(0, count);
}

function isoDate(year, month, day) {
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

export async function generateJobsForCustomer({
  customerId,
  year,
  month,
  staffId = "",
  dryRun = false,
}) {
  const customers = await readTable("customers");
  const customer = customers.find((c) => c.id === customerId);
  if (!customer) throw new Error("Customer not found");
  const pkg = PACKAGES[String(customer.package).toUpperCase()];
  if (!pkg) throw new Error("Unknown package");

  const routineDays = pickRoutineDates(year, month, pkg.routinePerMonth);
  const jobs = routineDays.map((day, i) => ({
    id: newId("JOB"),
    customer_id: customerId,
    staff_id: staffId,
    date: isoDate(year, month, day),
    time_slot: "09:00",
    type: JOB_TYPES.ROUTINE,
    status: "scheduled",
    checkin_at: "",
    checkout_at: "",
    warned_at: "",
    notes: `routine ${i + 1}/${pkg.routinePerMonth}`,
  }));

  if (pkg.combo === "combo_mini_deep") {
    const last = daysInMonth(year, month);
    let comboDay = last;
    while (new Date(year, month - 1, comboDay).getDay() === 0) comboDay -= 1;
    jobs.push({
      id: newId("JOB"),
      customer_id: customerId,
      staff_id: staffId,
      date: isoDate(year, month, comboDay),
      time_slot: "13:00",
      type: JOB_TYPES.COMBO_MINI,
      status: "scheduled",
      checkin_at: "",
      checkout_at: "",
      warned_at: "",
      notes: "combo_mini_deep extra",
    });
  }

  if (pkg.combo === "combo_full_big" && month % 2 === 0) {
    const mid = Math.min(15, daysInMonth(year, month));
    jobs.push({
      id: newId("JOB"),
      customer_id: customerId,
      staff_id: staffId,
      date: isoDate(year, month, mid),
      time_slot: "10:00",
      type: JOB_TYPES.COMBO_FULL,
      status: "scheduled",
      checkin_at: "",
      checkout_at: "",
      warned_at: "",
      notes: "combo_full_big extra every 2 months",
    });
  }

  if (dryRun) {
    console.log(JSON.stringify(jobs, null, 2));
    return jobs;
  }
  for (const j of jobs) await appendRow("jobs", j);
  console.log(`Created ${jobs.length} jobs for ${customerId}`);
  return jobs;
}

const args = parseArgs(process.argv);
if (args.customerId && args.year && args.month) {
  generateJobsForCustomer(args).catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
