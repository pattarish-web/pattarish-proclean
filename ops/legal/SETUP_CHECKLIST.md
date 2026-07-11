# เฟส 1 — Checklist นิติบุคคลและแบรนด์ Sangkan Office

## จดนิติบุคคล + VAT

- [ ] จดทะเบียนบริษัทผ่าน [DBD e-Registration](https://ereg.dbd.go.th/)
- [ ] จด VAT 7% หลังทุนจดทะเบียนครบ (หรือตามเกณฑ์ยอดขาย)
- [ ] ใช้ Virtual Office True Digital Park (~฿8,500/ปี) เป็นที่ตั้งบริษัท
- [ ] เปิดบัญชีธนาคารนิติบุคคล
- [ ] ตั้งค่าระบบออกใบกำกับภาษี (e-Tax Invoice)

## Sub-brand Sangkan Office

- [ ] ใช้ชื่อ **Sangkan Office** บน landing, Rich Menu, และสื่อขาย
- [ ] แสดง parent brand: "โดย Sangkan Clean" ทุกจุดสัมผัส
- [ ] ออกแบบโลโก้ย่อย (ใช้สี teal `#0d9488` ตาม brand หลัก)
- [ ] สั่งกล่องท้ายรถมอเตอร์ไซค์พร้อมโลโก้ Sangkan Office

## LINE Official Account

- [ ] Verify LINE OA `@sangkanclean` (ถ้ายังไม่ verify)
- [ ] สร้าง Channel ใน [LINE Developers Console](https://developers.line.biz/)
- [ ] เปิด Messaging API + ออก Channel Access Token
- [ ] ตั้ง Webhook URL ชี้ไป Make.com หรือ `ops/webhook/`
- [ ] สร้าง LIFF apps ตาม `ops/liff/` (checkin, qc-upload)
- [ ] อัปโหลด Rich Menu จาก `ops/line/rich-menu.json`
- [ ] เก็บ credentials ใน `.env` (อย่า commit):

```env
LINE_CHANNEL_ACCESS_TOKEN=
LINE_CHANNEL_SECRET=
LINE_OWNER_USER_ID=
LIFF_CHECKIN_ID=
LIFF_QC_UPLOAD_ID=
GOOGLE_SHEETS_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=
MAKE_WEBHOOK_URL=
```

## งบประมาณเริ่มต้น ฿85,000

| รายการ | งบ |
|--------|-----|
| Google Ads เดือน 1 | ~฿5,500 |
| Virtual Office + จด VAT | ~฿8,500 |
| LINE / Make / Hosting | ~฿2,500 |
| อุปกรณ์ + กล่องท้ายรถ | ~฿5,000 |
| เงินทุนหมุนเวียน | ~฿63,500 |
