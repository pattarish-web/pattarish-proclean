# โมดูลการจัดการ

## ไฟล์

| ไฟล์ | ใช้ทำอะไร |
|------|-----------|
| `rich-menu.json` | ยอดจอง / งานวันนี้ / Warning / ลูกค้าใหม่ / แม่บ้าน / **บิลค้าง** |

ตั้ง `RICH_MENU_ID_ADMIN` และ `LINE_OWNER_USER_ID`

## Billing (โอน + สลิป)

| คำสั่ง | ผล |
|--------|-----|
| `ออกบิล CUS-xxx` | บิลรายเดือน (หักมัดจำ+เครดิต) → Flex ลูกค้า |
| `ออกบิล CUS-xxx มัดจำ` | บิลมัดจำ Early Bird |
| `ยืนยัน PAY-xxx` | ยืนยันสลิป → affiliate 10% จากราคาแพ็คเต็ม |
| `ปฏิเสธ PAY-xxx` | ปฏิเสธ + คืนเครดิตที่ reserve |

หรือกดปุ่มใน Flex ที่ระบบ push หลังลูกค้าส่งสลิป / เมนู Billing

Early Warning รันจาก GitHub Actions: `.github/workflows/ops-early-warning.yml`

## Hire thresholds

L≥2 หรือ M≥3 หรือ S≥6 หรือ revenue≥฿17,000 (สถานะ booked/active)
