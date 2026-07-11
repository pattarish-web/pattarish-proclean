import { getConfig } from "../config/env.js";
import { findCustomerByLineId, findStaffByLineId } from "./sheets.js";

/**
 * @returns {Promise<"admin"|"staff"|"customer"|"guest">}
 */
export async function detectRole(lineUserId) {
  const { line } = getConfig();
  if (line.ownerUserIds.includes(lineUserId)) return "admin";

  try {
    const staff = await findStaffByLineId(lineUserId);
    if (staff) return "staff";
    const customer = await findCustomerByLineId(lineUserId);
    if (customer) return "customer";
  } catch (err) {
    console.warn("role detect sheets error:", err.message);
  }
  return "guest";
}

/** guest uses customer menu so they can book */
export function menuRole(role) {
  if (role === "guest") return "customer";
  return role;
}
