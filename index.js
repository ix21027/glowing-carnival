const { connect } = require("puppeteer-real-browser");
const fs = require('fs');

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

        for (const account of ACCOUNTS) {
            console.log(`\n--- Обробка рахунку: ${account} ---`);

            try {
                // 1. Навігація всередині циклу (це важливо для очищення стану!)
                // Це також допомагає уникнути плутанини, якщо сайт "зависне" на попередньому запиті
                await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
                
                // Чекаємо трохи прогрузки скриптів
                await new Promise(r => setTimeout(r, 3000));

await page.screenshot({ path: `error1_${account}.png` });
                // 2. Клік радіо
                await page.waitForSelector(radioLabelSelector, { timeout: 10000 });
                await page.click(radioLabelSelector);

                // 3. Чекаємо появи поля вводу (воно може з'являтися з затримкою після кліку)
                await page.waitForSelector(inputSelector, { timeout: 10000 });
                
await page.screenshot({ path: `error2_${account}.png` });
                // Фокус та очищення
                await page.click(inputSelector);
                await page.keyboard.down('Control');
                await page.keyboard.press('A');
                await page.keyboard.up('Control');
                await page.keyboard.press('Backspace');
                
                // Введення
                await page.type(inputSelector, account, { delay: 100 });
await page.screenshot({ path: `error3_${account}.png` });
                // 4. Пошук (Enter)
                await page.keyboard.press('Enter');
await page.screenshot({ path: `error4_${account}.png` });
                // 5. Очікування таблиці
                // Тут ми збільшуємо час очікування, бо сайт може думати
                await page.waitForSelector(tableSelector, { timeout: 20000 });
                await new Promise(r => setTimeout(r, 3000)); // Даємо час JS оновити дані всередині таблиці
await page.screenshot({ path: `error5_${account}.png` });
                // === ЛОГІКА ОТРИМАННЯ ТЕКСТУ ===
                const currentText = await page.$eval(tableSelector, el => el.innerText.trim());
                
                const stateFile = `state_${account}.txt`;
                let previousText = "";

                if (fs.existsSync(stateFile)) {
                    previousText = fs.readFileSync(stateFile, 'utf8');
                }
await page.screenshot({ path: `error_${account}.png` });
                // Порівняння
                if (currentText !== previousText) {
                    console.log(`⚠️ УВАГА: РОЗКЛАД ЗМІНИВСЯ для ${account}!`);
                    
                    fs.writeFileSync(stateFile, currentText);
                    
                    const element = await page.$(tableSelector);
                    const filename = `schedule_${account}_CHANGED.png`;
                    await element.screenshot({ path: filename });
                    console.log(`📸 Скріншот оновлено: ${filename}`);
                } else {
                    console.log(`✅ Розклад без змін для ${account}.`);
                }

            } catch (innerError) {
                console.error(`❌ Помилка для рахунку ${account}:`, innerError.message);
                // Робимо скріншот помилки для налагодження
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
