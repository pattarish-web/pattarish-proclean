import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const SITE_URL = 'https://www.sangkanclean.com';
const EXCLUDED_DIRS = new Set(['.git', '.agents', '.cursor', 'docs', 'marketing', 'ops', 'posts', 'seo']);
const EXCLUDED_FILES = new Set(['blog_template.html', 'local_template.html', 'service_landing_template.html', 'latest_posts.html']);
const REQUIRED_META = [
  ['title', /<title\b/i],
  ['description', /<meta\b[^>]*\bname=["']description["']/i],
  ['canonical', /<link\b[^>]*\brel=["']canonical["']/i],
  ['og:title', /<meta\b[^>]*\bproperty=["']og:title["']/i],
  ['og:description', /<meta\b[^>]*\bproperty=["']og:description["']/i],
  ['og:image', /<meta\b[^>]*\bproperty=["']og:image["']/i],
  ['og:url', /<meta\b[^>]*\bproperty=["']og:url["']/i],
  ['og:type', /<meta\b[^>]*\bproperty=["']og:type["']/i],
  ['twitter:card', /<meta\b[^>]*\bname=["']twitter:card["']/i],
];
const UNSUPPORTED_CLAIMS = [
  'SGS ISO',
  'BSI ISO',
  'GHPs Standard',
  'Green Industry',
  '5,000',
  '100%',
  '99.9%',
  '30 ปี',
];

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    if (entry.isDirectory()) {
      return EXCLUDED_DIRS.has(entry.name) ? [] : walk(path.join(dir, entry.name));
    }
    return entry.name.endsWith('.html') ? [path.join(dir, entry.name)] : [];
  });
}

function relative(file) {
  return path.relative(ROOT, file).split(path.sep).join('/');
}

function isIndexable(file, html) {
  const name = path.basename(file);
  return !EXCLUDED_FILES.has(name)
    && !name.startsWith('google')
    && !/<meta\b[^>]*\bname=["']robots["'][^>]*\bnoindex\b/i.test(html);
}

function jsonLdBlocks(html) {
  return [...html.matchAll(/<script\b[^>]*\btype=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];
}

function pageHasOrganizationSchema(html) {
  return html.includes(`${SITE_URL}/#organization`)
    || /"@type"\s*:\s*"Organization"/.test(html);
}

function checkSitemaps(errors, indexable) {
  for (const sitemap of ['sitemap-pages.xml', 'sitemap-blog.xml']) {
    const file = path.join(ROOT, sitemap);
    if (!fs.existsSync(file)) {
      errors.push(`${sitemap}: missing sitemap`);
      continue;
    }
    const xml = fs.readFileSync(file, 'utf8');
    for (const match of xml.matchAll(/<loc>([^<]+)<\/loc>/g)) {
      const url = match[1];
      if (!url.startsWith(`${SITE_URL}/`)) {
        errors.push(`${sitemap}: unexpected URL ${url}`);
        continue;
      }
      const decodedPath = decodeURIComponent(url.slice(SITE_URL.length + 1));
      const target = decodedPath || 'index.html';
      const absolute = path.join(ROOT, target);
      if (!fs.existsSync(absolute)) {
        errors.push(`${sitemap}: missing target ${target}`);
      } else if (!indexable.has(relative(absolute))) {
        errors.push(`${sitemap}: non-indexable target ${target}`);
      }
    }
  }
}

function checkPage(file, html, errors) {
  const rel = relative(file);
  for (const [name, pattern] of REQUIRED_META) {
    if (!pattern.test(html)) errors.push(`${rel}: missing ${name}`);
  }

  if ((html.match(/<h1\b/gi) ?? []).length !== 1) {
    errors.push(`${rel}: requires exactly one h1`);
  }

  if (/<meta\b[^>]*\bname=["']geo\./i.test(html)
    || /\b(?:GeoCoordinates|hasMap)\b/.test(html)) {
    errors.push(`${rel}: contains an unverified geographic pin`);
  }

  for (const marker of UNSUPPORTED_CLAIMS) {
    if (html.includes(marker)) errors.push(`${rel}: contains unsupported claim “${marker}”`);
  }

  for (const tag of html.matchAll(/<img\b[^>]*>/gi)) {
    const image = tag[0];
    if (/\b(?:role=["']presentation["']|alt=["']["'])/i.test(image)) continue;
    if (!/\bwidth=["'][^"']+["']/i.test(image) || !/\bheight=["'][^"']+["']/i.test(image)) {
      errors.push(`${rel}: image missing width/height`);
      break;
    }
  }

  for (const block of jsonLdBlocks(html)) {
    try {
      JSON.parse(block[1]);
    } catch (error) {
      errors.push(`${rel}: invalid JSON-LD (${error.message})`);
    }
  }

  if ((rel.startsWith('areas/') || rel.startsWith('blog/') || rel.startsWith('landing-'))
    && !/BreadcrumbList/.test(html)) {
    errors.push(`${rel}: missing BreadcrumbList`);
  }

  if ((rel.startsWith('areas/') || rel.startsWith('blog/') || rel.startsWith('landing-'))
    && !pageHasOrganizationSchema(html)) {
    errors.push(`${rel}: missing shared organization entity`);
  }
}

const errors = [];
const indexable = new Set();
for (const file of walk(ROOT)) {
  const html = fs.readFileSync(file, 'utf8');
  if (!isIndexable(file, html)) continue;
  indexable.add(relative(file));
  checkPage(file, html, errors);
}
checkSitemaps(errors, indexable);

if (errors.length) {
  console.error(`SEO/AIO/GEO quality gate failed with ${errors.length} error(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  console.log(`SEO/AIO/GEO quality gate passed for ${indexable.size} indexable pages.`);
}
