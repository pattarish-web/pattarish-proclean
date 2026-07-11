# Google Sheets Schema — Sangkan Office Ops

Spreadsheet หนึ่งไฟล์ 7 แท็บ — ชื่อชีตให้ตรงด้านล่าง  
Service account ต้องมีสิทธิ์ Editor

## Packages

| id | name | price_thb | routine_per_month | combo |
|----|------|-----------|-------------------|-------|
| S | Lite Office | 2900 | 4 | — |
| M | Growth Office | 6900 | 8 | combo_mini_deep ×1/month (extra) |
| L | Premium Executive | 9900 | 12 | combo_full_big every 2 months (extra) |

## customers

id, company_name, contact_name, line_user_id, package (S|M|L), address, lat, lng, affiliate_code, referred_by_code, deposit_thb, deposit_status (pending|paid|applied), status (lead|booked|active|paused|churned), billing_credit_thb, created_at, notes

## staff

id, name, line_user_id, salary, zone, status (active|training|inactive), training_status, created_at

## jobs

id, customer_id, staff_id, date (YYYY-MM-DD), time_slot (HH:MM), type (routine|combo_mini_deep|combo_full_big), status (scheduled|checked_in|done|issue|cancelled), checkin_at, checkout_at, warned_at, notes

## checkins

id, job_id, staff_id, lat, lng, distance_m, valid (Y|N ≤200m), timestamp

## qc_photos

id, job_id, type (before|after), drive_url, timestamp

## affiliate

id, code, referrer_customer_id, referred_customer_id, payment_thb, credit_thb (10%), payment_date, applied_to_bill, created_at

## payments

id, customer_id, type (deposit|subscription|topup), amount_thb, credit_applied_thb, deposit_applied_thb, payable_thb, method (transfer), slip_url, status (pending|confirmed|rejected), confirmed_by, confirmed_at, note, created_at

- `amount_thb` = ยอดบิลก่อนหักเครดิต/มัดจำ (เช่น ราคาแพ็คเกจ)
- `credit_applied_thb` = เครดิต Affiliate ที่ใช้ในบิลนี้ (หักจาก billing_credit ตอนสร้างบิล)
- `deposit_applied_thb` = มัดจำที่นำมาหัก (เมื่อ deposit_status=paid)
- `payable_thb` = ยอดที่ลูกค้าต้องโอนจริง (= amount - credit - deposit, floor 0)
- Affiliate 10% คิดจาก `amount_thb` (ราคาแพ็คเต็ม) ตอน confirm บิล subscription — เฉพาะช่วงโปร (`PROMO_END_DATE`, เฟส 1 = 2026-12-31)
- `billing_credit_thb` ที่ได้แล้ว **ไม่หมดอายุ** — หลังหมดโปรแค่หยุดสะสมใหม่ (รอเฟส 2)

## Hire thresholds

L≥2 or M≥3 or S≥6 or revenue≥17000 (booked/active with deposit)

## Job generation

- S: 4× routine/month
- M: 8× routine + 1× combo_mini_deep/month (extra)
- L: 12× routine/month + 1× combo_full_big every 2 months (extra)
