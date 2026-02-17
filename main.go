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
