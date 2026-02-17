from DrissionPage import ChromiumPage, ChromiumOptions
from pyvirtualdisplay import Display
import time
import random

def main():
    # 1. Запускаем виртуальный дисплей (обман системы, будто есть монитор)
    print(">>> Запускаю виртуальный дисплей...")
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    # 2. Настройка браузера
    co = ChromiumOptions()
    # ВАЖНО: Мы НЕ включаем --headless, так как у нас есть виртуальный дисплей
    co.set_argument('--no-sandbox')
    co.set_argument('--window-size=1920,1080')
    # Реалистичный User Agent
    co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    page = ChromiumPage(co)
    
    try:
        print(">>> Переход на сайт...")
        page.get('https://voe.com.ua/disconnection/detailed')
        
        # Ждем загрузки проверки Cloudflare
        time.sleep(5)
        
        # 3. Эмуляция человека: Двигаем мышкой, чтобы пройти проверку
        if "Just a moment" in page.title or "Security" in page.title:
            print(">>> Вижу проверку Cloudflare. Эмулирую движения мыши...")
            
            # Двигаем мышь в случайные координаты (как человек)
            for _ in range(5):
                x = random.randint(100, 700)
                y = random.randint(100, 500)
                page.actions.move_to((x, y), duration=random.uniform(0.5, 1.5))
            
            # Ждем, пока сайт пустит
            time.sleep(10)

        print(f">>> Заголовок страницы: {page.title}")

        # Делаем скриншот результата
        page.get_screenshot(path='.', name='result.png', full_page=True)
        
        # Сохраняем HTML
        with open("schedule.html", "w", encoding="utf-8") as f:
            f.write(page.html)

    except Exception as e:
        print(f"!!! Ошибка: {e}")
    finally:
        page.quit()
        display.stop()

if __name__ == "__main__":
    main()
