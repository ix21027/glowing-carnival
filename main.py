import asyncio
import nodriver as uc
import time

# Твои куки для адреса (Винница, А. Первозванного 20)
COOKIES = [
    {'name': 'f_search_type', 'value': '0', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_city_id', 'value': '510100000', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street_id', 'value': '1664', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house', 'value': '20', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house_id', 'value': '48508', 'domain': 'voe.com.ua', 'path': '/'},
    # URL encoded значения для города и улицы
    {'name': 'f_city', 'value': '%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street', 'value': '%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE', 'domain': 'voe.com.ua', 'path': '/'}
]

async def main():
    print(">>> Запуск Nodriver...")
    
    # Запускаем браузер. 
    # ВАЖНО: headless=False, потому что мы используем виртуальный дисплей (Xvfb) в GitHub Actions.
    # Cloudflare гораздо меньше подозревает браузеры с видимым окном.
    browser = await uc.start(
        headless=False,
        browser_args=['--no-sandbox', '--window-size=1920,1080']
    )

    try:
        # Устанавливаем куки через CDP (Network domain)
        # Это нужно сделать до перехода на сайт, но nodriver требует активной вкладки
        print(">>> Установка кук адреса...")
        for cookie in COOKIES:
            # Nodriver требует await для каждой команды CDP
            await browser.connection.send("Network.setCookie", cookie)

        print(">>> Переход на сайт...")
        page = await browser.get("https://voe.com.ua/disconnection/detailed")

        # Ждем прохождения проверки Cloudflare
        # Nodriver делает это умнее, но добавим явное ожидание
        print(">>> Ожидание Cloudflare (15 сек)...")
        await page.sleep(15)

        # Проверяем заголовок или контент
        content = await page.get_content()
        
        if "Just a moment" in content or "Security" in content:
            print("!!! Все еще висит проверка. Жду еще 10 сек...")
            await page.sleep(10)
            content = await page.get_content()

        # Сохраняем скриншот для проверки
        print(">>> Сохраняю скриншот...")
        await page.save_screenshot("result.png")

        # Сохраняем HTML
        if "table" in content or "Черга" in content:
            print(">>> УСПЕХ! График найден.")
            with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print(">>> График не найден (возможно, не сработали куки адреса). HTML сохранен для анализа.")
            with open("debug_fail.html", "w", encoding="utf-8") as f:
                f.write(content)

    except Exception as e:
        print(f"!!! Ошибка: {e}")
    finally:
        browser.stop()

if __name__ == "__main__":
    # Nodriver асинхронный, запускаем через asyncio
    asyncio.run(main())
