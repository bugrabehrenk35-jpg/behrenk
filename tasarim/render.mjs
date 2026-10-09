// Kullanım: node render.mjs sayfa.html cikti.png GENISLIK YUKSEKLIK [seffaf]
import { createRequire } from 'module';
import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(process.execPath, '../../lib/node_modules/playwright'));
const [, , html, out, w, h, seffaf] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
await page.goto('file://' + path.resolve(html));
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: out, omitBackground: seffaf === 'seffaf' });
await browser.close();
