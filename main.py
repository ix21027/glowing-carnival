from DrissionPage import ChromiumPage, ChromiumOptions
import time
import sys

def main():
    # Настройка браузера
    co = ChromiumOptions()
    co.set_argument('--headless=new') # Новый режим, скрытный
    co.set_argument('--no-sandbox')
    # Маскируемся под Mac (часто вызывает меньше подозрений)
    co.set_user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    page = ChromiumPage(co)
    
    # URL графика
    url = 'https://voe.com.ua/disconnection/detailed'

    print(">>> [1] Настраиваю адрес (Винница, А. Первозванного 20)...")
    
    # Подставляем твои куки ПЕРЕД загрузкой страницы.
    # DrissionPage позволяет это делать для домена заранее.
    cookies = [
        {'name': 'f_search_type', 'value': '0', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_city_id', 'value': '510100000', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_street_id', 'value': '1664', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_house', 'value': '20', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_house_id', 'value': '48508', 'domain': '.voe.com.ua', 'path': '/'},
        # URL-encoded строки лучше передавать как есть, браузер разберется
        {'name': 'f_city', 'value': '%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29', 'domain': '.voe.com.ua', 'path': '/'},
        {'name': 'f_street', 'value': '%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE', 'domain': '.voe.com.ua', 'path': '/'}
    ]
    
    # Применяем куки
    page.set.cookies(cookies)

    try:
        print(">>> [2] Захожу на сайт...")
        page.get(url)
        
        # Самый важный момент: ждем, пока Cloudflare пропустит.
        # Если IP чистый (через WARP), это займет 3-5 секунд.
        print(">>> [3] Жду прохождения защиты (до 15 сек)...")
        time.sleep(5)
        
        # Если все еще висит проверка - ждем еще
        if "Just a moment" in page.title or "Security" in page.title:
            print(">>> Еще проверяют... Жду...")
            time.sleep(10)
        
        print(f">>> [4] Заголовок страницы: {page.title}")

        # Проверяем, загрузилась ли таблица с очередями
        # Ищем текст "Черга" или структуру таблицы
        if page.ele('text:Черга') or page.ele('tag:table'):
            print(">>> УСПЕХ! График найден.")
            
            # Сохраняем скриншот для подтверждения
            page.get_screenshot(path='.', name='schedule_success.png', full_page=True)
            
            # Сохраняем HTML (потом распарсишь его BeautifulSoup)
            with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(page.html)
        else:
            print("!!! Страница открылась, но графика нет. Возможно, куки адреса не сработали.")
            page.get_screenshot(path='.', name='error_no_table.png')

    except Exception as e:
        print(f"!!! Критическая ошибка: {e}")
        page.get_screenshot(path='.', name='fatal_error.png')
        sys.exit(1)
    finally:
        page.quit()

if __name__ == "__main__":
    main()
