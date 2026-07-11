# โมดูลลูกค้า

## ไฟล์

| ไฟล์ | ใช้ทำอะไร |
|------|-----------|
| `rich-menu.json` | พื้นที่ 6 ช่อง — อัปโหลดผ่าน LINE API พร้อมรูป 2500×1686 |
| `liff-booking.html` | LIFF จอง Early Bird |

## อัปโหลด Rich Menu

1. ออกแบบรูปเมนู 2500×1686 ตาม 6 ช่อง  
2. `POST /v2/bot/richmenu` ด้วย body จาก `rich-menu.json`  
3. อัปรูป `POST /v2/bot/richmenu/{id}/content`  
4. ใส่ `RICH_MENU_ID_CUSTOMER` ใน env  

## Postback items

`packages` | `book` | `next_job` | `pow` | `affiliate` | `help`

## LIFF

Endpoint: `/liff/booking` (served from this folder by the webhook server)
