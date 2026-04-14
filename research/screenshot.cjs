const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

const HTML_FILE = path.resolve('/home/kai/.openclaw/workspace/research/xiaohongshu-cards.html');
const OUTPUT_DIR = '/home/kai/.openclaw/workspace/research/cards';
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const CHROMIUM = '/home/kai/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome';

(async () => {
  const browser = await chromium.launch({ 
    executablePath: CHROMIUM,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1440 });

  await page.goto(`file://${HTML_FILE}`, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);

  const cards = await page.$$('.card');
  console.log(`Found ${cards.length} cards`);

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    await card.scrollIntoViewIfNeeded();
    await page.waitForTimeout(800);
    await card.screenshot({
      path: path.join(OUTPUT_DIR, `card-${String(i + 1).padStart(2, '0')}.png`),
      type: 'png',
    });
    console.log(`✅ card-${String(i + 1).padStart(2, '0')}.png`);
  }

  await browser.close();
  console.log('Done!');
})();
