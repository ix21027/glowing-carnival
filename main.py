from DrissionPage import ChromiumPage, ChromiumOptions
import time
import sys

# Твоя полная строка куки (я вставил её сюда)
RAW_COOKIES = "f_search_type = 0;f_city = %D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F;cf_chl_rc_ni = 12;f_search_type = 0;f_city = %D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29;f_city_id = 510100000;f_street = %D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE;f_street_id = 1664;f_house = 20;f_house_id = 48508;_ga = GA1.3.1585069075.1771367448;_gid = GA1.3.814630124.1771367448;_gat = 1;cf_clearance = 0MX.80IKYdhLvdfheTnN7BcKKvVhdcEh7Yb0BHaqFzM-1771372423-1.2.1.1-oALSfxHnZXq7KJteUrkkfVyRNJ6Fq5uSmb1c31s3nBoqKfUOTeszu7kKfAM3NN8ZaLjkAXFmuzIbSLqgQ0gmTRWrbTvmrJD2rUgi6X1cia0aDMa6YLPbnl.F7Q6YroJOsH2.ChH9XwpTaFuiWxHpi9hd1R7lyb6UE8SnrWNkbjKha0qreciWuiHwo3hLi.GzUXsIuR2RQG6AAeX2SbTgCq.NJLtTilsx0efUd_WQeRHzdTnrjd2M32ridup1_Wl8"

def load_cookies(page, raw_cookie_string):
    """Парсит строку куки и устанавливает их в браузер"""
    cookie_list = []
    # Разбиваем по точке с запятой
    for item in raw_cookie_string.split(';'):
        if '=' in item:
            # Разбиваем только по первому знаку равно
            name, value = item.strip().split('=', 1)
            cookie_list.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.voe.com.ua',
                'path': '/'
            })
    
    if cookie_list:
        print(f">>> Загружаю {len(cookie_list)} куки (включая cf_clearance)...")
        page.set.cookies(cookie_list)

def main():
    co = ChromiumOptions()
    co.set_argument('--headless=new')
    co.set_argument('--no-sandbox')
    # Важно: User-Agent должен быть похож на тот, с которого ты скопировал куки (Windows Chrome)
    co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    page = ChromiumPage(co)

    # 1. Сразу применяем твои куки
    load_cookies(page, RAW_COOKIES)

    try:
        print(">>> Переход на сайт...")
        page.get('https://voe.com.ua/disconnection/detailed')
        
        # cf_clearance должна сработать мгновенно
        time.sleep(5)

        # 2. Проверка
        if "Just a moment" in page.title:
            print("!!! Cloudflare все еще думает. Возможно, User-Agent не совпал с кукой.")
            page.get_screenshot(path='.', name='challenge.png')
            time.sleep(5)
        
        # Проверяем наличие таблицы или слова "Черга"
        if "table" in page.html or "Черга" in page.html:
            print(">>> УСПЕХ! График найден (ул. А. Первозванного 20).")
            
            # Сохраняем скриншот
            page.get_screenshot(path='.', name='schedule.png', full_page=True)
            
            # Сохраняем HTML
            with open("schedule.html", "w", encoding="utf-8") as f:
                f.write(page.html)
        else:
            print(">>> Страница загрузилась, но графика нет. Скриншот сохранен.")
            page.get_screenshot(path='.', name='error.png', full_page=True)
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(page.html)

    except Exception as e:
        print(f"!!! Ошибка: {e}")
    finally:
        page.quit()

if __name__ == "__main__":
    main()
