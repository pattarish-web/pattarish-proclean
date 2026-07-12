# SEO, AIO, and GEO Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every public page technically complete for SEO and AI search while removing unsupported geographic and trust claims.

**Architecture:** Keep verified company identity in `site_config.py`, render that identity into all generated templates, and validate the final static files with a dependency-free Node quality gate. Service-area pages describe coverage with `areaServed`; no page asserts an unverified physical address, coordinate, map pin, branch, certification, statistic, rating, or review.

**Tech Stack:** Static HTML, Python generators, JSON-LD, Node.js standard library quality gate.

## Global Constraints

- Keep the public site a static Thai MPA; do not add React, Vite, or ERP routes.
- Preserve canonical URLs, FAQ content, crawlable HTML, sitemap integrity, LINE, telephone, and `#quote` CTAs.
- Do not modify `posts.json` or `seo.yml`; sanitize unsupported claims only when rendering public HTML.
- Do not invent an address, coordinate, Google Business Profile, certification, review, rating, historical metric, medical outcome, or local branch.
- Use `Organization` plus `Service` and typed `areaServed`; a service-area page is not proof of a physical location.

---

## File structure

| File | Responsibility |
|---|---|
| `site_config.py` | Verified business identity, shared organization schema, typed service-area schema |
| `build_local_pages.py` | Renders local service-area pages with area and breadcrumb JSON-LD |
| `build_service_landings.py` | Renders service pages with organization and breadcrumb JSON-LD |
| `build_blogs.py` | Renders blogs with full social metadata and removes unsupported claims only in output HTML |
| `build_assets.py` | Applies safe root-page markup upgrades and image-dimension normalization |
| `local_template.html`, `service_landing_template.html`, `blog_template.html` | Canonical source for generated public metadata and structured data |
| `index.html`, `blog.html`, `privacy.html`, `landing-*.html` | Hand-maintained indexable pages that need the same metadata/entity cleanup |
| `scripts/seo_quality_gate.mjs` | Static, dependency-free production quality gate |

### Task 1: Add the static quality gate

**Files:**
- Create: `scripts/seo_quality_gate.mjs`
- Test: `scripts/seo_quality_gate.mjs`

**Interfaces:**
- Consumes: generated `*.html`, `areas/*.html`, and `blog/*.html`.
- Produces: process exit code `0` and `SEO/AIO/GEO quality gate passed for N indexable pages` when valid; otherwise a line per violation and exit code `1`.

- [ ] **Step 1: Write the failing checks**

Create a Node standard-library script that recursively scans public HTML, excludes `.git`, `marketing`, `ops`, templates, verification files, and `noindex` redirects, and records these errors:

```js
const required = [
  ['title', /<title\b/i],
  ['description', /<meta[^>]+name=["']description["']/i],
  ['canonical', /<link[^>]+rel=["']canonical["']/i],
  ['og:title', /property=["']og:title["']/i],
  ['og:description', /property=["']og:description["']/i],
  ['og:image', /property=["']og:image["']/i],
  ['og:url', /property=["']og:url["']/i],
  ['og:type', /property=["']og:type["']/i],
  ['twitter:card', /name=["']twitter:card["']/i],
];

function assertPage(path, html) {
  for (const [name, pattern] of required) {
    if (!pattern.test(html)) errors.push(`${path}: missing ${name}`);
  }
  if ((html.match(/<h1\b/gi) || []).length !== 1) errors.push(`${path}: requires one h1`);
  if (/<meta[^>]+name=["']geo\./i.test(html) || /"geo"\s*:|"hasMap"\s*:/.test(html)) errors.push(`${path}: contains unverified GEO pin`);
}
```

Parse every `application/ld+json` script with `JSON.parse`, require `width` and `height` for every non-decorative `<img>`, and reject exact unsupported public-claim markers: `SGS ISO`, `BSI ISO`, `GHPs Standard`, `Green Industry`, `5,000`, `100%`, `99.9%`, and `30 ปี`.

- [ ] **Step 2: Run the gate to verify it fails against the current site**

Run: `node scripts/seo_quality_gate.mjs`

Expected: non-zero exit with missing social tags, image-dimension errors, legacy GEO fields, and unsupported claims.

- [ ] **Step 3: Add JSON-LD and crawl checks**

Extend the script to require `Organization` or an `@id` reference to `https://www.sangkanclean.com/#organization` on all generated service, local-area, and blog pages. Parse `sitemap-pages.xml` and `sitemap-blog.xml`; ensure every sitemap path exists and is indexable.

- [ ] **Step 4: Re-run the gate to retain the failing baseline**

Run: `node scripts/seo_quality_gate.mjs`

Expected: non-zero exit; keep the output as the baseline for Tasks 2-5.

- [ ] **Step 5: Commit the isolated gate**

```bash
git add scripts/seo_quality_gate.mjs
git commit -m "test: add static SEO quality gate"
```

### Task 2: Establish a verified organization and service-area schema

**Files:**
- Modify: `site_config.py`
- Modify: `build_local_pages.py`
- Modify: `build_service_landings.py`
- Test: `scripts/seo_quality_gate.mjs`

**Interfaces:**
- Produces `organization_schema()` returning an `Organization` object with `@id` `https://www.sangkanclean.com/#organization`.
- Produces `area_served_schema(names)` returning a list of `AdministrativeArea` objects.
- Builders consume `{{organization_schema}}`, `{{area_served_schema}}`, and `{{breadcrumb_schema}}` placeholders.

- [ ] **Step 1: Add failing source assertions to the quality gate**

Add a source-level check that generated area pages contain an `AdministrativeArea` object for their configured area and do not contain `LocalBusiness`, `GeoCoordinates`, `hasMap`, or `geo.*` meta tags.

- [ ] **Step 2: Confirm the assertion fails**

Run: `node scripts/seo_quality_gate.mjs`

Expected: every `areas/local-*.html` page fails the source assertion.

- [ ] **Step 3: Implement shared schema helpers**

Replace coordinate and map fields in `BUSINESS` with a stable organization ID and verified contact channels. Add these helpers to `site_config.py`:

```python
ORGANIZATION_ID = f"{SITE_URL}/#organization"

def organization_schema():
    return {
        "@type": "Organization",
        "@id": ORGANIZATION_ID,
        "name": "Sangkan Clean",
        "url": f"{SITE_URL}/",
        "telephone": BUSINESS["phone"],
        "email": BUSINESS["email"],
        "sameAs": [BUSINESS["facebook"], BUSINESS["line"], BUSINESS["messenger"]],
    }

def area_served_schema(names):
    return [{"@type": "AdministrativeArea", "name": name} for name in names]
```

In each builder, use `json.dumps(..., ensure_ascii=False)` for organization, area served, and a three-item `BreadcrumbList`; pass those strings to the template instead of a city address, coordinate, or generic slug.

- [ ] **Step 4: Rebuild local and service pages**

Run: `python build_local_pages.py` then `python build_service_landings.py`.

Expected: the console reports six local pages and seven service landings, each with the new schema.

- [ ] **Step 5: Run the gate for these surfaces**

Run: `node scripts/seo_quality_gate.mjs`

Expected: no GEO-pin or typed-area errors for `areas/*.html` and `landing-*.html`.

- [ ] **Step 6: Commit the entity model**

```bash
git add site_config.py build_local_pages.py build_service_landings.py
git commit -m "feat: use evidence-first organization schema"
```

### Task 3: Upgrade generated templates and rendered blog output

**Files:**
- Modify: `local_template.html`
- Modify: `service_landing_template.html`
- Modify: `blog_template.html`
- Modify: `build_blogs.py`
- Test: `scripts/seo_quality_gate.mjs`

**Interfaces:**
- Templates consume `{{organization_schema}}`, `{{breadcrumb_schema}}`, `{{area_served_schema}}`, `{{twitter_title}}`, and `{{twitter_description}}`.
- `sanitize_public_content(content: str) -> str` strips unsupported claim sentences only from rendered HTML.

- [ ] **Step 1: Add failing template tests to the quality gate**

Require complete Open Graph and Twitter metadata on all indexable HTML, a `BreadcrumbList` on service, local-area, and blog pages, and a resolvable organization reference in each JSON-LD graph.

- [ ] **Step 2: Confirm the template baseline fails**

Run: `node scripts/seo_quality_gate.mjs`

Expected: existing local/service pages fail social and breadcrumb checks; existing blog pages fail Twitter checks.

- [ ] **Step 3: Implement complete metadata and linked JSON-LD**

Use this pattern in the templates, retaining the existing canonical URLs and visible FAQ content:

```html
<meta property="og:type" content="website">
<meta property="og:title" content="{{title}} | Sangkan Clean">
<meta property="og:description" content="{{description}}">
<meta property="og:url" content="{{canonical}}">
<meta property="og:image" content="{{site_url}}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{title}} | Sangkan Clean">
<meta name="twitter:description" content="{{description}}">
<meta name="twitter:image" content="{{site_url}}/og-image.png">
```

Place the organization, `WebPage` or `Service`, `BreadcrumbList`, and existing `FAQPage`/`Article` entities in one `@graph`. Remove every legacy `geo.region`, `geo.placename`, `geo.position`, `ICBM`, `GeoCoordinates`, `hasMap`, and `LocalBusiness` field from these templates. Keep article `datePublished`, `dateModified`, and organization author/publisher references.

- [ ] **Step 4: Sanitize unsupported claims at render time**

Add `sanitize_public_content` before `word_count` and template replacement in `render_blog_html`. Remove a full enclosing sentence or list item when it contains one of the exact unsupported markers defined by the quality gate; do not mutate `posts.json`. Apply the same safe wording in templates: replace statistical, certification, health-outcome, and insurance assertions with non-numerical operational descriptions.

- [ ] **Step 5: Rebuild blog and generated pages**

Run: `python build_blogs.py`, `python build_local_pages.py`, and `python build_service_landings.py`.

Expected: each command completes, the public HTML has no unsupported marker, and `posts.json` has no diff.

- [ ] **Step 6: Run the quality gate**

Run: `node scripts/seo_quality_gate.mjs`

Expected: generated pages pass metadata, schema, breadcrumb, and unsupported-claim checks.

- [ ] **Step 7: Commit generated-page improvements**

```bash
git add blog_template.html local_template.html service_landing_template.html build_blogs.py blog areas landing-*.html
git commit -m "feat: complete generated SEO metadata"
```

### Task 4: Make hand-maintained pages evidence-first and performance-safe

**Files:**
- Modify: `index.html`
- Modify: `blog.html`
- Modify: `privacy.html`
- Modify: `landing-bigcleaning.html`
- Modify: `landing-maid.html`
- Modify: `landing-sangkan-office.html`
- Modify: `build_assets.py`
- Test: `scripts/seo_quality_gate.mjs`

**Interfaces:**
- `normalize_image_dimensions(html: str) -> str` adds safe intrinsic dimensions to non-decorative images missing them.
- `patch_root_html_files()` calls the normalizer after analytics patching.

- [ ] **Step 1: Add root-page failures to the quality gate**

Require all social metadata, valid JSON-LD, no forbidden GEO pins/unsupported claims, and dimensions on root page images. Require the home LCP image to carry `fetchpriority="high"` and an image preload link.

- [ ] **Step 2: Confirm the baseline fails**

Run: `node scripts/seo_quality_gate.mjs`

Expected: `index.html` fails for legacy location and unsupported claims; root pages fail missing social metadata or image-dimension checks.

- [ ] **Step 3: Update the home entity and trust copy**

Replace the homepage `LocalBusiness` graph with an `Organization` graph using only verified contact channels and service offers. Remove the generic Bangkok address, coordinates, and map link. Replace the certification/statistic block with a visible “แนวทางการให้บริการ” section that describes planning, appropriate equipment, scope confirmation, and post-service checks without named certifications, numerical performance, medical outcomes, or guarantees.

Add this preload directly before stylesheets, retaining the existing eager hero image:

```html
<link rel="preload" as="image" href="images/hero-cleaning.jpg" fetchpriority="high">
```

- [ ] **Step 4: Complete root-page social and navigation schema**

Add complete OG/Twitter metadata to `blog.html`, `privacy.html`, and the three hand-maintained landing pages. Add a `BreadcrumbList` to `blog.html`, privacy, and service landings. Keep privacy content indexable only if it remains a public policy page.

- [ ] **Step 5: Add safe image-dimension normalization**

In `build_assets.py`, implement a regex-based `normalize_image_dimensions` that skips images with `role="presentation"` or empty `alt`, preserves existing dimensions, and adds `width="1200" height="675"` to content images that lack both attributes. Call it for each root HTML file; use `width="180" height="80"` for the logo source path.

- [ ] **Step 6: Run the root build and check dimensions**

Run: `python build_assets.py` then `node scripts/seo_quality_gate.mjs`.

Expected: the gate reports no root metadata, unsupported-claim, LCP-preload, or image-dimension errors.

- [ ] **Step 7: Commit root-page cleanup**

```bash
git add index.html blog.html privacy.html landing-bigcleaning.html landing-maid.html landing-sangkan-office.html build_assets.py
git commit -m "feat: harden root SEO and trust content"
```

### Task 5: Rebuild, verify, and record the final state

**Files:**
- Modify: generated `blog/*.html`, `areas/*.html`, `landing-*.html`, `sitemap-pages.xml`, `sitemap-blog.xml`, `sitemap.xml`, `posts-index.json`
- Test: `scripts/seo_quality_gate.mjs`

**Interfaces:**
- `python build_site.py` produces the deployable static site.
- `node scripts/seo_quality_gate.mjs` is the required pre-deploy gate.

- [ ] **Step 1: Perform the full build**

Run: `python build_site.py`

Expected: blog, listing, area, service, sitemap, analytics, and redirect build steps complete without exceptions.

- [ ] **Step 2: Run the complete quality gate**

Run: `node scripts/seo_quality_gate.mjs`

Expected: `SEO/AIO/GEO quality gate passed for 99 indexable pages` and exit code `0`.

- [ ] **Step 3: Inspect the final diff**

Run: `git diff --check HEAD~4..HEAD` and `git status --short`.

Expected: no whitespace errors; generated files reflect only the revised templates and build output.

- [ ] **Step 4: Commit final generated artifacts**

```bash
git add blog areas landing-*.html sitemap.xml sitemap-pages.xml sitemap-blog.xml posts-index.json index.html blog.html privacy.html
git commit -m "build: refresh evidence-first SEO pages"
```

## Self-review

- Spec coverage: Task 1 enforces the quality contract; Task 2 removes fabricated GEO signals; Task 3 upgrades generated metadata/AIO; Task 4 fixes static pages and Core Web Vitals markup; Task 5 rebuilds and verifies every public artifact.
- Placeholder scan: no unassigned implementation steps, undecided data, or deferred fixes remain.
- Type consistency: every builder consumes JSON strings generated by `site_config.py`; the gate checks only final static HTML and sitemap artifacts.

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-13-seo-aio-geo-quality.md`.

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks.
2. **Inline Execution** — execute tasks in this session using `superpowers:executing-plans` with checkpoints.
