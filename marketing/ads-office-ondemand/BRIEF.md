# Sangkan Office — Ad Artwork Brief

แคมเปญ: **แม่บ้านออฟฟิศ On-Demand** (โมเดล B + Affiliate)  
แบรนด์: **Sangkan Office** โดย Sangkan Clean · โซนอุดมสุข–บางนา

## Offer ที่ล็อก

| รายการ | รายละเอียด |
|--------|------------|
| Hook | ไม่ต้องจ้างแม่บ้านประจำ · เรียกใช้ได้ตามต้องการ |
| แพ็คในโฆษณา | **S ฿2,900** / **M ฿6,900** ต่อเดือน (M = แนะนำ) |
| Package L | ฿9,900 มีใน ops/LIFF — **ไม่ใส่ใน ad creative เฟสนี้** (upsell ในแชทเท่านั้น) |
| Affiliate | ชวนเพื่อนในโซน · รับเครดิตเงินคืน 10% ของยอดค่าใช้จ่าย |
| Affiliate terms | สะสมได้ถึงสิ้นปี · เครดิตไม่หมดอายุ ใช้จนกว่าจะหมด |

## กลุ่มเป้าหมาย

โฮมออฟฟิศ · ออฟฟิศเอเจนซี่ · บริษัท Tech · โซนอุดมสุข–บางนา

## สีและแบรนด์

- Primary `#0d9488` · Dark `#0f172a` · Accent `#f59e0b`
- โลโก้/ชื่อ: Sangkan Office
- Footer: โดย Sangkan Clean · LINE `@sangkanclean`

## ชุดครีเอทีฟ

| รหัส | แนว | ไฟล์ Feed |
|------|------|-----------|
| A | Hook vs จ้างประจำ | `feed/A-hook-no-permanent.png` |
| B | Price ladder S/M + affiliate line | `feed/B-price-sm.png` |
| C | Trust GPS / รูปก่อน-หลัง | `feed/C-trust-gps.png` |
| D | Early Bird | `feed/D-early-bird.png` |
| E | Affiliate เครดิตคืน 10% | `feed/E-affiliate-credit.png` |

Stories: `stories/` (A, B, D, E) · LINE: `line/` (A, B, E)

## สร้างภาพใหม่ (art-directed)

ภาพ editorial อยู่ใน `art/` แล้วคอมโพสิตข้อความมินิมอลทับ:

```bash
python marketing/ads-office-ondemand/generate_creatives.py
```

โทน: ภาพโบชัวร์พรีเมียม + ข้อความน้อย (ไม่ใช่ UI แอป / ไม่ผ่าแผงขาว)


## CTA และปลายทาง

ดู [cta.md](cta.md) — **ห้าม** ชี้ไป `landing-maid.html` (แม่บ้านประจำคนละออฟเฟอร์)

## อ้างอิง copy / สเปก

- [copy-th.md](copy-th.md)
- [specs.md](specs.md)
