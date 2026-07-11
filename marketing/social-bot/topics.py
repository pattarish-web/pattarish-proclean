"""Rotating topics for daily social content."""

from __future__ import annotations

# format: "video" ~40% (Ken Burns clips for FB/IG Reels); "image" for still posts.
# TikTok always gets a 9:16 clip regardless of format.
VIDEO_TOPIC_IDS = frozenset(
    {"office_ondemand", "agency_focus", "price_pack", "affiliate"}
)

# headline/angle: ไทยสั้นๆ สบายๆ มั่นใจ แม่นยำ — อ่านบนกราฟิกได้ชัด
TOPICS: list[dict[str, str]] = [
    {
        "id": "office_ondemand",
        "label": "แม่บ้านออฟฟิศ On-Demand",
        "angle": "ไม่จ้างประจำ ก็เรียกใช้ได้ โซนอุดมสุข–บางนา",
        "headline": "ออฟฟิศสะอาด โดยไม่จ้างประจำ",
        "format": "video",
    },
    {
        "id": "agency_focus",
        "label": "เอเจนซี่ / ทีมครีเอทีฟ",
        "angle": "โฟกัสงานสร้างสรรค์ เรื่องคลีนเรารับ มี QC + คนสำรอง",
        "headline": "เอเจนซี่โฟกัสงาน เราดูแลคลีน",
        "format": "video",
    },
    {
        "id": "tech_team",
        "label": "บริษัท Tech / สตาร์ทอัพ",
        "angle": "GPS check-in + รูปก่อน–หลัง โปร่งใส ออฟฟิศพร้อมลุย",
        "headline": "Tech team อยากได้ออฟฟิศที่พร้อม",
        "format": "image",
    },
    {
        "id": "big_cleaning",
        "label": "Big Cleaning",
        "angle": "คลีนลึกคราบฝัง ทีมมืออาชีพประสบการณ์ 30+ ปี",
        "headline": "Big Cleaning ที่จบงานจริง",
        "format": "image",
    },
    {
        "id": "maid_backup",
        "label": "แม่บ้านประจำ + คนสำรอง",
        "angle": "ทำงานในนามบริษัท มี QC และคนทดแทนเมื่อลา",
        "headline": "แม่บ้านประจำ ที่ไม่ทิ้งงานกลางคัน",
        "format": "image",
    },
    {
        "id": "service_area",
        "label": "พื้นที่บริการ",
        "angle": "กทม. นนทบุรี สมุทรปราการ ปทุมธานี ชลบุรี ระยอง",
        "headline": "คลีนถึงโซนที่คุณอยู่",
        "format": "image",
    },
    {
        "id": "price_pack",
        "label": "แพ็ค S / M ออฟฟิศ",
        "angle": "S ฿2,900 / M ฿6,900 ต่อเดือน โฮมออฟฟิศ–เอเจนซี่",
        "headline": "แพ็คแม่บ้านออฟฟิศ ราคาชัด",
        "format": "video",
    },
    {
        "id": "affiliate",
        "label": "ชวนเพื่อนรับเครดิต",
        "angle": "ชวนเพื่อนในโซน ได้เครดิตคืน 10% สะสมถึงสิ้นปี",
        "headline": "ชวนเพื่อนในโซน ได้เครดิตคืน",
        "format": "video",
    },
    {
        "id": "after_construction",
        "label": "หลังก่อสร้าง",
        "angle": "ฝุ่นปูน คราบสี เคลียร์ก่อนเข้าอยู่หรือเปิดร้าน",
        "headline": "หลังก่อสร้าง — เคลียร์ฝุ่นคราบ",
        "format": "image",
    },
    {
        "id": "soft_cleaning",
        "label": "Soft Cleaning",
        "angle": "คลีนประจำ อ่อนโยนกับพื้นผิว ออฟฟิศและคอนโด",
        "headline": "Soft Cleaning ดูแลคลีนประจำ",
        "format": "image",
    },
]


def pick_topic(last_id: str | None) -> dict[str, str]:
    if not last_id:
        return TOPICS[0]
    ids = [t["id"] for t in TOPICS]
    try:
        idx = ids.index(last_id)
    except ValueError:
        return TOPICS[0]
    return TOPICS[(idx + 1) % len(TOPICS)]
