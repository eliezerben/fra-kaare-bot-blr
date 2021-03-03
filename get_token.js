const puppeteer = require('puppeteer');

(async () => {

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    // Go to bmm and login
    console.error('Waiting for sign in page to load.');
    await page.goto('https://bmm.brunstad.org');
    await page.waitForSelector('[name=submit]', { visible: true });
    await page.type('[name=email]', process.env.BMM_USERNAME);
    await page.type('[name=password]', process.env.BMM_PASSWORD);
    await page.click('[name=submit]');
    // Wait until bmm page is fully loaded and token data is set in localStorage
    console.error('Waiting for BMM to load.');
    await page.waitForSelector('.bmm-latest', { visible: true });
    let token_data_str = null;
    const timeout = 30000, interval = 200;
    let elapsedTime = 0;
    const intervalId = setInterval(async () => {
        console.error('Waiting for token to be set.');
        token_data_str = await page.evaluate("localStorage.getItem('oidc')");
        if (token_data_str || elapsedTime >= timeout) {
            token_data = JSON.parse(token_data_str)
            // Print actual access_token to STDOUT
            console.log(token_data.access_token)
            clearInterval(intervalId);
            await browser.close();
        }
        elapsedTime += interval
    }, interval);

})();
