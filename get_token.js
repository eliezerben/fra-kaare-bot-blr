const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    // Go to bmm and login
    await page.goto('https://bmm.brunstad.org', { waitUntil: 'networkidle0' });
    await page.type('[name=email]', 'eliezerben96@gmail.com');
    await page.type('[name=password]', 'Feloship1@portal');
    await page.screenshot({path: './test1.png'});
    await page.click('[name=submit]');
    // Wait until bmm page is fully loaded and token data is set in localStorage
    await page.waitForSelector('.bmm-latest');
    let token_data_str = null;
    let retry = true;
    while (retry) {
        console.log('Waiting for token to be set.')
        token_data_str = await page.evaluate("localStorage.getItem('oidc')")
        if (!token_data_str) {
            await page.waitForTimeout(500);
            continue;
        }
        retry = false
    }
    token_data = JSON.parse(token_data_str)
    console.log(token_data.access_token)
    await browser.close();
})();
