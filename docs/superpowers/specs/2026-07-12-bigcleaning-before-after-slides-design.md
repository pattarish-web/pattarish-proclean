# Big Cleaning Before/After Slides — Design Spec

**Date:** 2026-07-12  
**Page:** `landing-bigcleaning.html` (`https://www.sangkanclean.com/landing-bigcleaning.html`)  
**Status:** Approved for planning (pending user review of this written spec)

## Goal

Add a before/after results section to the Big Cleaning landing page so visitors can see cleaning outcomes across heavy and light job types. Interaction is a carousel of pairs; each pair uses a drag comparison slider.

## Placement

Insert a new section **after Pricing (`#pricing`)** and **before Social Proof (`#social-proof`)**.

Suggested section id: `#before-after`.

## Section structure

- Section label + headline (Thai), e.g. “ก่อนทำ → หลังทำ”
- One short supporting sentence
- Carousel showing **one pair at a time** (mobile and desktop)
- Per slide:
  - Venue / job type title
  - Intensity badge: `งานหนัก` | `งานปานกลาง` | `งานเบา`
  - Before/after comparison slider
- Controls: prev/next arrows, dot pagination, swipe on touch
- Slow autoplay; pause on user interaction (drag handle, arrow, swipe, focus)
- Honor `prefers-reduced-motion`: no autoplay

## Interaction model (Approach 1 — vanilla)

**Carousel + comparison slider per pair**, implemented in-page with vanilla JS (no new comparison library).

### Comparison slider

- Base layer: after image
- Overlay layer: before image, clipped from left by a vertical divider
- Draggable vertical handle with “ก่อน” / “หลัง” labels
- Mouse + touch + keyboard (arrow keys when handle focused)
- Default divider position ~50%

### Carousel

- One active slide; others hidden/offscreen
- Arrows + dots + horizontal swipe
- Changing slides always resets the comparison handle to 50%

## Content: 8 pairs

Images are **generated photorealistic pairs** (matching camera angle, lighting, and furnishings between before and after). No on-page disclaimer that images are not real customer jobs (explicit product decision).

| # | Slug | Venue (TH) | Intensity | Before | After |
|---|------|------------|-----------|--------|-------|
| 1 | `factory` | โรงงาน | งานหนัก | Floor oil stains, machine dust | Clean dry industrial floor |
| 2 | `post-construction` | หลังก่อสร้าง | งานหนัก | Cement dust, debris, rough floor | Clear, clean, handover-ready |
| 3 | `bathroom` | ห้องน้ำคราบหนัก | งานหนัก | Limescale, rust, dull tiles | Bright clean bathroom |
| 4 | `hotel` | โรงแรม | งานปานกลาง | Stained lobby carpet/dust | Guest-ready lobby |
| 5 | `condo` | คอนโด | งานปานกลาง | Kitchen/floor soil buildup | Move-in clean |
| 6 | `office` | ออฟฟิศ | งานเบา | Dusty desks, dull floor | Ordered, clean office |
| 7 | `showroom` | โชว์รูม | งานเบา | Dusty displays, dull floor | Glossy floor, clean displays |
| 8 | `glass-floor` | พื้นกระจก / หินขัด | งานเบา | Footprints, haze | Mirror-gloss surface |

### Asset naming

Directory: `images/before-after/`

```
01-factory-before.jpg
01-factory-after.jpg
02-post-construction-before.jpg
02-post-construction-after.jpg
03-bathroom-before.jpg
03-bathroom-after.jpg
04-hotel-before.jpg
04-hotel-after.jpg
05-condo-before.jpg
05-condo-after.jpg
06-office-before.jpg
06-office-after.jpg
07-showroom-before.jpg
07-showroom-after.jpg
08-glass-floor-before.jpg
08-glass-floor-after.jpg
```

Web-optimized JPEG; target roughly 1200–1600px on the long edge for retina without huge payloads.

## Visual / CSS

- Match existing Big Cleaning landing tokens in `style-bigcleaning.css` (teal / glass language)
- Avoid extra nested card chrome; slider media is the visual anchor
- Full-bleed within the section’s content column (not inset collage cards)
- Touch-friendly handle hit area on mobile
- Must not collide with floating phone/LINE CTAs

## Files to change

| File | Change |
|------|--------|
| `landing-bigcleaning.html` | New `#before-after` section markup + carousel/slider script |
| `style-bigcleaning.css` | Section, carousel, comparison slider, badges, responsive rules |
| `images/before-after/*` | 16 generated images (8 before + 8 after) |

Optional: extract JS to a small dedicated file only if the inline script becomes hard to maintain; default is keep with the page’s existing script pattern.

## Out of scope

- Pulling live photos from ops/staff Drive tagging
- Third-party comparison libraries / CDN widgets
- Filter tabs by intensity
- Claiming or labeling images as specific named client case studies
- Changes to other landing pages in this pass

## Success criteria

1. Section appears between pricing and social proof on desktop and mobile
2. All 8 pairs are reachable via carousel controls and swipe
3. Each pair’s divider is draggable and clearly shows before vs after
4. Images look photorealistic and paired (same scene, different soil state)
5. Autoplay does not fight the user; reduced-motion users get no autoplay
6. Page still loads and existing CTAs/conversion markup remain intact

## Open decisions resolved

- Image source: generate realistic pairs
- No “not real customer work” disclaimer on page
- UX: carousel + per-pair drag compare
- Count/mix: 8 pairs (B)
- Placement: after pricing (B)
- Implementation: vanilla Approach 1
