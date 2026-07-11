/**
 * Promo phases for Sangkan Office.
 * Phase 1 (Early Bird + Affiliate 10%): ends PROMO_END_DATE (default 2026-12-31 BKK).
 * Credits already earned never expire — only new promo grants stop after the end date.
 * Phase 2: raise PROMO_PHASE + set a new PROMO_END_DATE when ready.
 */
import { getConfig } from "./env.js";

/** Today as YYYY-MM-DD in Asia/Bangkok */
export function todayBangkok() {
  return new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Bangkok" });
}

export function getPromoConfig() {
  const cfg = getConfig();
  return {
    phase: cfg.promoPhase,
    endDate: cfg.promoEndDate, // YYYY-MM-DD inclusive
    affiliatePct: cfg.affiliatePct,
  };
}

/** Inclusive end-of-day Bangkok: active while today <= endDate */
export function isPromoActive(onDate = todayBangkok()) {
  const { endDate } = getPromoConfig();
  if (!endDate) return true; // blank = open-ended
  return String(onDate).slice(0, 10) <= String(endDate).slice(0, 10);
}

export function promoStatusLine() {
  const { phase, endDate } = getPromoConfig();
  if (!isPromoActive()) {
    return `โปรเฟส ${phase} หมดอายุแล้ว${endDate ? ` (ถึง ${endDate})` : ""} — เครดิตที่มีอยู่ยังใช้ได้ตลอด · เฟสถัดไปจะแจ้งภายหลัง`;
  }
  return `โปรเฟส ${phase} ถึง ${endDate || "ยังไม่กำหนด"} · เครดิตที่ได้แล้วไม่หมดอายุ`;
}
