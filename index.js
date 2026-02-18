const { connect } = require("puppeteer-real-browser");
const fs = require('fs');

async function run() {
    console.log("=== ЗАПУСК СКРИПТА ===");
    
    // Подключаемся. Важно: headless: false + Xvfb в GitHub Actions
    const { browser, page } = await connect({
        headless: false, 
        turnstile: true,
        args: [
            "--no-sandbox", 
            "--disable-setuid-sandbox", 
            "--start-maximized"
        ],
        connectOption: {
            defaultViewport: null
        }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';
        console.log(`Переход на: ${url}`);

        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

        console.log("Страница загружена. Ожидание стабилизации (Cloudflare)...");
        
        // Ждем 10 секунд, чтобы все проверки прошли и JS отработал
        await new Promise(r => setTimeout(r, 10000));

        // Проверка: загрузился ли контент (например, футер)
        try {
            await page.waitForSelector('footer', { timeout: 10000 });
            console.log("Элемент footer найден. Сайт доступен.");
        } catch (e) {
            console.log("WARN: Футер не найден, возможно капча или ошибка загрузки.");
        }

        // Делаем скриншот
        await page.screenshot({ path: 'screenshot.png', fullPage: true });
        console.log("Скриншот сделан: screenshot.png");

    } catch (e) {
        console.error("ОШИБКА:", e);
        // Делаем скриншот ошибки, если возможно
        if (page) await page.screenshot({ path: 'error_screen.png' });
        process.exit(1);
    } finally {
        await browser.close();
        console.log("Браузер закрыт.");
        process.exit(0);
    }
}

run();
