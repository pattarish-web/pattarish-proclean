# โมดูลแม่บ้าน (ใช้งานง่าย)

เมนู 4 ช่องใหญ่ ภาษาไทยสั้นๆ:

| ปุ่ม | ทำอะไร |
|------|--------|
| งานวันนี้ | ดูว่าวันนี้ไปที่ไหน |
| ถึงที่แล้ว | ยืนยันถึงหน้างาน (GPS อัตโนมัติ ไม่ต้องพิมพ์รหัส) |
| ส่งรูปงาน | ส่งรูปในแชท → เลือกก่อน/หลัง → พิมพ์ 「ส่งงานเสร็จ」 |
| มีปัญหา | เข้าไม่ได้ / ลูกค้าเลื่อน / อื่นๆ |

ตั้ง `RICH_MENU_ID_STAFF`, `LIFF_CHECKIN_ID`, `LIFF_POW_ID`, `GOOGLE_DRIVE_FOLDER_ID`

## เก็บรูปหลายใบใน Google Drive

1. สร้างโฟลเดอร์ใน Google Drive ของคุณ เช่น `Sangkan Office PoW`
2. Share ให้ `sangkan-office-ops@seo-keyword-tool-501418.iam.gserviceaccount.com` เป็น **Editor**
3. คัดลอก Folder ID จาก URL  
   `https://drive.google.com/drive/folders/`**`FOLDER_ID`**
4. ใส่ใน `.env`: `GOOGLE_DRIVE_FOLDER_ID=...`
5. เปิด **Google Drive API** ในโปรเจกต์ GCP เดียวกับ service account
