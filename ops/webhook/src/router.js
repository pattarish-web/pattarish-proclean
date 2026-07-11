import { detectRole, menuRole } from "./lib/roles.js";
import { linkRichMenu, unlinkRichMenu, reply, textMsg } from "./lib/line.js";
import { handleStaffOnboardCommands } from "./lib/staffOnboard.js";
import { handleCustomerEvent, handleCustomerPostbackAlias } from "./modules/customer/index.js";
import { handleStaffEvent, handleStaffAlias } from "./modules/staff/index.js";
import { handleAdminEvent, handleAdminAlias } from "./modules/admin/index.js";

/**
 * Route a single LINE event after signature verification.
 */
export async function routeEvent(event) {
  const userId = event.source?.userId;
  if (!userId) return;

  const role = await detectRole(userId);
  const menu = menuRole(role);

  if (event.type === "follow") {
    try {
      // Guest: no Office rich menu until they choose Sangkan Office
      if (role === "guest") {
        await unlinkRichMenu(userId);
      } else {
        await linkRichMenu(userId, menu);
      }
    } catch (err) {
      console.warn("richMenu follow:", err.message);
    }
  }

  // Global: รหัสของฉัน / สมัครแม่บ้าน <code>
  if (await handleStaffOnboardCommands(event, userId)) return;

  // Unified rich-menu postbacks: action=menu&role=customer&item=packages
  if (event.type === "postback") {
    const data = new URLSearchParams(event.postback?.data || "");
    if (data.get("action") === "menu") {
      const item = data.get("item");
      const r = data.get("role") || menu;
      await dispatchMenu(r, item, event, userId);
      return;
    }
  }

  if (role === "admin") {
    await handleAdminEvent(event, userId);
    return;
  }
  if (role === "staff") {
    await handleStaffEvent(event, userId);
    return;
  }
  await handleCustomerEvent(event, userId);
}

async function dispatchMenu(role, item, event, userId) {
  try {
    if (role === "admin") {
      await handleAdminAlias(item, event, userId);
      return;
    }
    if (role === "staff") {
      await handleStaffAlias(item, event, userId);
      return;
    }
    await handleCustomerPostbackAlias(item, event, userId);
  } catch (err) {
    console.error("menu dispatch", err);
    if (event.replyToken) {
      await reply(event.replyToken, textMsg("เกิดข้อผิดพลาด ลองใหม่อีกครั้ง"));
    }
  }
}
