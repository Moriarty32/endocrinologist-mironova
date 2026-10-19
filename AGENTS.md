# AGENTS.md — endocrinologist-mironova

Статический многостраничный сайт врача-эндокринолога. HTML + CSS + vanilla JS,
без сборщика и без runtime-зависимостей. Страницы генерируются Python-скриптом
из единого файла контента.

- Репозиторий: https://github.com/Moriarty32/endocrinologist-mironova (ветка `main`)
- Демо: https://moriarty32.github.io/endocrinologist-mironova/ (GitHub Pages, `.nojekyll`)
- Локальная копия: `D:\Проекты\endocrinologist-mironova`

## Инструменты на этой машине

Нет в PATH — вызывать по полному пути:

- git: `$env:USERPROFILE\.local\git\cmd\git.exe`
- node: `$env:USERPROFILE\.local\node\node.exe` (v24)
- python: `python` (3.12) — в PATH
- Python-зависимости: только `Pillow` (для `tools/prepare_assets.py` и `tools/build_audit_screens.py`)

## Сборка и проверки

```powershell
python tools/build_site.py          # генерация страниц, site-data.js, sitemap.xml
python tools/check_multipage.py     # 33 страницы: ссылки, canonical, H1, описания, id
python tools/check_assets.py        # все URL ассетов из CSS существуют
python -m http.server 4173          # локальный просмотр: http://localhost:4173/
```

JS-синтаксис: `node --check app.js` (и `booking.js`, `assets/js/site.js`, `assets/js/site-data.js`).

`build_site.py` идемпотентен: повторный запуск не должен менять рабочее дерево
(кроме `content/__pycache__`, см. ниже).

## Архитектура

- `content/site_content.py` — единственный источник данных: `BRAND`, `CONTACT`,
  `PRICES`, `SERVICES` (7), `DISEASES` (10), `ARTICLES` (3), `FAQ`.
- `tools/build_site.py` — генератор. Перезаписывает `uslugi/**`, `zabolevaniya/**`,
  `stati/**`, `zapis/`, разделы (`ceny/`, `o-vrache/`, `kontakty/`, `faq/`,
  `dokumenty/`, юридические страницы), `404.html`, `sitemap.xml`,
  `assets/js/site-data.js` и redirect-заглушки старых URL.
- `index.html` — **ручной** файл (квиз, диалоги документов), генератором не
  перезаписывается; общая шапка/футер подключаются из `assets/js/site.js`.
- `assets/js/site.js` — шапка, mega menu, мобильное меню, футер, подстановка цен.
- `app.js` — формы, маска телефона, квиз, `<dialog>`, `track()` → `window.dataLayer`.
- `booking.js` + `booking.css` — страница `/zapis/`: 7 дней, слоты, сводка выбора.
- CSS-слои: `styles.css` (база и формы) → `landing.css` (главная) +
  `inner.css`/`pages.css` (внутренние) + `site.css` (шапка/футер) → `typography.css`
  (переопределяет размеры текста на всех страницах).

## Правила работы

- Правки контента и цен — только в `content/site_content.py`, затем
  `python tools/build_site.py`. Сгенерированные HTML руками не редактировать.
- Правки общей шапки, меню и футера — в `assets/js/site.js`.
- Абсолютных путей в коде нет; `BASE_URL` в `build_site.py` задаёт канонические URL
  (жёстко привязан к GitHub Pages этого репозитория).
- Аналитика не должна получать медицинские данные: в события идут только имена
  событий и неконфиденциальные флаги.
- Формы демонстрационные: на сервер ничего не отправляется, контакты кладутся в
  `sessionStorage` текущей вкладки. Бэкенда нет.

## Известные ограничения

- `content/__pycache__/site_content.cpython-312.pyc` закоммичен в репозиторий, хотя
  `__pycache__/` в `.gitignore`; после сборки файл «грязнит» `git status`.
- `README.md` и `AUDIT.md` ссылаются на старый путь `D:\Проекты\site` — только текст
  документации, в коде таких путей нет.
- Медицинские тексты, цены, реквизиты, фото и юридические документы — прототип,
  требуют подтверждения и редактуры перед публикацией (см. `DECISIONS.md`,
  `AUDIT.md`, раздел «Важно: это прототип» в `README.md`).
- `tools/check_site.py`, `tools/patch_home.py`, `tools/patch_home_links.py` —
  одноразовые исторические скрипты, в текущем пайплайне не участвуют.
- CI нет: проверки запускаются вручную.
