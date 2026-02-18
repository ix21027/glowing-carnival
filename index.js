const { connect } = require("puppeteer-real-browser");

// Данные ваших аккаунтов
const ACCOUNTS = [
    {
        id: 'account_1',
        personal_account: '400910046',
        eic: '62Z4291896444446'
    },
    {
        id: 'account_2',
        personal_account: '400720714',
        eic: '62Z0658084868027'
    }
];

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (2 АККАУНТА) ===");

    const { browser, page } = await connect({
        headless: false,
        turnstile: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        connectOption: { defaultViewport: null }
    });

    try {
        const url = 'https://voe.com.ua/disconnection/detailed';

        // Проходим по списку аккаунтов
        for (const acc of ACCOUNTS) {
            console.log(`\n--- Обработка аккаунта: ${acc.personal_account} ---`);

            // 1. Устанавливаем куки (они перезапишут предыдущие)
            const cookiesToSet = [
                { name: 'f_search_type', value: '2', domain: '.voe.com.ua' },
                { name: 'f_personal_account', value: acc.personal_account, domain: '.voe.com.ua' },
                { name: 'f_eic', value: acc.eic, domain: '.voe.com.ua' }
            ];

            // Если есть токен Cloudflare в секретах, добавляем его, чтобы не выкинуло
            if (process.env.CF_COOKIE) {
                cookiesToSet.push({
                    name: 'cf_clearance',
                    value: process.env.CF_COOKIE,
                    domain: '.voe.com.ua'
                });
            }

            await page.setCookie(...cookiesToSet);
            console.log("Куки обновлены.");

            // 2. Переходим на страницу (или обновляем её)
            // Использование goto каждый раз гарантирует, что сайт увидит новые куки
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

            // 3. Ждем загрузки и прохождения Cloudflare
            console.log("Ждем загрузку страницы...");
            // Пауза 7 секунд. Если сайт медленный, можно увеличить.
            await new Promise(r => setTimeout(r, 7000));

            // 4. Пытаемся нажать кнопку поиска, чтобы график точно обновился
            try {
                // Ждем кнопку поиска
                const searchBtnSelector = '#edit-submit-detailed-search';
                const btn = await page.$(searchBtnSelector);
                
                if (btn) {
                    console.log("Нажимаем 'Показать'...");
                    await btn.click();
                    // Ждем обновления таблицы после клика
                    await new Promise(r => setTimeout(r, 5000));
                } else {
                    console.log("Кнопка поиска не найдена, делаем скрин как есть.");
                }
            } catch (e) {
                console.log("Ошибка клика (не критично):", e.message);
            }

            // 5. Делаем скриншот
            const filename = `schedule_${acc.id}.png`;
            await page.screenshot({ path: filename, fullPage: true });
            console.log(`✅ Скриншот сохранен: ${filename}`);
        }

    } catch (e) {
        console.error("КРИТИЧЕСКАЯ ОШИБКА:", e);
        process.exit(1);
    } finally {
        await browser.close();
        console.log("Браузер закрыт.");
        process.exit(0);
    }
}

run();
