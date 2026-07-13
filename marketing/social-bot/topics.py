"""Rotating topics for daily social content — Content Cluster strategy.

Each cluster groups 2 educational posts + 1 promotional post around the same
theme so the knowledge content naturally leads into the sales pitch.
Rotation order: Edu1 → Edu2 → Promo → (next cluster) Edu1 → Edu2 → Promo …
"""

from __future__ import annotations

# format: "video" ~40% (Ken Burns clips for FB/IG Reels); "image" for still posts.
# TikTok always gets a 9:16 clip regardless of format.
VIDEO_TOPIC_IDS = frozenset(
    {"office_ondemand", "agency_focus", "price_pack", "affiliate"}
)

# ---------- Content Clusters --------------------------------------------------
# Each cluster = list of 3 dicts: [edu1, edu2, promo]
# type: "edu" = educational / value-first content (no hard sell)
#       "promo" = promotional content with CTA

CLUSTERS: list[list[dict[str, str]]] = [
    # ── Cluster 1: ออฟฟิศ On-Demand ──
    [
        {
            "id": "edu_desk_germ",
            "type": "edu",
            "cluster": "office_ondemand",
            "label": "5 จุดในออฟฟิศที่สกปรกกว่าฝารองนั่ง",
            "angle": "คีย์บอร์ด โทรศัพท์ ลูกบิดประตู — แบคทีเรียมากกว่าห้องน้ำ",
            "headline": "5 จุดสกปรก ที่คุณสัมผัสทุกวัน",
            "format": "image",
        },
        {
            "id": "edu_germ_lifespan",
            "type": "edu",
            "cluster": "office_ondemand",
            "label": "เชื้อโรคบนโต๊ะทำงาน อยู่ได้นานแค่ไหน?",
            "angle": "ไวรัสไข้หวัดอยู่บนพื้นผิวได้ 24 ชม. แบคทีเรียอยู่ได้หลายวัน",
            "headline": "เชื้อโรคบนโต๊ะ อยู่ได้กี่ชั่วโมง?",
            "format": "image",
        },
        {
            "id": "office_ondemand",
            "type": "promo",
            "cluster": "office_ondemand",
            "label": "แม่บ้านออฟฟิศ On-Demand",
            "angle": "เรียกใช้ได้ ไม่จ้างประจำ โซนอุดมสุข–บางนา",
            "headline": "ออฟฟิศสะอาด โดยไม่จ้างประจำ",
            "format": "video",
        },
    ],
    # ── Cluster 2: เอเจนซี่ / ครีเอทีฟ ──
    [
        {
            "id": "edu_productivity",
            "type": "edu",
            "cluster": "agency_focus",
            "label": "ออฟฟิศสะอาด เพิ่ม Productivity ได้จริงหรือ?",
            "angle": "งานวิจัยชี้ สภาพแวดล้อมสะอาดช่วยโฟกัสดีขึ้น 15%",
            "headline": "ออฟฟิศสะอาด = ทำงานดีขึ้น?",
            "format": "image",
        },
        {
            "id": "edu_creative_block",
            "type": "edu",
            "cluster": "agency_focus",
            "label": "Creative Block อาจเกิดจากสภาพแวดล้อมไม่ดี",
            "angle": "สมองต้องการพื้นที่ปลอดโปร่ง เพื่อคิดสร้างสรรค์",
            "headline": "Creative Block ที่แท้คือออฟฟิศ?",
            "format": "image",
        },
        {
            "id": "agency_focus",
            "type": "promo",
            "cluster": "agency_focus",
            "label": "เอเจนซี่ / ทีมครีเอทีฟ",
            "angle": "โฟกัสงานครีเอทีฟ คลีนมี QC + คนสำรอง",
            "headline": "เอเจนซี่โฟกัสงาน เราดูแลคลีน",
            "format": "video",
        },
    ],
    # ── Cluster 3: Tech / สตาร์ทอัพ ──
    [
        {
            "id": "edu_dust_it",
            "type": "edu",
            "cluster": "tech_team",
            "label": "ฝุ่นตัวร้ายของอุปกรณ์ IT ที่หลายคนมองข้าม",
            "angle": "ฝุ่นสะสมทำให้คอมร้อน พัดลมทำงานหนัก อายุสั้นลง",
            "headline": "ฝุ่น ทำลายคอมคุณอยู่ทุกวัน",
            "format": "image",
        },
        {
            "id": "edu_server_room",
            "type": "edu",
            "cluster": "tech_team",
            "label": "Server Room และมุมอับในออฟฟิศ ดูแลยังไง?",
            "angle": "จุดที่แอร์ไม่ถึง ฝุ่นสะสมเร็วกว่าปกติ 3 เท่า",
            "headline": "Server Room สะอาด ระบบมั่นคง",
            "format": "image",
        },
        {
            "id": "tech_team",
            "type": "promo",
            "cluster": "tech_team",
            "label": "บริษัท Tech / สตาร์ทอัพ",
            "angle": "GPS + รูปก่อน–หลัง ออฟฟิศพร้อมลุย",
            "headline": "Tech team อยากได้ออฟฟิศที่พร้อม",
            "format": "image",
        },
    ],
    # ── Cluster 4: Big Cleaning ──
    [
        {
            "id": "edu_big_clean_why",
            "type": "edu",
            "cluster": "big_cleaning",
            "label": "ทำไมต้อง Big Cleaning อย่างน้อยปีละ 2 ครั้ง?",
            "angle": "คราบฝังลึก เชื้อรา แบคทีเรียสะสมในจุดที่มองไม่เห็น",
            "headline": "Big Cleaning ปีละ 2 ครั้ง ทำไม?",
            "format": "image",
        },
        {
            "id": "edu_hidden_dirt",
            "type": "edu",
            "cluster": "big_cleaning",
            "label": "คราบฝังลึกที่ทำความสะอาดปกติไม่ถึง",
            "angle": "ใต้เฟอร์นิเจอร์ รางแอร์ ร่องกระเบื้อง — จุดที่ถูกลืม",
            "headline": "จุดที่ทำความสะอาดปกติไม่ถึง",
            "format": "image",
        },
        {
            "id": "big_cleaning",
            "type": "promo",
            "cluster": "big_cleaning",
            "label": "Big Cleaning",
            "angle": "คลีนลึกคราบฝัง ทีมมืออาชีพ 30+ ปี",
            "headline": "Big Cleaning ที่จบงานจริง",
            "format": "image",
        },
    ],
    # ── Cluster 5: แม่บ้านประจำ + คนสำรอง ──
    [
        {
            "id": "edu_checklist",
            "type": "edu",
            "cluster": "maid_backup",
            "label": "Checklist ทำความสะอาดออฟฟิศระดับมืออาชีพ",
            "angle": "จุดที่ต้องทำทุกวัน ทุกสัปดาห์ และทุกเดือน",
            "headline": "Checklist คลีนออฟฟิศ มืออาชีพ ✅",
            "format": "image",
        },
        {
            "id": "edu_maid_absent",
            "type": "edu",
            "cluster": "maid_backup",
            "label": "แม่บ้านลาหยุดกะทันหัน จัดการยังไงดี?",
            "angle": "ปัญหาที่ทุกออฟฟิศเจอ — ไม่มีคนสำรอง ออฟฟิศไม่ได้คลีน",
            "headline": "แม่บ้านลา ออฟฟิศไม่ได้คลีน?",
            "format": "image",
        },
        {
            "id": "maid_backup",
            "type": "promo",
            "cluster": "maid_backup",
            "label": "แม่บ้านประจำ + คนสำรอง",
            "angle": "มี QC และคนทดแทนเมื่อลา",
            "headline": "แม่บ้านประจำ ที่ไม่ทิ้งงานกลางคัน",
            "format": "image",
        },
    ],
    # ── Cluster 6: พื้นที่บริการ ──
    [
        {
            "id": "edu_zone_problems",
            "type": "edu",
            "cluster": "service_area",
            "label": "ออฟฟิศแต่ละย่าน เจอปัญหาความสะอาดต่างกันยังไง?",
            "angle": "ริมถนนใหญ่ ฝุ่นเยอะ / ใกล้น้ำ ชื้นง่าย / ตึกเก่า คราบฝัง",
            "headline": "ย่านไหน ปัญหาคลีนต่างกัน?",
            "format": "image",
        },
        {
            "id": "edu_pm25",
            "type": "edu",
            "cluster": "service_area",
            "label": "ฝุ่น PM2.5 กับออฟฟิศริมถนนใหญ่",
            "angle": "ฝุ่นละอองเข้าออฟฟิศตามรอยเปิดปิดประตู ส่งผลต่อสุขภาพ",
            "headline": "PM2.5 เข้าออฟฟิศ ดูแลยังไง?",
            "format": "image",
        },
        {
            "id": "service_area",
            "type": "promo",
            "cluster": "service_area",
            "label": "พื้นที่บริการ",
            "angle": "กทม. นนทบุรี สมุทรปราการ ปทุมฯ ชลบุรี ระยอง",
            "headline": "คลีนถึงโซนที่คุณอยู่",
            "format": "image",
        },
    ],
    # ── Cluster 7: แพ็คราคา ──
    [
        {
            "id": "edu_outsource_vs_hire",
            "type": "edu",
            "cluster": "price_pack",
            "label": "จ้างแม่บ้านเอง vs. Outsource อะไรคุ้มกว่า?",
            "angle": "เปรียบเทียบต้นทุน เวลา และความเสี่ยง อย่างตรงไปตรงมา",
            "headline": "จ้างเอง vs. Outsource คุ้มกว่า?",
            "format": "image",
        },
        {
            "id": "edu_hidden_cost",
            "type": "edu",
            "cluster": "price_pack",
            "label": "ต้นทุนแฝงของการจ้างแม่บ้านเองที่ไม่มีใครบอก",
            "angle": "ประกันสังคม อุปกรณ์ สำรองคนลา — ต้นทุนที่ซ่อนอยู่",
            "headline": "ต้นทุนแฝง จ้างแม่บ้านเอง 💰",
            "format": "image",
        },
        {
            "id": "price_pack",
            "type": "promo",
            "cluster": "price_pack",
            "label": "แพ็ค S / M ออฟฟิศ",
            "angle": "S ฿2,900 / M ฿6,900 ต่อเดือน",
            "headline": "แพ็คแม่บ้านออฟฟิศ ราคาชัด",
            "format": "video",
        },
    ],
    # ── Cluster 8: Affiliate ──
    [
        {
            "id": "edu_building_hygiene",
            "type": "edu",
            "cluster": "affiliate",
            "label": "ออฟฟิศในตึกเดียวกัน ช่วยกันรักษาความสะอาดได้",
            "angle": "ถ้าทั้งชั้นสะอาด โอกาสปนเปื้อนข้ามห้องลดลง",
            "headline": "ตึกสะอาด เริ่มจากทุกออฟฟิศ",
            "format": "image",
        },
        {
            "id": "edu_zone_clean",
            "type": "edu",
            "cluster": "affiliate",
            "label": "ทำไมตึกสะอาดทั้งชั้น ดีกว่าสะอาดห้องเดียว?",
            "angle": "แมลง ฝุ่น และกลิ่นเดินทางข้ามห้องได้ — ดูแลด้วยกันดีกว่า",
            "headline": "สะอาดทั้งชั้น > สะอาดห้องเดียว",
            "format": "image",
        },
        {
            "id": "affiliate",
            "type": "promo",
            "cluster": "affiliate",
            "label": "ชวนเพื่อนรับเครดิต",
            "angle": "ชวนเพื่อนในโซน ได้เครดิตคืน 10%",
            "headline": "ชวนเพื่อนในโซน ได้เครดิตคืน",
            "format": "video",
        },
    ],
    # ── Cluster 9: หลังก่อสร้าง ──
    [
        {
            "id": "edu_construction_dust",
            "type": "edu",
            "cluster": "after_construction",
            "label": "ฝุ่นปูนหลังรีโนเวท อันตรายกว่าที่คิด",
            "angle": "ฝุ่นซิลิกาจากงานก่อสร้างเข้าปอดได้ ต้องคลีนก่อนเข้าใช้",
            "headline": "ฝุ่นปูนหลังรีโนเวท ⚠️ อันตราย",
            "format": "image",
        },
        {
            "id": "edu_move_in_clean",
            "type": "edu",
            "cluster": "after_construction",
            "label": "ย้ายเข้าออฟฟิศใหม่ ต้อง Deep Clean ก่อนทุกครั้ง",
            "angle": "สารเคมี ฝุ่น คราบสี ที่ตาเปล่ามองไม่เห็น แต่สูดเข้าไปได้",
            "headline": "ก่อนย้ายเข้า ต้อง Deep Clean",
            "format": "image",
        },
        {
            "id": "after_construction",
            "type": "promo",
            "cluster": "after_construction",
            "label": "หลังก่อสร้าง",
            "angle": "ฝุ่นปูน คราบสี เคลียร์ก่อนเข้าอยู่",
            "headline": "หลังก่อสร้าง — เคลียร์ฝุ่นคราบ",
            "format": "image",
        },
    ],
    # ── Cluster 10: Soft Cleaning ──
    [
        {
            "id": "edu_routine_clean",
            "type": "edu",
            "cluster": "soft_cleaning",
            "label": "ทำไมต้องคลีนประจำ ไม่ใช่รอจนสกปรก?",
            "angle": "เชื้อโรคสะสมทุกวัน ไม่ต้องรอเห็นคราบแล้วค่อยทำ",
            "headline": "คลีนประจำ ดีกว่ารอจนสกปรก",
            "format": "image",
        },
        {
            "id": "edu_harsh_chemical",
            "type": "edu",
            "cluster": "soft_cleaning",
            "label": "สารเคมีแรงๆ ทำลายเฟอร์นิเจอร์ออฟฟิศยังไง?",
            "angle": "น้ำยาที่ไม่เหมาะ ทำให้หนังลอก ไม้ด่าง สีเปลี่ยน",
            "headline": "น้ำยาผิด เฟอร์นิเจอร์พัง!",
            "format": "image",
        },
        {
            "id": "soft_cleaning",
            "type": "promo",
            "cluster": "soft_cleaning",
            "label": "Soft Cleaning",
            "angle": "คลีนประจำ อ่อนโยน ออฟฟิศและคอนโด",
            "headline": "Soft Cleaning ดูแลคลีนประจำ",
            "format": "image",
        },
    ],
]

# Flat list for iteration: edu1, edu2, promo, edu1, edu2, promo, …
TOPICS: list[dict[str, str]] = [
    topic for cluster in CLUSTERS for topic in cluster
]


def pick_topic(last_id: str | None) -> dict[str, str]:
    """Pick the next topic in the cluster rotation."""
    if not last_id:
        return TOPICS[0]
    ids = [t["id"] for t in TOPICS]
    try:
        idx = ids.index(last_id)
    except ValueError:
        return TOPICS[0]
    return TOPICS[(idx + 1) % len(TOPICS)]
