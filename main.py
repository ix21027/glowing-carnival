from curl_cffi import requests
from bs4 import BeautifulSoup
import time
import os
import sys

def main():
    url = "https://voe.com.ua/disconnection/detailed"
    
    # 1. Твои "координаты". Сайт сразу поймет, какой дом нужен.
    cookies = {
        'f_search_type': '0',
        'f_city_id': '510100000',
        'f_street_id': '1664',
        'f_house': '20',
        'f_house_id': '48508',
        'f_city': '%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29',
        'f_street': '%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%B8%D0%B3%D0%BE'
    }

    # 2. (ОПЦИЯ) Если есть cf_clearance из секретов GitHub — добавляем его
    # Это "золотой ключ", если автоматика не сработает
    cf_clearance = os.environ.get('CF_COOKIE')
    if cf_clearance:
        print(">>> Использую сохраненный cf_clearance!")
        cookies['cf_clearance'] = cf_clearance

    print(f">>> Запрос данных для дома ID: {cookies['f_house_id']}...")

    try:
        # МАГИЯ ЗДЕСЬ: impersonate="chrome124"
        # Мы говорим серверу: "Я Chrome версии 124, вот мои шифры".
        response = requests.get(
            url, 
            cookies=cookies,
            impersonate="chrome124", 
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://voe.com.ua/"
            },
            timeout=30
        )

        # Проверка на Cloudflare
        if response.status_code == 403 or "Just a moment" in response.text:
            print("!!! Cloudflare заблокировал запрос (403/Challenge).")
            # Сохраняем, чтобы ты увидел, что пошло не так
            with open("error_cf.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            sys.exit(1)

        # Успех?
        print(f">>> Ответ получен. Код: {response.status_code}")
        
        # Парсим HTML, ищем таблицу
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Обычно график лежит в таблице или div с классом
        table = soup.find('table')
        if table:
            print(">>> УРА! Таблица графика найдена.")
            with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(str(table))
        elif "Черга" in response.text:
             print(">>> Таблицы нет, но есть слово 'Черга'. Сохраняю HTML.")
             with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(response.text)
        else:
            print(">>> Страница загрузилась, но графика нет. Проверь куки адреса.")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)

    except Exception as e:
        print(f"!!! Ошибка запроса: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
