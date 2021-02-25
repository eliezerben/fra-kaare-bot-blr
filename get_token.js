const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto('https://bmm.brunstad.org', { waitUntil: 'networkidle0' });
    await page.type('[name=email]', process.env.BMM_USERNAME)
    await page.type('[name=password]', process.env.BMM_PASSWORD)

    await Promise.all([
        await page.click('[name=submit]'),
        await page.waitForNavigation({ waitUntil: 'networkidle0' })
    ]);
    token_data_str = await page.evaluate("localStorage.getItem('oidc')")
    token_data = JSON.parse(token_data_str)
    console.log(token_data.access_token)
    await browser.close();
})();
