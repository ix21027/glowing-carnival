import asyncio
import nodriver as uc
import json

# Твой User-Agent
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/605.1.15"

# Куки адреса (Винница, А. Первозванного 20)
COOKIES = [
    {'name': 'f_search_type', 'value': '0', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_city_id', 'value': '510100000', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street_id', 'value': '1664', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house', 'value': '20', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house_id', 'value': '48508', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_city', 'value': '%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street', 'value': '%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE', 'domain': 'voe.com.ua', 'path': '/'}
]

async def enable_mobile_emulation(tab):
    """Принудительно включаем мобильный режим через CDP"""
    
    # 1. Переопределяем User-Agent на уровне сети
    await tab.send("Network.setUserAgentOverride", {
        "userAgent": USER_AGENT,
        "platform": "iPhone",
        "acceptLanguage": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    })

    # 2. Переопределяем параметры экрана (Эмуляция дисплея iPhone)
    await tab.send("Emulation.setDeviceMetricsOverride", {
        "width": 390,
        "height": 844,
        "deviceScaleFactor": 3, # Retina дисплей
        "mobile": True,         # Самый важный флаг для Cloudflare
        "screenOrientation": {"type": "portraitPrimary", "angle": 0}
    })

    # 3. Включаем сенсорный ввод (Touch Events)
    await tab.send("Emulation.setTouchEmulationEnabled", {
        "enabled": True,
        "maxTouchPoints": 5
    })

async def main():
    print(">>> Запуск Nodriver (iPhone Mode)...")
    
    # Запускаем браузер с размером окна как у телефона
    # headless=False важно, так как мы используем Xvfb
    browser = await uc.start(
        headless=False,
        browser_args=[
            '--no-sandbox', 
            f'--user-agent={USER_AGENT}',
            '--window-size=390,844', # Размер окна браузера снаружи
            '--disable-gpu' # Иногда помогает стабильности в Docker
        ]
    )

    try:
        # Получаем текущую вкладку
        tab = await browser.get("about:blank")
        
        # Включаем полную эмуляцию iPhone
        await enable_mobile_emulation(tab)
        
        # Устанавливаем куки
        print(">>> Установка кук адреса...")
        for cookie in COOKIES:
            await tab.send("Network.setCookie", cookie)

        print(">>> Переход на сайт...")
        await tab.get("https://voe.com.ua/disconnection/detailed")

        # Ждем прохождения Cloudflare
        print(">>> Ожидание (15 сек)...")
        await tab.sleep(15)

        # Сохраняем скриншот (чтобы увидеть, мобильная ли версия)
        await tab.save_screenshot("iphone_view.png")

        content = await tab.get_content()
        
        if "table" in content or "Черга" in content:
            print(">>> УСПЕХ! График найден.")
            with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(content)
        elif "Just a moment" in content:
            print("!!! Cloudflare все еще проверяет. Пробуем подождать еще...")
            await tab.sleep(10)
            await tab.save_screenshot("retry_view.png")
            
            # Вторая попытка прочитать контент
            content = await tab.get_content()
            with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print(">>> Странный результат. Сохраняю HTML для отладки.")
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(content)

    except Exception as e:
        print(f"!!! Ошибка: {e}")
    finally:
        browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
