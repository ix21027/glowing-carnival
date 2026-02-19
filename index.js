const { connect } = require("puppeteer-real-browser");
const fs = require('fs');

// Ваші налаштування (краще брати з env, але можна і тут для тесту)
const TG_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

const ACCOUNTS = ['400910046', '400720714'];

// --- ФУНКЦІЯ ВІДПРАВКИ В TELEGRAM ---
async function sendTelegramPhoto(caption, filePath) {
    if (!TG_TOKEN || !TG_CHAT_ID) {
        console.log("⚠️ Telegram токен або Chat ID не задані. Пропускаємо відправку.");
        return;
    }

    try {
        const formData = new FormData();
        formData.append('chat_id', TG_CHAT_ID);
        formData.append('caption', caption);
        // Читаємо файл і додаємо його у форму
        const fileBuffer = fs.readFileSync(filePath);
        const blob = new Blob([fileBuffer], { type: 'image/png' });
        formData.append('photo', blob, 'screenshot.png');

        const response = await fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendPhoto`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.ok) {
            console.log("✅ Фото успішно відправлено в Telegram!");
        } else {
            console.error("❌ Помилка Telegram API:", data.description);
        }
    } catch (error) {
        console.error("❌ Помилка при відправці в Telegram:", error.message);
    }
}

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (MONITORING + TELEGRAM) ===");

    const { browser, page } = await connect({
        headless: false,
        turnstile: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--window-size=1280,720"],
        connectOption: { defaultViewport: { width: 1280, height: 720 } }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';
        
        // Селектори
        const radioLabelSelector = "div.form-item.form__item.form__item--radio.form__item--search-type.form__item--radio--2 > label";
        const inputSelector = 'input[data-drupal-selector="edit-personal-account"]'; 
        const submitButtonSelector = '#edit-submit-detailed-search';
        const tableSelector = ".disconnection-detailed-table-container";

        for (const account of ACCOUNTS) {
            console.log(`\n--- Обробка рахунку: ${account} ---`);

            try {
                // 1. Навігація
                await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
                await new Promise(r => setTimeout(r, 13000));

                // 2. Клік радіо
                await page.waitForSelector(radioLabelSelector, { timeout: 10000 });
                await page.click(radioLabelSelector);
                
                // 3. Введення рахунку
                await page.waitForSelector(inputSelector, { timeout: 10000 });
                await page.click(inputSelector);
                
                await page.keyboard.down('Control');
                await page.keyboard.press('A');
                await page.keyboard.up('Control');
                await page.keyboard.press('Backspace');
                
                await page.type(inputSelector, account); // Прибрали delay для швидкості

                // 4. Пошук
                await page.click(submitButtonSelector);

                // 5. Очікування таблиці
                await page.waitForSelector(tableSelector, { timeout: 20000 });
                await new Promise(r => setTimeout(r, 1000));

                // === ПЕРЕВІРКА ЗМІН ===
                const currentText = await page.$eval(tableSelector, el => el.innerText.trim());
                
                const stateFile = `state_${account}.txt`;
                let previousText = "";

                if (fs.existsSync(stateFile)) {
                    previousText = fs.readFileSync(stateFile, 'utf8');
                }

                if (currentText !== previousText) {
                    console.log(`⚠️ УВАГА: РОЗКЛАД ЗМІНИВСЯ для ${account}!`);
                    
                    // Зберігаємо новий стан
                    fs.writeFileSync(stateFile, currentText);
                    
                    // Робимо скріншот
                    const element = await page.$(tableSelector);
                    const filename = `schedule_${account}_CHANGED.png`;
                    await element.screenshot({ path: filename });
                    console.log(`📸 Скріншот збережено: ${filename}`);

                    // === ВІДПРАВКА В TELEGRAM ===
                    const caption = `💡 Увага! Змінився графік для рахунку ${account}.\nДата: ${new Date().toLocaleString('uk-UA')}`;
                    await sendTelegramPhoto(caption, filename);

                } else {
                    console.log(`✅ Розклад без змін для ${account}.`);
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
