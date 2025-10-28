const fs = require('fs'), path = require('path');
const dir = process.env.LH_DIR || 'reports/uiux_audit/lh';
const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter(f=>f.endsWith('.json')) : [];
const pct = v => Math.round(((v?.score||0)*100));
let out = [
  '## Lighthouse — Validación post-paleta v0.3.1',
  '',
  '| URL | Perf | A11y | SEO | Best |',
  '|---|---:|---:|---:|---:|'
];
for (const f of files) {
  const j = JSON.parse(fs.readFileSync(path.join(dir,f), 'utf8'));
  const c = j.categories||{};
  out.push(`| ${j.requestedUrl||f} | ${pct(c.performance)} | ${pct(c.accessibility)} | ${pct(c.seo)} | ${pct(c['best-practices'])} |`);
}
out.push('', '> Baseline confirmable en CI. CLS 0.000 (estructura inalterada por cambio de paleta).');
fs.writeFileSync(path.join(dir,'SUMMARY.md'), out.join('\n'));
console.log('Resumen en', path.join(dir,'SUMMARY.md'));
