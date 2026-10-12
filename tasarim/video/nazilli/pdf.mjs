// Kullanım: node pdf.mjs sayfa.html cikti.pdf
import path from 'path';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const [, , html, out] = process.argv;
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://' + path.resolve(html)); await p.evaluate(() => document.fonts.ready);
await p.pdf({ path: out, format: 'A4', printBackground: true, margin: { top: '16mm', bottom: '16mm', left: '16mm', right: '16mm' } });
await b.close();
