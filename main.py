from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os

def main():
    # Настройка браузера для работы в Docker/GitHub Actions
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--headless=new') # Важный режим, маскирующийся под обычный браузер
    co.set_argument('--disable-gpu')
    co.set_argument('--window-size=1920,1080')
    
    # Подмена User-Agent (на всякий случай)
    co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    page = ChromiumPage(co)
    
    print(">>> [1] Запускаю браузер...")

    try:
        # Переходим на сайт
        url = 'https://voe.com.ua/disconnection/detailed'
        page.get(url)
        
        print(">>> [2] Жду прохождения Cloudflare Challenge...")
        
        # Cloudflare обычно требует 3-5 секунд для редиректа.
        # DrissionPage не вылетает по таймауту, он ждет.
        time.sleep(8) 
        
        # Проверка: если мы все еще на заглушке Cloudflare
        if "Just a moment" in page.title or "Attention Required" in page.title:
            print("!!! Еще проверяют. Жду еще 10 секунд...")
            time.sleep(10)

        # Вывод заголовка страницы для отладки
        print(f">>> [3] Текущий заголовок: {page.title}")

        # Делаем скриншот того, что видит бот (для проверки)
        page.get_screenshot(path='.', name='page_view.png', full_page=True)
        
        # Сохраняем HTML код страницы
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(page.html)
            
        print(">>> [4] Успешно сохранено.")

    except Exception as e:
        print(f"!!! Ошибка: {e}")
        # Если упало, все равно пробуем сделать скриншот
        try:
            page.get_screenshot(path='.', name='error_view.png')
        except:
            pass
    finally:
        page.quit()

if __name__ == "__main__":
    main()
