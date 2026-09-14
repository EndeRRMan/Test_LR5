from pathlib import Path
from urllib.parse import quote
import re

from playwright.sync_api import sync_playwright


SEARCH_QUERY = "Атака титанов аниме"


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

        # 2. Вводим поисковый запрос
        search = page.get_by_placeholder("Поиск")
        search.fill(SEARCH_QUERY)

        # 3. Открываем страницу поиска
        search_url = (
            "https://rutube.ru/search/?query="
            + quote(SEARCH_QUERY)
        )

        page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(3000)

        assert "/search/" in page.url

        print(f"\nURL поиска: {page.url}")

        # 4. Получаем ссылки из результатов поиска
        links = page.locator(
            'main a[href^="/video/"]:visible'
        )

        count = links.count()
        print(f"Найдено ссылок: {count}")

        assert count > 0, "Поиск RUTUBE не вернул результатов"

        # Настоящее видео выглядит примерно так:
        # /video/b217354c33f687d783400b9b45dcf2ff/
        video_pattern = re.compile(
            r"^/video/[0-9a-f]{32}/$"
        )

        href = None

        for i in range(count):
            candidate = links.nth(i).get_attribute("href")

            if candidate and video_pattern.match(candidate):
                href = candidate
                break

        assert href is not None, "Не удалось найти ссылку на видео"

        print(f"Первое настоящее видео: {href}")

        # 5. Открываем первое видео
        page.goto(
            f"https://rutube.ru{href}",
            wait_until="domcontentloaded",
            timeout=30000
        )

        assert "/video/" in page.url

        # 6. Сохраняем screenshot
        page.screenshot(
            path="artifacts/scenario2.png",
            full_page=True
        )

        # 7. Сохраняем HTML
        Path("artifacts/scenario2.html").write_text(
            page.content(),
            encoding="utf-8"
        )

        browser.close()
