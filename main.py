from playwright.sync_api import sync_playwright
import time
import random

# Твои данные адреса (Винница, А. Первозванного 20)
COOKIES = [
    {'name': 'f_search_type', 'value': '0', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_city_id', 'value': '510100000', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street_id', 'value': '1664', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house', 'value': '20', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_house_id', 'value': '48508', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_city', 'value': '%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29', 'domain': 'voe.com.ua', 'path': '/'},
    {'name': 'f_street', 'value': '%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE', 'domain': 'voe.com.ua', 'path': '/'}
]

def human_mouse_move(page):
    """Имитация движений человека (дрожание курсора)"""
    for _ in range(10):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y, steps=10)
        time.sleep(random.uniform(0.1, 0.3))

def main():
    with sync_playwright() as p:
        print(">>> Запуск Firefox...")
        
        # Запускаем Firefox.
        # headless=False важно, так как мы используем виртуальный экран в GitHub Actions
        browser = p.firefox.launch(
            headless=False, 
            args=['--width=1920', '--height=1080']
        )
        
        # Создаем контекст с настройками "как у человека"
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            locale='uk-UA',
            timezone_id='Europe/Kiev'
        )
        
        # Добавляем куки адреса сразу
        context.add_cookies(COOKIES)
        
        page = context.new_page()

        print(">>> Переход на сайт...")
        try:
            page.goto("https://voe.com.ua/disconnection/detailed", timeout=60000)
            
            print(">>> Ждем Cloudflare...")
            # Даем время на загрузку проверки
            page.wait_for_timeout(5000)
            
            # Двигаем мышкой, чтобы пройти "невидимую капчу"
            print(">>> Эмуляция активности...")
            human_mouse_move(page)
            
            # Если есть чекбокс капчи, пробуем кликнуть (иногда помогает)
            try:
                # Ищем iframe капчи
                iframe = page.frame_locator("iframe[src*='challenges']").first
                if iframe:
                    box = iframe.locator("input[type='checkbox']")
                    if box.is_visible():
                        box.click()
            except:
                pass

            # Ждем долго (иногда Firefox проходит проверку медленнее)
            print(">>> Ожидание результата (до 20 сек)...")
            page.wait_for_timeout(20000)

            # Проверка
            title = page.title()
            print(f">>> Заголовок: {title}")
            
            # Делаем скриншот
            page.screenshot(path="firefox_result.png", full_page=True)
            
            content = page.content()
            if "table" in content or "Черга" in content:
                print(">>> УСПЕХ! График найден.")
                with open("schedule.html", "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                print(">>> График не найден. Смотри скриншот.")
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"!!! Ошибка: {e}")
            page.screenshot(path="error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
