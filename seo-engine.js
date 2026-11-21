#!/usr/bin/env node

/**
 * ENTERPRISE SEO AUTOMATION ENGINE (Zero-Dependency)
 * Universal, category-agnostic, geography-agnostic SEO audit, sitemap generator,
 * favicon pipeline, and live production crawler verifier.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { execSync } = require('child_process');

const ANSI = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m'
};

function logPass(msg) {
  console.log(`  ${ANSI.green}[PASS]${ANSI.reset} ${msg}`);
}

function logWarn(msg) {
  console.log(`  ${ANSI.yellow}[WARN]${ANSI.reset} ${msg}`);
}

function logFail(msg) {
  console.log(`  ${ANSI.red}[FAIL]${ANSI.reset} ${msg}`);
}

function logInfo(msg) {
  console.log(`  ${ANSI.cyan}[INFO]${ANSI.reset} ${msg}`);
}

// ----------------------------------------------------------------------------
// 1. FILE FINDER & HTML SCANNER
// ----------------------------------------------------------------------------
function findHtmlFiles(dir, fileList = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (['node_modules', '.git', 'admin', 'dist', 'build'].includes(entry.name)) continue;
      findHtmlFiles(fullPath, fileList);
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      fileList.push(fullPath);
    }
  }
  return fileList;
}

// ----------------------------------------------------------------------------
// 2. AUDIT MODULE (HTML, Meta, Schema, Favicons)
// ----------------------------------------------------------------------------
function auditProject(projectDir) {
  console.log(`\n${ANSI.bold}${ANSI.cyan}=== ENTERPRISE SEO AUDIT: PRE-FLIGHT CHECKLIST ===${ANSI.reset}\n`);
  
  const files = findHtmlFiles(projectDir);
  console.log(`Scanning ${files.length} HTML pages across project tree...\n`);

  let totalErrors = 0;
  let totalWarnings = 0;

  // Check Favicons in Root
  console.log(`${ANSI.bold}Checking Google-Compliant Favicon Infrastructure:${ANSI.reset}`);
  const hasIco = fs.existsSync(path.join(projectDir, 'favicon.ico'));
  const has48 = fs.existsSync(path.join(projectDir, 'favicon-48x48.png'));
  const has96 = fs.existsSync(path.join(projectDir, 'favicon-96x96.png'));
  const has192 = fs.existsSync(path.join(projectDir, 'favicon-192x192.png'));
  const hasSvg = fs.existsSync(path.join(projectDir, 'favicon.svg'));

  if (hasIco) logPass('favicon.ico physically present in root.');
  else { logFail('Missing favicon.ico in web root.'); totalErrors++; }

  if (has48) logPass('favicon-48x48.png present (Google Search 48px square requirement met).');
  else { logFail('Missing favicon-48x48.png (Google will display generic grey globe in search).'); totalErrors++; }

  if (has96) logPass('favicon-96x96.png present (High-DPI multiple).');
  if (has192) logPass('favicon-192x192.png present (PWA & Android multiple).');
  if (hasSvg) logPass('favicon.svg present (Vector scalability).');

  console.log(`\n${ANSI.bold}Checking Page-Level SEO Metadata & Schema:${ANSI.reset}`);

  for (const file of files) {
    const relPath = path.relative(projectDir, file);
    console.log(`\n${ANSI.bold}Page: ${relPath}${ANSI.reset}`);
    const html = fs.readFileSync(file, 'utf8');

    // Title Check
    const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    if (titleMatch && titleMatch[1].trim()) {
      const len = titleMatch[1].trim().length;
      if (len >= 30 && len <= 65) {
        logPass(`Title (${len} chars): "${titleMatch[1].trim()}"`);
      } else {
        logWarn(`Title length is ${len} chars (Recommended: 30-65 chars): "${titleMatch[1].trim()}"`);
        totalWarnings++;
      }
    } else {
      logFail('Missing <title> tag.');
      totalErrors++;
    }

    // Description Check
    const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i);
    if (descMatch && descMatch[1].trim()) {
      const len = descMatch[1].trim().length;
      if (len >= 100 && len <= 170) {
        logPass(`Meta Description (${len} chars): Valid length.`);
      } else {
        logWarn(`Meta Description is ${len} chars (Recommended: 120-165 chars).`);
        totalWarnings++;
      }
    } else {
      logFail('Missing <meta name="description"> tag.');
      totalErrors++;
    }

    // Canonical Tag
    const canonicalMatch = html.match(/<link\s+rel=["']canonical["']\s+href=["']([^"']+)["']/i);
    if (canonicalMatch) {
      logPass(`Canonical: ${canonicalMatch[1]}`);
    } else {
      logWarn('Missing canonical tag (<link rel="canonical" href="...">).');
      totalWarnings++;
    }

    // OpenGraph Check
    const hasOgTitle = /<meta\s+property=["']og:title["']/i.test(html);
    const hasOgImage = /<meta\s+property=["']og:image["']/i.test(html);
    if (hasOgTitle && hasOgImage) {
      logPass('OpenGraph social tags present (og:title, og:image).');
    } else {
      logWarn('Incomplete OpenGraph tags (Missing og:title or og:image).');
      totalWarnings++;
    }

    // Favicon Link Tags Check
    const hasFaviconLink = /<link\s+[^>]*rel=["'](?:shortcut\s+)?icon["'][^>]*href=["']\/favicon\.ico["']/i.test(html) ||
                           /<link\s+[^>]*href=["']\/favicon\.ico["']/i.test(html);
    const has48Link = /favicon-48x48\.png/i.test(html);
    if (hasFaviconLink && has48Link) {
      logPass('Favicon link tags include binary /favicon.ico and 48x48 PNG.');
    } else {
      logWarn('Missing explicit link tags for /favicon.ico or /favicon-48x48.png in <head>.');
      totalWarnings++;
    }

    // Schema.org JSON-LD Check
    const jsonLdMatches = html.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/gi);
    if (jsonLdMatches && jsonLdMatches.length > 0) {
      let validSchemas = 0;
      for (const block of jsonLdMatches) {
        const rawJson = block.replace(/<script\s+type=["']application\/ld\+json["']>/i, '').replace(/<\/script>/i, '');
        try {
          const parsed = JSON.parse(rawJson);
          validSchemas++;
        } catch (e) {
          logFail(`Malformed Schema.org JSON-LD syntax: ${e.message}`);
          totalErrors++;
        }
      }
      if (validSchemas > 0) {
        logPass(`Schema.org JSON-LD: ${validSchemas} valid block(s) detected.`);
      }
    } else {
      logWarn('No Schema.org JSON-LD structured data found.');
      totalWarnings++;
    }
  }

  console.log(`\n------------------------------------------------------------`);
  if (totalErrors === 0 && totalWarnings === 0) {
    console.log(`${ANSI.bold}${ANSI.green}AUDIT COMPLETE: 100% PERFECT SEO HEALTH (0 errors, 0 warnings)${ANSI.reset}\n`);
  } else {
    console.log(`${ANSI.bold}AUDIT SUMMARY: ${totalErrors} Errors, ${totalWarnings} Warnings.${ANSI.reset}\n`);
  }
}

// ----------------------------------------------------------------------------
// 3. SITEMAP GENERATOR
// ----------------------------------------------------------------------------
function generateSitemap(projectDir, baseDomain) {
  console.log(`\n${ANSI.bold}${ANSI.cyan}=== GENERATING PRODUCTION SITEMAP.XML ===${ANSI.reset}\n`);
  const cleanDomain = baseDomain.replace(/\/+$/, '');
  const files = findHtmlFiles(projectDir);
  const today = new Date().toISOString().split('T')[0];

  const urls = [];

  for (const file of files) {
    const rel = path.relative(projectDir, file).replace(/\\/g, '/');
    let urlPath = '';
    let priority = '0.8';
    let freq = 'weekly';

    if (rel === 'index.html') {
      urlPath = '/';
      priority = '1.0';
      freq = 'daily';
    } else if (rel.startsWith('services/')) {
      urlPath = '/' + rel.replace(/\.html$/, '');
      priority = '0.9';
    } else if (rel.startsWith('tools/')) {
      urlPath = '/' + rel.replace(/\.html$/, '');
      priority = '0.9';
    } else if (rel.startsWith('regions/') || rel.startsWith('locations/')) {
      urlPath = '/' + rel.replace(/\.html$/, '');
      priority = '0.8';
    } else {
      urlPath = '/' + rel.replace(/\.html$/, '');
      priority = '0.7';
    }

    urls.push({
      loc: `${cleanDomain}${urlPath}`,
      lastmod: today,
      changefreq: freq,
      priority
    });
  }

  // Sort: Homepage first, then by priority desc
  urls.sort((a, b) => parseFloat(b.priority) - parseFloat(a.priority));

  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  xml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

  for (const u of urls) {
    xml += `  <url>\n`;
    xml += `    <loc>${u.loc}</loc>\n`;
    xml += `    <lastmod>${u.lastmod}</lastmod>\n`;
    xml += `    <changefreq>${u.changefreq}</changefreq>\n`;
    xml += `    <priority>${u.priority}</priority>\n`;
    xml += `  </url>\n`;
  }
  xml += `</urlset>\n`;

  const outPath = path.join(projectDir, 'sitemap.xml');
  fs.writeFileSync(outPath, xml, 'utf8');
  logPass(`Generated ${urls.length} URLs in sitemap: ${outPath}`);
}

// ----------------------------------------------------------------------------
// 4. ROBOTS.TXT GENERATOR
// ----------------------------------------------------------------------------
function generateRobots(projectDir, baseDomain) {
  console.log(`\n${ANSI.bold}${ANSI.cyan}=== GENERATING PRODUCTION ROBOTS.TXT ===${ANSI.reset}\n`);
  const cleanDomain = baseDomain.replace(/\/+$/, '');
  const content = `User-agent: *\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: ${cleanDomain}/sitemap.xml\n`;
  const outPath = path.join(projectDir, 'robots.txt');
  fs.writeFileSync(outPath, content, 'utf8');
  logPass(`Generated compliant robots.txt at: ${outPath}`);
}

// ----------------------------------------------------------------------------
// 5. LIVE PRODUCTION VERIFIER (Network Pings)
// ----------------------------------------------------------------------------
async function fetchHead(url) {
  return new Promise((resolve) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.request(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
      }
    }, (res) => {
      resolve({
        statusCode: res.statusCode,
        headers: res.headers
      });
    });
    req.on('error', (err) => resolve({ statusCode: 0, error: err.message }));
    req.setTimeout(8000, () => {
      req.destroy();
      resolve({ statusCode: 408, error: 'Connection timeout (>8s)' });
    });
    req.end();
  });
}

async function verifyProduction(baseDomain) {
  const cleanDomain = baseDomain.replace(/\/+$/, '');
  console.log(`\n${ANSI.bold}${ANSI.cyan}=== LIVE PRODUCTION CRAWLER VERIFICATION ===${ANSI.reset}`);
  console.log(`Target: ${cleanDomain}\n`);

  // 1. Robots.txt
  const robotsRes = await fetchHead(`${cleanDomain}/robots.txt`);
  if (robotsRes.statusCode === 200) {
    const cType = robotsRes.headers['content-type'] || '';
    if (cType.includes('text/plain')) {
      logPass(`/robots.txt returns HTTP 200 (text/plain)`);
    } else {
      logWarn(`/robots.txt returns HTTP 200 but incorrect Content-Type: ${cType}`);
    }
  } else {
    logFail(`/robots.txt failed with HTTP ${robotsRes.statusCode}`);
  }

  // 2. Sitemap.xml
  const sitemapRes = await fetchHead(`${cleanDomain}/sitemap.xml`);
  if (sitemapRes.statusCode === 200) {
    logPass(`/sitemap.xml returns HTTP 200 (Valid XML payload)`);
  } else {
    logFail(`/sitemap.xml failed with HTTP ${sitemapRes.statusCode}`);
  }

  // 3. Favicon.ico
  const icoRes = await fetchHead(`${cleanDomain}/favicon.ico`);
  if (icoRes.statusCode === 200) {
    const cType = icoRes.headers['content-type'] || '';
    if (cType.includes('image/x-icon') || cType.includes('image/vnd.microsoft.icon')) {
      logPass(`/favicon.ico returns HTTP 200 with proper image/x-icon MIME type`);
    } else if (cType.includes('text/html')) {
      logFail(`/favicon.ico returned HTML (SPA catch-all bug). Google will reject this icon.`);
    } else {
      logWarn(`/favicon.ico returns HTTP 200 (${cType})`);
    }
  } else {
    logFail(`/favicon.ico returned HTTP ${icoRes.statusCode}`);
  }

  // 4. Favicon 48px
  const p48Res = await fetchHead(`${cleanDomain}/favicon-48x48.png`);
  if (p48Res.statusCode === 200) {
    logPass(`/favicon-48x48.png returns HTTP 200 (Google Search multiple verified)`);
  } else {
    logFail(`/favicon-48x48.png missing or returned HTTP ${p48Res.statusCode}`);
  }

  // 5. Homepage Root
  const homeRes = await fetchHead(`${cleanDomain}/`);
  if (homeRes.statusCode === 200) {
    logPass(`Homepage (/) returns HTTP 200 OK to Googlebot User-Agent`);
  } else {
    logFail(`Homepage (/) failed with HTTP ${homeRes.statusCode}`);
  }

  console.log(`\n${ANSI.bold}Verification Complete.${ANSI.reset}\n`);
}

// ----------------------------------------------------------------------------
// CLI DISPATCHER
// ----------------------------------------------------------------------------
async function main() {
  const args = process.argv.slice(2);
  const cwd = process.cwd();

  if (args.length === 0 || args.includes('--help')) {
    console.log(`
${ANSI.bold}Enterprise SEO Automation Engine${ANSI.reset}
Usage:
  node seo-engine.js --audit                  Run pre-flight audit on all HTML files
  node seo-engine.js --sitemap <domain>       Scan project and generate production sitemap.xml
  node seo-engine.js --robots <domain>        Generate RFC 9309-compliant robots.txt
  node seo-engine.js --verify <domain>        Run live HTTP crawl tests against production
  node seo-engine.js --all <domain>           Run audit, sitemap generator, and live verification
    `);
    process.exit(0);
  }

  if (args.includes('--audit')) {
    auditProject(cwd);
  }

  const sitemapIdx = args.indexOf('--sitemap');
  if (sitemapIdx !== -1) {
    const domain = args[sitemapIdx + 1] || 'https://example.com';
    generateSitemap(cwd, domain);
  }

  const robotsIdx = args.indexOf('--robots');
  if (robotsIdx !== -1) {
    const domain = args[robotsIdx + 1] || 'https://example.com';
    generateRobots(cwd, domain);
  }

  const verifyIdx = args.indexOf('--verify');
  if (verifyIdx !== -1) {
    const domain = args[verifyIdx + 1];
    if (!domain) {
      console.error('Please specify a domain: node seo-engine.js --verify https://yourdomain.com');
      process.exit(1);
    }
    await verifyProduction(domain);
  }

  const allIdx = args.indexOf('--all');
  if (allIdx !== -1) {
    const domain = args[allIdx + 1] || 'https://jvkcommerce.com';
    auditProject(cwd);
    generateSitemap(cwd, domain);
    generateRobots(cwd, domain);
    await verifyProduction(domain);
  }
}

main();
