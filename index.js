const { connect } = require("puppeteer-real-browser");

// Список рахунків для перевірки
const ACCOUNTS = ['400910046', '400720714'];

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (CLICK + KEYBOARD) ===");

    const { browser, page } = await connect({
        headless: false,
        turnstile: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        connectOption: { defaultViewport: null }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';
        // Селектор радіо-кнопки (пошук по рахунку)
        const radioLabelSelector = "div.form-item.form__item.form__item--radio.form__item--search-type.form__item--radio--2 > label";
        // Селектор таблиці з результатами
        const tableSelector = ".disconnection-detailed-table-container";

        for (const account of ACCOUNTS) {
            console.log(`\n--- Обробка рахунку: ${account} ---`);

            try {
                // 1. Переходимо на сайт
                await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
                
                // Чекаємо завантаження
                console.log("Чекаємо завантаження сайту...");
                await new Promise(r => setTimeout(r, 5000));

                // 2. Клік по вибору типу пошуку
                console.log("Клікаємо на тип пошуку...");
                await page.waitForSelector(radioLabelSelector, { timeout: 10000 });
                await page.click(radioLabelSelector);
                
                // Пауза, щоб сайт відреагував на клік
                await new Promise(r => setTimeout(r, 2000));

                // 3. Імітація: TAB -> TAB (перехід до поля вводу)
                console.log("Натискаємо TAB x2...");
                await page.keyboard.press('Tab');
                await new Promise(r => setTimeout(r, 200));
                await page.keyboard.press('Tab');
                await new Promise(r => setTimeout(r, 200));

                // 4. Вводимо номер рахунку
                console.log(`Вводимо рахунок: ${account}`);
                // Страховка: очищаємо поле перед введенням
                await page.keyboard.down('Control');
                await page.keyboard.press('A');
                await page.keyboard.up('Control');
                await page.keyboard.press('Backspace');
                
                // Друкуємо цифри
                await page.keyboard.type(account, { delay: 100 });

                // 5. Натискаємо Enter
                console.log("Натискаємо Enter...");
                await page.keyboard.press('Enter');

                // 6. Чекаємо появи таблиці (графіка)
                console.log("Очікування таблиці результатів...");
                // Збільшив таймаут до 20 сек, бо сайт може думати довго
                await page.waitForSelector(tableSelector, { timeout: 20000 });
                
                // Даємо ще секунду на промальовування
                await new Promise(r => setTimeout(r, 1000));

                // 7. Робимо скріншот ТІЛЬКИ ЕЛЕМЕНТА
                const element = await page.$(tableSelector);
                if (element) {
                    const filename = `schedule_${account}.png`;
                    await element.screenshot({ path: filename });
                    console.log(`✅ Скріншот збережено: ${filename}`);
                } else {
                    console.error("Елемент знайдено, але виникла помилка при знімку.");
                }

            } catch (innerError) {
                console.error(`❌ Помилка для рахунку ${account}:`, innerError.message);
                // Робимо скрін помилки, щоб зрозуміти, що пішло не так
                await page.screenshot({ path: `error_${account}.png` });
            }
        }

    } catch (e) {
        console.error("КРИТИЧНА ПОМИЛКА:", e);
        process.exit(1);
    } finally {
        await browser.close();
        console.log("Браузер закрито.");
        process.exit(0);
    }
}

run();
