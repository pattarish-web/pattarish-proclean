# Role Detection

| Role | Source | Rich Menu |
|------|--------|-----------|
| admin | LINE_OWNER_USER_ID (comma-separated) | modules/admin |
| staff | staff sheet status active\|training | modules/staff |
| customer | customers.line_user_id | modules/customer |
| guest | not found | customer menu (can book) |

Priority: admin > staff > customer > guest

Package codes: S=Lite 2900, M=Growth 6900, L=Premium 9900
