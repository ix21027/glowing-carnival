const { connect } = require("puppeteer-real-browser");

const ACCOUNTS = ['400910046', '400720714'];

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (KEYBOARD NAVIGATION) ===");

    const { browser, page } = await connect({
        headless: false,
        turnstile: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        connectOption: { defaultViewport: null }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';
        const targetSelector = '.disconnection-detailed-table-container';

        for (const code of ACCOUNTS) {
            console.log(`\n--- Обробка рахунку: ${code} ---`);

            // 1. Перехід на сайт (або перезавантаження для скидання фокусу)
            // Це важливо, щоб "Tab x2" завжди спрацьовував однаково
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
            
            // Чекаємо трохи, щоб сайт провантажився і став активним
            await new Promise(r => setTimeout(r, 4000));

            // 2. Імітація: TAB -> TAB
            console.log("Натискаємо TAB x2...");
            await page.keyboard.press('Tab');
            await new Promise(r => setTimeout(r, 200)); // Невелика затримка як у людини
            await page.keyboard.press('Tab');
            await new Promise(r => setTimeout(r, 500));

            // 3. Вводимо код
            console.log(`Друкуємо код: ${code}`);
            // Про всяк випадок очищаємо поле (Ctrl+A -> Backspace), якщо там щось було
            await page.keyboard.down('Control');
            await page.keyboard.press('A');
            await page.keyboard.up('Control');
            await page.keyboard.press('Backspace');
            
            // Вводимо цифри
            await page.keyboard.type(code, { delay: 100 }); // delay 100мс імітує швидкість друку

            // 4. Натискаємо Enter
            console.log("Натискаємо Enter...");
            await page.keyboard.press('Enter');

            // 5. Чекаємо на появу таблиці з графіком
            try {
                console.log("Очікування таблиці...");
                // Чекаємо саме на контейнер таблиці
                await page.waitForSelector(targetSelector, { timeout: 15000 });
                
                // Даємо ще секунду, щоб стилі промалювалися
                await new Promise(r => setTimeout(r, 2000));

                // 6. Робимо скріншот ТІЛЬКИ ЕЛЕМЕНТА
                const element = await page.$(targetSelector);
                if (element) {
                    const filename = `schedule_${code}.png`;
                    await element.screenshot({ path: filename });
                    console.log(`✅ Скріншот елемента збережено: ${filename}`);
                } else {
                    console.error("Елемент знайдено, але не вдалося захопити.");
                }

            } catch (e) {
                console.error(`❌ Не вдалося знайти таблицю для коду ${code}. Можливо, сайт довго вантажиться або даних немає.`);
                // Робимо скрін всієї сторінки для налагодження
                await page.screenshot({ path: `error_${code}.png` });
            }
        }

    } catch (e) {
        console.error("КРИТИЧНА ПОМИЛКА:", e);
        process.exit(1);
    } finally {
        await browser.close();
        console.log("Роботу завершено.");
        process.exit(0);
    }
}

run();
