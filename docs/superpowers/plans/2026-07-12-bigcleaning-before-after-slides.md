# Big Cleaning Before/After Slides — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an 8-pair before/after carousel with drag comparison sliders to `landing-bigcleaning.html`, using generated photorealistic paired images.

**Architecture:** New `#before-after` section between pricing and social proof. Vanilla JS carousel + CSS clip-path comparison slider. Images generated via Gemini (`gemini_api.py`) into `images/before-after/`.

**Tech Stack:** HTML, CSS (`style-bigcleaning.css`), vanilla JS, Gemini image API, JPEG assets

## Global Constraints

- No on-page “not real customer work” disclaimer
- Vanilla only — no comparison libraries
- 8 pairs: factory, post-construction, bathroom, hotel, condo, office, showroom, glass-floor
- Placement: after `#pricing`, before `#social-proof`
- Match existing teal/glass landing tokens
- Changing slides resets comparison handle to 50%
- `prefers-reduced-motion`: no autoplay

---

### Task 1: Generate 16 paired images

**Files:**
- Create: `scripts/generate_before_after.py` (or run inline once)
- Create: `images/before-after/01-factory-before.jpg` … `08-glass-floor-after.jpg`

**Interfaces:**
- Produces: 16 JPEG files named per design spec

- [ ] **Step 1:** Ensure `images/before-after/` exists
- [ ] **Step 2:** Generate each BEFORE with locked scene prompt (photorealistic documentary photo, no text overlays, no people faces if avoidable)
- [ ] **Step 3:** Generate each AFTER by editing the BEFORE image (same camera/lighting/layout, only soil removed) via Gemini multimodal image input
- [ ] **Step 4:** Verify all 16 files exist and open cleanly

### Task 2: CSS for section + carousel + comparison

**Files:**
- Modify: `style-bigcleaning.css` (append before-after block)

- [ ] **Step 1:** Add `.ba-section`, `.ba-carousel`, `.ba-slide`, `.ba-compare`, handle, badges, arrows, dots, reduced-motion
- [ ] **Step 2:** Mobile touch hit-area for handle; avoid floating CTA collision

### Task 3: HTML section markup

**Files:**
- Modify: `landing-bigcleaning.html` (insert between pricing and social proof)

- [ ] **Step 1:** Insert `#before-after` with 8 slides, intensity badges, img pairs, carousel chrome
- [ ] **Step 2:** Wire `alt` text in Thai

### Task 4: Carousel + comparison JS

**Files:**
- Modify: `landing-bigcleaning.html` script block

- [ ] **Step 1:** Comparison slider init (pointer + keyboard)
- [ ] **Step 2:** Carousel prev/next/dots/swipe + autoplay pause rules + handle reset on slide change
- [ ] **Step 3:** Manual check in browser: drag, swipe, arrows, reduced-motion

### Task 5: Verify

- [ ] Open local `landing-bigcleaning.html`, confirm section order and interactions
- [ ] Confirm all 8 pairs load

**Note:** Do not commit unless the user asks.
