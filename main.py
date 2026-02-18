from playwright.sync_api import sync_playwright
import time

# Твои куки адреса (Винница, А. Первозванного 20)
COOKIES = [
    {'name': 'f_search_type', 'value': '0', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_city_id', 'value': '510100000', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street_id', 'value': '1664', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house', 'value': '20', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house_id', 'value': '48508', 'domain': 'voe.com.ua', 'path': '/'},
    # URL-encoded строки
    {'name': 'f_city', 'value': '%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street', 'value': '%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE', 'domain': 'voe.com.ua', 'path': '/'}
]

def main():
    print(">>> Подключаюсь к Browserless (ws://localhost:3000)...")
    
    with sync_playwright() as p:
        # Подключаемся к запущенному Docker-контейнеру
        # ВАЖНО: Мы передаем аргументы для Stealth-режима прямо в URL подключения или через args
        browser = p.chromium.connect_over_cdp("ws://localhost:3000")
        
        # Создаем контекст (профиль)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Устанавливаем куки
        context.add_cookies(COOKIES)
        
        page = context.new_page()

        print(">>> Переход на сайт...")
        try:
            page.goto("https://voe.com.ua/disconnection/detailed", timeout=60000)
            
            print(">>> Ждем Cloudflare (10 сек)...")
            page.wait_for_timeout(10000)
            
            # Проверка контента
            content = page.content()
            
            # Делаем скриншот результата
            page.screenshot(path="result.png", full_page=True)
            
            if "table" in content or "Черга" in content:
                print(">>> УСПЕХ! График найден.")
                with open("schedule.html", "w", encoding="utf-8") as f:
                    f.write(content)
            elif "Just a moment" in content:
                print("!!! Cloudflare еще думает. Пробую подождать еще...")
                page.wait_for_timeout(10000)
                page.screenshot(path="retry.png")
            else:
                print(">>> График не найден. Скриншот сохранен.")
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"!!! Ошибка: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
