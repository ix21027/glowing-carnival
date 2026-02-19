const { connect } = require("puppeteer-real-browser");
const fs = require('fs'); // Модуль для роботи з файлами

const ACCOUNTS = ['400910046', '400720714'];

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (ПЕРЕВІРКА ЗМІН) ===");

    const { browser, page } = await connect({
        headless: false,
        turnstile: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        connectOption: { defaultViewport: null }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';
        
        // Селектори
        const radioLabelSelector = "div.form-item.form__item.form__item--radio.form__item--search-type.form__item--radio--2 > label";
        const inputSelector = 'input[data-drupal-selector="edit-personal-account"]'; 
        const tableSelector = ".disconnection-detailed-table-container";

        // 1. Навігація
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await new Promise(r => setTimeout(r, 3000));

        // 2. Клік радіо
        await page.waitForSelector(radioLabelSelector, { timeout: 10000 });
        await page.click(radioLabelSelector);
                
        
        for (const account of ACCOUNTS) {
            console.log(`\n--- Обробка рахунку: ${account} ---`);

            try {
                
                // 3. Введення рахунку
                await page.waitForSelector(inputSelector, { timeout: 10000 });
                await page.click(inputSelector);
                
                await page.keyboard.down('Control');
                await page.keyboard.press('A');
                await page.keyboard.up('Control');
                await page.keyboard.press('Backspace');
                
                await page.type(inputSelector, account, { delay: 100 });

                // 4. Пошук
                await page.keyboard.press('Enter');

                // 5. Очікування таблиці
                await page.waitForSelector(tableSelector, { timeout: 20000 });
                await new Promise(r => setTimeout(r, 5000));

                // === НОВА ЛОГІКА: ОТРИМАННЯ ТЕКСТУ ===
                // Отримуємо "чистий" текст з таблиці для порівняння
                const currentText = await page.$eval(tableSelector, el => el.innerText.trim());
                
                // Ім'я файлу для збереження стану
                const stateFile = `state_${account}.txt`;
                let previousText = "";

                // Читаємо попередній стан, якщо файл існує
                if (fs.existsSync(stateFile)) {
                    previousText = fs.readFileSync(stateFile, 'utf8');
                }

                if (currentText !== previousText) {
                    console.log(`⚠️ УВАГА: РОЗКЛАД ЗМІНИВСЯ для ${account}!`);
                    
                    // Зберігаємо новий стан у файл
                    fs.writeFileSync(stateFile, currentText);
                    
                    // Робимо скріншот (тільки якщо змінився або вперше)
                    const element = await page.$(tableSelector);
                    const filename = `schedule_${account}_CHANGED.png`;
                    await element.screenshot({ path: filename });
                    console.log(`📸 Скріншот оновлено: ${filename}`);

                } else {
                    console.log(`✅ Розклад без змін для ${account}.`);
                    // Можна не робити скріншот, щоб не засмічувати артефакти,
                    // або робити його з іншим ім'ям.
                }

            } catch (innerError) {
                console.error(`❌ Помилка для рахунку ${account}:`, innerError.message);
                await page.screenshot({ path: `error_${account}.png` });
            }
        }

    } catch (e) {
        console.error("КРИТИЧНА ПОМИЛКА:", e);
        process.exit(1);
    } finally {
        await browser.close();
        process.exit(0);
    }
}

run();
