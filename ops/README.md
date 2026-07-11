# Sangkan Office Ops (LINE)

ระบบปฏิบัติการ LINE OA แยก 3 โมดูล — ลูกค้า / แม่บ้าน / การจัดการ  
ขับด้วย GitHub Actions + Node webhook (ไม่ใช้ Make.com)

## โครงสร้าง

```
ops/
├── shared/           # schema Sheets, roles, packages
├── modules/
│   ├── customer/     # Rich Menu + LIFF จอง
│   ├── staff/        # Rich Menu + LIFF check-in / PoW
│   └── admin/        # Rich Menu แดชบอร์ด
└── webhook/          # Node server (ESM, Node 18+)
```

## Quick start

1. สร้าง Google Sheet 7 แท็บ (รวม `payments`) — วาง header จาก `shared/sheets/headers/*.csv`
2. ตั้งค่า `webhook/.env` จาก `webhook/.env.example` (LINE + Sheets อย่างน้อย)
3. `cd ops/webhook && npm install && npm start` → ตรวจ `http://localhost:3000/health`
4. Deploy Docker จากโฟลเดอร์ `ops/` (ดู `webhook/README.md` / `render.yaml`)
5. ชี้ LINE Webhook → `https://<host>/webhook`
6. สร้าง LIFF 3 ตัวชี้ `/liff/booking`, `/liff/checkin`, `/liff/pow` → ใส่ ID ใน env
7. `npm run richmenu:images && npm run richmenu:upload` → ใส่ `RICH_MENU_ID_*` ใน env
8. ใส่ GitHub Secrets ชุดเดียวกับ `.env` สำหรับ workflow `ops-early-warning.yml`

## Business rules

- **Packages:** S Lite ฿2,900 (4 routine) · M Growth ฿6,900 (8 routine + combo_mini_deep/mo) · L Premium ฿9,900 (12 routine + combo_full_big every 2 mo)
- **Affiliate:** 10% of referred **package amount** (ราคาแพ็คเต็ม) → referrer credit during promo phase; **credits never expire**; bill floors at ฿0
- **Promo phase 1:** ends `PROMO_END_DATE` (default 2026-12-31 BKK). After that, no new Early Bird bookings / no new affiliate grants until phase 2.
- **Payments:** โอนธนาคาร + สลิปใน LINE → แอดมินยืนยัน (`payments` ledger)
- **Roles:** admin (`LINE_OWNER_USER_ID`) > staff (sheet) > customer (sheet) > guest→customer menu
- **Early warning:** `time_slot` + 15 minutes (not a fixed clock time)

### Billing (LINE)

| ใคร | คำสั่ง / การใช้ |
|-----|----------------|
| แอดมิน | `ออกบิล CUS-xxx` · `ออกบิล CUS-xxx มัดจำ` · `ยืนยัน PAY-xxx` · `ปฏิเสธ PAY-xxx` · เมนู Billing |
| ลูกค้า | รับ Flex บิล → โอน → ส่งรูปสลิป · พิมพ์ `บิล` / `เครดิต` |

รายละเอียดเพิ่ม: `webhook/README.md` และ README ในแต่ละโมดูล
