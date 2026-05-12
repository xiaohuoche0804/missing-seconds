const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Go to the new chapter page
  await page.goto('https://fanqienovel.com/main/writer/7637711913522056254/publish/7638435626483712574?enter_from=newchapter_0', { waitUntil: 'networkidle' });

  // Wait for page to load
  await page.waitForTimeout(2000);

  // Get page title
  console.log('Title:', await page.title());

  // Check URL
  console.log('URL:', page.url());

  // Try to find chapter number input
  const inputs = await page.$$('input');
  console.log('Number of inputs:', inputs.length);

  for (let i = 0; i < inputs.length; i++) {
    const box = await inputs[i].boundingBox();
    const value = await inputs[i].inputValue();
    console.log(`Input ${i}: value="${value}", box=`, JSON.stringify(box));
  }

  await browser.close();
})();