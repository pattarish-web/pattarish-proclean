# Sangkan SEO + LINE Ops — คู่มือย้ายเครื่อง / Machine Setup

โปรเจกต์นี้พกสกิลเอเจนต์ไว้ใน repo สำหรับย้ายเครื่อง

## สิ่งที่อยู่ในโปรเจกต์

| path | ความหมาย |
|------|----------|
| `.agents/skills/` | สกิลภายนอก (SEO/Node) + สกิลธุรกิจ |
| `.cursor/skills/sangkan-*` | สกิลธุรกิจติด git |
| `scripts/restore-agent-skills.ps1` | รีติดตั้งสกิลภายนอกบนเครื่องใหม่ |
| `AGENTS.md` | โน้ตให้เอเจนต์ |
| `ops/` | LINE webhook + LIFF + Sheets schema |

ERP / ใบเสนอราคา / Topology อยู่ที่ repo พี่น้อง: `../sangkan-clean`  
สเปก: `../sangkan-clean/docs/superpowers/specs/2026-07-12-erp-spine-redesign-design.md`

## ย้ายเครื่อง

```powershell
cd cleaning-seo-website
powershell -ExecutionPolicy Bypass -File .\scripts\restore-agent-skills.ps1
```

แล้ว Reload Window ใน Cursor

## คู่กับ ERP

| งาน | Repo |
|-----|------|
| Blog / GEO / landing / FormSubmit | ที่นี่ |
| LINE webhook / Sheets / LIFF | `ops/` ที่นี่ |
| CRM / QT / ใบกำกับ / Topology | `sangkan-clean` |
