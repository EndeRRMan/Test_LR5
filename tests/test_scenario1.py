import re
from urllib.parse import quote

from playwright.sync_api import expect, sync_playwright


SEARCH_QUERY = "Атака титанов аниме"


def test_rutube_like_headed():
    with sync_playwright() as p:
        # Подключаемся к уже открытому Chrome,
        # где пользователь заранее авторизован в RUTUBE
        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        page.bring_to_front()

        # 1. Открываем RUTUBE
        page.goto(
            "https://rutube.ru/",
            wait_until="domcontentloaded",
            timeout=30000
        )

        # 2. Вводим поисковый запрос
        search = page.get_by_placeholder("Поиск")
        search.fill(SEARCH_QUERY)

        # Пытаемся выполнить поиск штатной кнопкой
        search_button = page.get_by_role(
            "button",
            name="Отправить форму поиска"
        )

        search_button.click()

        page.wait_for_timeout(2000)

        # Если RUTUBE почему-то не перешёл на страницу поиска,
        # открываем её напрямую
        if "/search/" not in page.url:
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

        print(f"\nПоиск выполнен: {SEARCH_QUERY}")

        # 3. Ищем первое настоящее видео
        links = page.locator(
            'main a[href^="/video/"]:visible'
        )

        video_pattern = re.compile(
            r"^/video/[0-9a-f]{32}/$"
        )

        href = None

        for i in range(links.count()):
            candidate = links.nth(i).get_attribute("href")

            if candidate and video_pattern.match(candidate):
                href = candidate
                break

        assert href is not None, "Видео не найдено"

        print(f"Первое видео: {href}")

        # 4. Открываем первое видео
        page.goto(
            f"https://rutube.ru{href}",
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(3000)

        assert "/video/" in page.url

        # 5. Находим главную кнопку лайка
        like_button = page.get_by_title(
            "Нравится",
            exact=True
        )

        like_button.wait_for(
            state="visible",
            timeout=20000
        )

        # Получаем текущее состояние
        like_state = like_button.get_attribute("aria-pressed")

        print(f"Начальное состояние лайка: {like_state}")

        # 6. Если лайк уже стоит — снимаем его
        if like_state == "true":
            print("Лайк уже стоит -> снимаем")

            like_button.click()

            expect(like_button).to_have_attribute(
                "aria-pressed",
                "false"
            )

            # Обновляем страницу
            page.reload(
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(2000)

            like_button = page.get_by_title(
                "Нравится",
                exact=True
            )

            expect(like_button).to_have_attribute(
                "aria-pressed",
                "false"
            )

            print("После обновления лайк снят")

        else:
            print("Лайк изначально не установлен")

        # 7. Ставим лайк
        like_button = page.get_by_title(
            "Нравится",
            exact=True
        )

        like_button.click()

        expect(like_button).to_have_attribute(
            "aria-pressed",
            "true"
        )

        print("Лайк поставлен")

        # 8. Обновляем страницу
        page.reload(
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(2000)

        # 9. Проверяем, что после обновления лайк сохранился
        like_button = page.get_by_title(
            "Нравится",
            exact=True
        )

        expect(like_button).to_have_attribute(
            "aria-pressed",
            "true"
        )

        print("После обновления лайк всё ещё активен")
        print("Сценарий №1 успешно выполнен")