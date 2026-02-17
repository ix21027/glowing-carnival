package main

import (
	"fmt"
	"os"
	"time"

	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/devices"
	"github.com/go-rod/rod/lib/launcher"
	"github.com/go-rod/rod/lib/proto"
	"github.com/go-rod/stealth"
)

func main() {
	fmt.Println(">>> Запуск Go-Rod (Mobile Mode)...")

	// 1. Настройка браузера
	// ВАЖНО: Headless(false). Мы запускаем полноценный браузер,
	// чтобы Cloudflare не видел флага "HeadlessChrome".
	// На сервере это сработает благодаря Xvfb (см. yaml файл).
	u := launcher.New().
		Headless(false).
		NoSandbox(true).
		MustLaunch()

	browser := rod.New().ControlURL(u).MustConnect()
	defer browser.MustClose()

	// 2. Включаем режим невидимки (Stealth)
	page := stealth.MustPage(browser)

	// 3. Включаем эмуляцию iPhone
	// Это автоматически ставит нужный User-Agent, включает Touch Events
	// и меняет разрешение экрана.
	// Используем пресет iPhone X/13/14 (они похожи по отпечаткам)
	fmt.Println(">>> Активация эмуляции iPhone...")
	page.MustEmulate(devices.IPhoneX)

	// Если принципиально нужен именно твой User-Agent (iOS 18), 
	// раскомментируй строку ниже, но пресет devices.IPhoneX надежнее:
	// page.MustEval(`() => Object.defineProperty(navigator, 'userAgent', { get: () => 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/605.1.15' })`)

	// 4. Устанавливаем куки адреса (Винница, А. Первозванного 20)
	fmt.Println(">>> Установка кук адреса...")
	page.MustSetCookies(
		&proto.NetworkCookie{Name: "f_search_type", Value: "0", Domain: "voe.com.ua", Path: "/"},
		&proto.NetworkCookie{Name: "f_city_id", Value: "510100000", Domain: "voe.com.ua", Path: "/"},
		&proto.NetworkCookie{Name: "f_street_id", Value: "1664", Domain: "voe.com.ua", Path: "/"},
		&proto.NetworkCookie{Name: "f_house", Value: "20", Domain: "voe.com.ua", Path: "/"},
		&proto.NetworkCookie{Name: "f_house_id", Value: "48508", Domain: "voe.com.ua", Path: "/"},
		// URL-encoded значения
		&proto.NetworkCookie{Name: "f_city", Value: "%D0%BC..%20%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%20%28%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%B0%20%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2F%D0%9C.%D0%92%D1%96%D0%BD%D0%BD%D0%B8%D1%86%D1%8F%29", Domain: "voe.com.ua", Path: "/"},
		&proto.NetworkCookie{Name: "f_street", Value: "%D0%B2%D1%83%D0%BB%D0%B8%D1%86%D1%8F%20%D0%90%D0%BD%D0%B4%D1%80%D1%96%D1%8F%20%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%B7%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE", Domain: "voe.com.ua", Path: "/"},
	)

	// 5. Переход на сайт
	fmt.Println(">>> Переход на сайт...")
	page.MustNavigate("https://voe.com.ua/disconnection/detailed")

	// 6. Ожидание
	// Ждем стабилизации сети (пока Cloudflare перенаправит)
	// И даем лишние 10 секунд для надежности
	page.MustWaitStable()
	time.Sleep(10 * time.Second)

	title := page.MustInfo().Title
	fmt.Printf(">>> Текущий заголовок: %s\n", title)

	// 7. Сохранение результатов
	fmt.Println(">>> Делаю скриншот...")
	page.MustScreenshot("iphone_result.png")

	html := page.MustHTML()
	if len(html) > 0 {
		fmt.Println(">>> Сохраняю HTML...")
		os.WriteFile("schedule.html", []byte(html), 0644)
	}

	// Простая проверка успеха
	if page.MustHasR("div", "Черга") || page.MustHas("table") {
		fmt.Println(">>> УСПЕХ! График найден.")
	} else {
		fmt.Println(">>> График не найден. Проверь iphone_result.png")
	}
}
