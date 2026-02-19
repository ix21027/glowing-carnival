const { connect } = require("puppeteer-real-browser");

// Ваші особові рахунки
const ACCOUNTS = ['400910046', '400720714'];

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (DRUPAL SELECTOR) ===");

    const { browser, page } = await connect({
        headless: false,
        turnstile: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        connectOption: { defaultViewport: null }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';
        
        // 1. Селектор радіо-кнопки (Тип пошуку: Особовий рахунок)
        // Шукаємо label, який відповідає за вибір особового рахунку
        const radioLabelSelector = "div.form-item.form__item.form__item--radio.form__item--search-type.form__item--radio--2 > label";
        
        // 2. Селектор поля вводу (Беремо з вашого HTML)
        // Використовуємо атрибут data-drupal-selector, бо ID динамічний
        const inputSelector = 'input[data-drupal-selector="edit-personal-account"]';
        
        // 3. Селектор кнопки "Пошук"
        const submitButtonSelector = '#edit-submit-detailed-search';
        
        // 4. Селектор таблиці результатів
        const tableSelector = ".disconnection-detailed-table-container";

        for (const account of ACCOUNTS) {
            console.log(`\n--- Обробка рахунку: ${account} ---`);

            try {
                // А. Переходимо на сайт
                await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
                await new Promise(r => setTimeout(r, 3000));

                // Б. Клікаємо на тип пошуку "Особовий рахунок"
                console.log("Клікаємо на радіо-кнопку...");
                await page.waitForSelector(radioLabelSelector, { timeout: 10000 });
                await page.click(radioLabelSelector);

                // В. Чекаємо, поки з'явиться потрібний інпут
                // Сайт може трохи "подумати" перед тим як підмінити поле
                console.log("Чекаємо на поле вводу рахунку...");
                await page.waitForSelector(inputSelector, { timeout: 10000 });
                
                // Г. Вводимо дані
                console.log(`Вводимо рахунок: ${account}`);
                await page.click(inputSelector); // Фокус на полі
                
                // Очищення поля (про всяк випадок)
                await page.keyboard.down('Control');
                await page.keyboard.press('A');
                await page.keyboard.up('Control');
                await page.keyboard.press('Backspace');
                
                // Введення цифр
                await page.type(inputSelector, account, { delay: 100 });

                // Д. Натискаємо кнопку пошуку
                console.log("Натискаємо кнопку 'Пошук'...");
                await page.click(submitButtonSelector);

                // Е. Чекаємо результатів
                console.log("Очікування таблиці...");
                await page.waitForSelector(tableSelector, { timeout: 20000 });
                await new Promise(r => setTimeout(r, 1000));

                // Є. Робимо скріншот елемента
                const element = await page.$(tableSelector);
                if (element) {
                    const filename = `schedule_${account}.png`;
                    await element.screenshot({ path: filename });
                    console.log(`✅ Скріншот збережено: ${filename}`);
                }

            } catch (innerError) {
                console.error(`❌ Помилка для рахунку ${account}:`, innerError.message);
                // Робимо скрін помилки
                await page.screenshot({ path: `error_${account}.png` });
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
