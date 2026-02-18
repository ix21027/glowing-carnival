from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import datetime

url = "https://voe.com.ua/disconnection/detailed"

with sync_playwright() as pw:
    # Можно добавить прокси (см. ниже)
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    )
    
    page = context.new_page()
    stealth_sync(page)                    # ← главное для обхода Cloudflare
    
    print("Открываем страницу...")
    page.goto(url, wait_until="networkidle", timeout=60000)
    
    # Ждём загрузки графика (можно уточнить селектор после инспекции)
    page.wait_for_timeout(15000)          # 15 секунд обычно хватает
    
    # Скриншот всей страницы или только области графика
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"voe-graph-{timestamp}.png"
    
    page.screenshot(path=filename, full_page=True)
    print(f"Скриншот сохранён: {filename}")
    
    browser.close()