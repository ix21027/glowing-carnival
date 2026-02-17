from DrissionPage import ChromiumPage, ChromiumOptions
import time

def main():
    co = ChromiumOptions()
    
    # 1. Основные настройки для скрытности
    co.set_argument('--no-sandbox')
    co.set_argument('--headless=new') # Скрытый режим (но для телефона можно и убрать)
    
    # --- НАСТРОЙКИ ПОД ТЕЛЕФОН (Pixel 7 Pro) ---
    
    # А. Правильный User-Agent (Android 14)
    mobile_ua = "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.143 Mobile Safari/537.36"
    co.set_user_agent(mobile_ua)

    # Б. Эмуляция размера экрана телефона
    co.set_argument('--window-size=412,915')
    
    # В. Включаем поддержку сенсорного экрана (Touch Events)
    # Это критично! У телефонов нет мышки, у них тачскрин.
    co.set_argument('--touch-events=enabled') 

    # Запускаем
    page = ChromiumPage(co)

    # Г. Магия CDP (Chrome DevTools Protocol)
    # Мы принудительно говорим браузеру: "Ты - мобильный телефон"
    # Это меняет заголовки Sec-CH-UA-Mobile на ?1 (True)
    page.run_cdp('Emulation.setUserAgentOverride', 
        userAgent=mobile_ua,
        platform='Android',
        mobile=True,
        deviceScaleFactor=3,
        screenOrientation={'type': 'portraitPrimary', 'angle': 0}
    )


    # --- ТВОИ КУКИ АДРЕСА ---
    # Чтобы сразу увидеть график для твоего дома
    cookies = [
        {'name': 'f_house_id', 'value': '48508', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_city_id', 'value': '510100000', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_house', 'value': '20', 'domain': '.voe.com.ua', 'path': '/'}
    ]
    page.set.cookies(cookies)

    try:
        print(">>> Захожу как Android (Pixel 7)...")
        page.get('https://voe.com.ua/disconnection/detailed')

        # Проверка защиты
        time.sleep(5)
        
        # Если нужно кликнуть (эмуляция пальца)
        # page.tap() - это именно тап пальцем, а не клик мышкой
        
        if "Just a moment" in page.title:
            print(">>> Жду прохождения проверки...")
            time.sleep(10)

        print(f">>> Заголовок: {page.title}")
        
        # Делаем скриншот, чтобы убедиться, что сайт открылся в мобильной верстке
        page.get_screenshot(path='.', name='mobile_view.png', full_page=True)
        print(">>> Скриншот сохранен (mobile_view.png)")
        
        # Сохраняем HTML
        with open("mobile_schedule.html", "w", encoding="utf-8") as f:
            f.write(page.html)

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        page.quit()

if __name__ == "__main__":
    main()
