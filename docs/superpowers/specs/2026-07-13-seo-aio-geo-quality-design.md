# SEO, AIO, and GEO quality design

## Goal

Raise the site's technical SEO quality and its usefulness to AI search systems without publishing unverified business facts. The site currently has verified contact channels, service descriptions, and editorial content, but it does not have a verified street address, local-office coordinates, certification identifiers, or evidence for historical performance claims.

## Decision

Use an evidence-first entity model:

- Keep the verified brand name, phone number, email address, LINE, Facebook, Messenger, service descriptions, and declared service areas.
- Model the company as an `Organization` and its offerings as `Service`. Do not model an unverified physical location as a `LocalBusiness` with a guessed address or map pin.
- Describe coverage with typed `areaServed` values only. Local pages are service-area pages, not claimed branch locations.
- Remove coordinate meta tags and generic Bangkok map links from generated pages.
- Remove or soften unverified numerical, certification, medical, insurance, and customer-volume claims. Do not add rating or review schema without authentic review data.

## Scope

1. Create reusable SEO helpers and entity data in the site configuration.
2. Update service, local-area, blog, home, privacy, and blog-index metadata so every indexable page has complete social metadata, Twitter cards, canonical URLs, and a breadcrumb where it is meaningful.
3. Improve JSON-LD to link pages to the same organization entity and use typed service areas.
4. Add image width and height defaults in generated content, preload the home LCP image, and introduce a modern image path for the hero when a local WebP asset is available.
5. Add a repository quality gate that checks indexable files for metadata, social tags, JSON-LD validity, image dimensions, canonical URLs, and forbidden fabricated GEO fields or legacy claims.

## Non-goals

- Do not invent an address, coordinates, Google Business Profile, certification number, customer review, rating, staff biography, or business statistic.
- Do not claim a separate branch or office in each service area.
- Do not assert that laboratory, regulatory, or health outcomes are proven without a source.

## Data flow

`site_config.py` is the source of truth for verified business identity and service areas. Build scripts consume it to render templates. Templates render complete metadata and linked JSON-LD. The quality gate validates the generated static site before deployment.

## Validation

- Rebuild all generated pages and sitemaps.
- Parse every indexable JSON-LD block as JSON.
- Require one title, description, canonical, H1, complete Open Graph set, Twitter card, and image dimensions on indexable pages.
- Reject coordinates, map pins, and deprecated geo-meta tags in service-area pages.
- Reject unsupported numerical/medical/certification claims introduced in templates or the home page.

## Risks and mitigation

The conservative cleanup can reduce marketing specificity where past content used unverified claims. The replacement wording preserves clear services, contact paths, and coverage while avoiding trust-damaging assertions. Verified facts can be added later only through the central configuration and evidence pages.
