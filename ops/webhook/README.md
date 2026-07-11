# Ops Webhook — Sangkan Office

Node.js LINE webhook + LIFF endpoints for 3 modules (customer / staff / admin).

## Setup

1. Create Google Sheet with tabs from `../shared/sheets/schema.md` (headers in `../shared/sheets/headers/`)
2. Create service account, share sheet as Editor, download JSON key
3. LINE Developers → Messaging API → Channel access token + channel secret
4. Copy env and fill secrets:

```bash
cp .env.example .env
```

5. Install & run locally:

```bash
cd ops/webhook
npm install
npm start
```

6. Deploy (recommended: **Render Docker** — see below), then set `PUBLIC_BASE_URL`
7. LINE Console → Webhook URL = `https://<host>/webhook` → Verify → Enable
8. Create 3 LIFF apps → put IDs in `.env` / host env → redeploy
9. Generate + upload Rich Menus → paste `RICH_MENU_ID_*` → redeploy
10. Add the same secrets as GitHub Actions secrets for `ops-early-warning.yml`

## Env

See `.env.example`

| Variable | Purpose |
|----------|---------|
| `LINE_CHANNEL_SECRET` | Webhook signature validation |
| `LINE_CHANNEL_ACCESS_TOKEN` | Messaging API |
| `LINE_OWNER_USER_ID` | Admin LINE user IDs (comma-separated) |
| `GOOGLE_SHEETS_ID` | Spreadsheet ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account JSON (raw or base64) |
| `LIFF_BOOKING_ID` / `LIFF_CHECKIN_ID` / `LIFF_POW_ID` | LIFF app IDs |
| `RICH_MENU_ID_CUSTOMER` / `STAFF` / `ADMIN` | Rich menu IDs |
| `GPS_RADIUS_M` | Check-in radius (default 200) |
| `AFFILIATE_PCT` | Referrer credit % (default 10) |
| `BANK_TRANSFER_INFO` | ข้อความบัญชี/PromptPay ใน Flex บิล |
| `PUBLIC_BASE_URL` | Public HTTPS base (no trailing slash) |
| `PORT` | HTTP port (default 3000) |

## Deploy (Render Docker)

`vercel.json` is legacy — this app is a long-running Node HTTP server. Prefer Docker.

1. Push `ops/` to GitHub (this repo)
2. [Render](https://render.com) → New → Blueprint → root directory **`ops`** (uses `ops/render.yaml`)
   - Or Web Service → Docker → Dockerfile path `ops/webhook/Dockerfile` → **Docker build context = `ops`**
3. Fill env vars from `.env.example` (at least LINE + Sheets + `PUBLIC_BASE_URL`)
4. After first deploy, open `https://<service>/health` → `{ "ok": true }`

Local Docker (from `ops/`):

```bash
docker build -f webhook/Dockerfile -t sangkan-ops .
docker run --env-file webhook/.env -p 3000:3000 -e PUBLIC_BASE_URL=https://YOUR_HOST sangkan-ops
```

## Connect LINE Webhook + LIFF + Rich Menu

### A. Webhook

1. LINE Developers → your Messaging API channel → Messaging API
2. Webhook URL: `https://<PUBLIC_BASE_URL host>/webhook`
3. Verify → Enable webhook
4. Disable auto-reply / greeting if they fight the bot (optional)

### B. LIFF (3 apps, same channel)

| LIFF | Endpoint |
|------|----------|
| Booking | `https://<host>/liff/booking` |
| Check-in | `https://<host>/liff/checkin` |
| PoW | `https://<host>/liff/pow` |

Size: Full. Put the three LIFF IDs into `LIFF_BOOKING_ID` / `LIFF_CHECKIN_ID` / `LIFF_POW_ID` and redeploy. The server injects these IDs into the HTML at serve time.

### C. Rich Menu

```bash
cd ops/webhook
npm run richmenu:images    # placeholder 2500×1686 PNGs (replace with branded art later)
npm run richmenu:upload    # needs LINE_CHANNEL_ACCESS_TOKEN in .env
```

Paste printed `RICH_MENU_ID_*` into `.env` / Render env → redeploy.  
On follow, the webhook links the menu for that user’s role (`admin` / `staff` / `customer`).

### D. Admin user

Set `LINE_OWNER_USER_ID` to your LINE user ID (comma-separated if several). Get it by messaging the bot once and reading webhook logs, or via LINE Developers “Your user ID” tools.

## Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/webhook` | POST | LINE webhook |
| `/api/booking` | POST | Create Early Bird booking |
| `/api/checkin` | POST | Staff GPS check-in |
| `/api/pow` | POST | Upload PoW photo URLs |
| `/api/affiliate/payment` | POST | Apply 10% affiliate credit (ใช้ภายใน confirm) |
| `/api/billing/create` | POST | ออกบิล + push Flex ลูกค้า |
| `/api/billing/confirm` | POST | แอดมินยืนยันสลิป → ตัดเครดิต + affiliate จากราคาแพ็คเต็ม (`amount_thb`) |
| `/api/billing/reject` | POST | ปฏิเสธสลิป + คืนเครดิตที่ reserve |
| `/liff/booking` | GET | Customer booking form |
| `/liff/checkin` | GET | Staff check-in LIFF |
| `/liff/pow` | GET | Staff PoW LIFF |
| `/health` | GET | Health check |

## Scripts

| Command | Purpose |
|---------|---------|
| `npm start` | HTTP server webhook + LIFF API |
| `npm run early-warning` | Scan jobs past start+15m without check-in → push admin |
| `npm run generate-jobs` | Generate routine+combo jobs from package rules |
| `npm run richmenu:images` | Generate placeholder rich-menu PNGs |
| `npm run richmenu:upload` | Create + upload rich menus via LINE API |
