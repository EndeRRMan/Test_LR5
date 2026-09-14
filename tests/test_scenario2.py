from pathlib import Path

from playwright.sync_api import sync_playwright


def test_rutube_search_headless():
    artifacts = Path("artifacts")
    artifacts.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1920, "height": 1080}
        )

        # 1. Открываем RUTUBE
        page.goto(
            "https://rutube.ru/",
            wait_until="domcontentloaded",
            timeout=30000
        )

        # 2. Ищем видео
        search = page.get_by_placeholder("Поиск")
        search.fill("Лунтик")
        search.press("Enter")

        # 3. Ждём результаты поиска
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # 4. Берём первое видимое видео из выдачи
        first_video = page.locator(
            'a[href^="/video/"]:visible'
        ).first

        first_video.wait_for(
            state="visible",
            timeout=20000
        )

        # Получаем ссылку первого видео
        href = first_video.get_attribute("href")
        assert href is not None

        # 5. Переходим на страницу видео напрямую
        page.goto(
            f"https://rutube.ru{href}",
            wait_until="domcontentloaded",
            timeout=30000
        )

        # 6. Проверяем, что открылась страница видео
        assert "/video/" in page.url

        # 7. Сохраняем скриншот
        page.screenshot(
            path="artifacts/scenario2.png",
            full_page=True
        )

        # 8. Сохраняем HTML страницы
        Path("artifacts/scenario2.html").write_text(
            page.content(),
            encoding="utf-8"
        )

        browser.close()
