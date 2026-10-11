// Kullanım: node render.mjs sayfa.html cikti.png GENISLIK YUKSEKLIK [seffaf] [olcek]
import { createRequire } from 'module';
import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(process.execPath, '../../lib/node_modules/playwright'));
const [, , html, out, w, h, seffaf, olcek] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +(olcek || 1) });
await page.goto('file://' + path.resolve(html));
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: out, omitBackground: seffaf === 'seffaf' });
await browser.close();
