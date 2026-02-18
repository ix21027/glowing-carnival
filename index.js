const { connect } = require("puppeteer-real-browser");

async function run() {
    console.log("=== ЗАПУСК СКРИПТА (С КУКИ) ===");
    
    // Подключаемся. Опции настроены для обхода Cloudflare и работы в GitHub Actions
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
        console.log("Установка куки для формы поиска...");

        // === БЛОК УСТАНОВКИ ВАШИХ КУКИ ===
        // Эти куки заставят сайт сразу показать нужный адрес/счет
        await page.setCookie(
            {
                name: 'f_search_type',
                value: '2', // Тип поиска (видимо, по EIC или счету)
                domain: '.voe.com.ua'
            },
            {
                name: 'f_personal_account',
                value: '400910046', // Ваш лицевой счет
                domain: '.voe.com.ua'
            },
            {
                name: 'f_eic',
                value: '62Z4291896444446', // Ваш EIC код
                domain: '.voe.com.ua'
            },
            // Добавляем cf_clearance, если он передан через секреты GitHub
            process.env.CF_COOKIE ? {
                name: 'cf_clearance',
                value: process.env.CF_COOKIE,
                domain: '.voe.com.ua'
            } : null
        ).then(() => {
            // Фильтруем null, если CF_COOKIE не задан
            console.log("Куки успешно установлены.");
        });

        const url = 'https://voe.com.ua/disconnection/detailed';
        console.log(`Переход на: ${url}`);

        // Переходим на сайт. Куки отправятся вместе с запросом.
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

        console.log("Страница загружена. Ждем обработки Cloudflare и скриптов сайта...");
        
        // Пауза 10-15 секунд для прохождения проверок и рендеринга таблицы
        await new Promise(r => setTimeout(r, 15000));

        // Дополнительная попытка нажать кнопку "Показать", если таблица не появилась сама
        // (Иногда куки подставляют данные, но кнопку нужно нажать скриптом)
        try {
            // Ищем кнопку поиска (селектор может отличаться, это примерный)
            const searchButton = await page.$('#edit-submit-detailed-search');
            if (searchButton) {
                console.log("Нажимаем кнопку поиска для обновления данных...");
                await searchButton.click();
                await new Promise(r => setTimeout(r, 5000)); // Ждем обновления таблицы
            }
        } catch (e) {
            console.log("Кнопка поиска не найдена или уже нажата.");
        }

        // Делаем скриншот
        const filename = 'schedule_result.png';
        await page.screenshot({ path: filename, fullPage: true });
        console.log(`Скриншот сохранен: ${filename}`);

    } catch (e) {
        console.error("КРИТИЧЕСКАЯ ОШИБКА:", e);
        if (page) await page.screenshot({ path: 'error_debug.png' });
        process.exit(1);
    } finally {
        await browser.close();
        console.log("Браузер закрыт.");
        process.exit(0);
    }
}

run();
