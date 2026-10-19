# -*- coding: utf-8 -*-
"""Static multi-page build for the endocrinologist site.

Reads content/site_content.py, writes:
- assets/js/site-data.js
- uslugi/**, zabolevaniya/**, stati/**, section pages
- sitemap.xml
- redirect stubs for legacy root URLs

The home page is maintained separately because it carries the interactive
quiz and document dialogs; its shell is replaced with the shared one.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content"))

import site_content as C  # noqa: E402

BASE_URL = "https://moriarty32.github.io/endocrinologist-mironova"
VERSION = "20261020j"
ASSETS = "assets"

SERVICES_BY_SLUG = {item["slug"]: item for item in C.SERVICES}
DISEASES_BY_SLUG = {item["slug"]: item for item in C.DISEASES}
ARTICLES_BY_SLUG = {item["slug"]: item for item in C.ARTICLES}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def price(key: str) -> str:
    return f"{C.PRICES[key]:,}".replace(",", " ")


def page_url(path: str) -> str:
    if not path or path == "/":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{path.strip('/')}/"


def breadcrumbs(items: list[tuple[str, str | None]], base: str) -> str:
    parts = []
    for index, (label, href) in enumerate(items):
        if href:
            parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{esc(label)}</span>')
        if index < len(items) - 1:
            parts.append('<span class="sep" aria-hidden="true">/</span>')
    return f'<nav class="breadcrumbs" aria-label="Хлебные крошки">{"".join(parts)}</nav>'


def faq_html(items: list[tuple[str, str]], prefix: str, open_first: bool = True) -> str:
    blocks = []
    for index, (question, answer) in enumerate(items):
        blocks.append(
            f'<details{" open" if open_first and index == 0 else ""}><summary>{esc(question)}</summary>'
            f'<div><p>{esc(answer)}</p></div></details>'
        )
    return f'<div class="faq-accordion" id="{prefix}">{"".join(blocks)}</div>'


def lead_list(items: list[str], class_name: str = "check-list") -> str:
    return f'<ul class="{class_name}">' + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def process_list(items: list[dict]) -> str:
    blocks = []
    for item in items:
        blocks.append(f"<li><strong>{esc(item['title'])}</strong>{esc(item['text'])}</li>")
    return f'<ol class="number-list">{"".join(blocks)}</ol>'


def page_shell(
    *,
    title: str,
    description: str,
    canonical: str,
    base: str,
    body: str,
    body_class: str = "inner-page",
    json_ld: list[dict] | None = None,
    og_type: str = "website",
    image: str = "assets/img/og-cover.jpg",
    extra_head: str = "",
    extra_scripts: str = "",
) -> str:
    ld = ""
    if json_ld:
        ld = "\n".join(
            f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=False)}</script>'
            for item in json_ld
        )
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#176b65">
  <meta property="og:type" content="{esc(og_type)}">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:site_name" content="Анна Миронова — врач-эндокринолог">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{BASE_URL}/{image}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{base}styles.css?v={VERSION}">
  <link rel="stylesheet" href="{base}pages.css?v={VERSION}">
  <link rel="stylesheet" href="{base}site.css?v={VERSION}">
  <link rel="stylesheet" href="{base}inner.css?v={VERSION}">
  <link rel="stylesheet" href="{base}typography.css?v={VERSION}">
  <link rel="stylesheet" href="{base}inner-theme.css?v={VERSION}">
  {extra_head}
  {ld}
</head>
<body class="{esc(body_class)}" data-base="{esc(base)}">
  <a class="skip-link" href="#main">Перейти к содержанию</a>
  <div id="site-header"></div>
  <main id="main" class="page-main">
{body}
  </main>
  <div id="site-footer"></div>
  <p class="sr-only" id="live-region" aria-live="polite"></p>
  <script src="{base}assets/js/site-data.js?v={VERSION}" defer></script>
  <script src="{base}assets/js/site.js?v={VERSION}" defer></script>
  <script src="{base}app.js?v={VERSION}" defer></script>
  {extra_scripts}
</body>
</html>
"""


def booking_form(source: str, topic: str, base: str, title: str = "Записаться на консультацию") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", source.lower()).strip("-")[:48]
    return f"""
<div class="page-form-card final-form-card">
  <h2>{esc(title)}</h2>
  <p class="form-sub">Оставьте контакт — согласуем время и удобный формат связи.</p>
  <div class="page-form-success" data-form-success tabindex="-1" hidden>
    <h3>Заявка отправлена</h3>
    <p>Спасибо! Это демонстрационная версия: данные не отправляются на сервер. В рабочей версии здесь будет подтверждение записи.</p>
    <button class="btn btn-ghost" type="button" data-form-reset>Отправить ещё одну заявку</button>
  </div>
  <form class="page-form" data-form="{esc(source)}" novalidate>
    <input type="hidden" name="source" value="{esc(source)}">
    <input type="hidden" name="topic" value="{esc(topic)}">
    <div class="form-row-2">
      <div class="page-field">
        <label for="name-{slug}">Ваше имя</label>
        <input id="name-{slug}" name="name" type="text" autocomplete="name" placeholder="Как к вам обращаться" required>
      </div>
      <div class="page-field">
        <label for="phone-{slug}">Телефон</label>
        <input id="phone-{slug}" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" data-phone required>
      </div>
    </div>
    <div class="page-field">
      <label for="contact-{slug}">Способ связи</label>
      <select id="contact-{slug}" name="contact">
        <option>WhatsApp</option>
        <option>Telegram</option>
        <option>Телефон</option>
      </select>
    </div>
    <label class="consent-line">
      <input type="checkbox" name="consent" required>
      <span>Согласен с <a href="{base}politika-konfidencialnosti/">политикой конфиденциальности</a> и <a href="{base}soglasie-na-obrabotku-dannyh/">обработкой персональных данных</a>.</span>
    </label>
    <button class="btn btn-primary" type="submit">Записаться на консультацию</button>
    <p class="form-error" data-form-error hidden>Проверьте имя, телефон и согласие на обработку данных.</p>
    <p class="form-note">Демонстрационная форма. Не отправляйте медицинские документы и подробности здоровья через этот сайт.</p>
  </form>
</div>"""


def aside_booking(
    base: str,
    *,
    topic: str,
    toc: list[tuple[str, str]] | None = None,
    related: list[tuple[str, str]] | None = None,
) -> str:
    toc_html = ""
    if toc:
        toc_html = (
            '<div class="toc-card"><p>На странице</p>'
            + "".join(f'<a href="#{esc(anchor)}">{esc(label)}</a>' for anchor, label in toc)
            + "</div>"
        )
    related_html = ""
    if related:
        related_html = (
            '<div class="aside-card"><h2>Связанные страницы</h2><div class="aside-links">'
            + "".join(f'<a href="{esc(href)}">{esc(label)}</a>' for label, href in related)
            + "</div></div>"
        )
    return f"""
<aside class="inner-aside" aria-label="Запись и навигация">
  <div class="aside-card aside-card-mint">
    <h2>Записаться на консультацию</h2>
    <div class="aside-price"><strong data-price="primary">{price('primary')}</strong><span>₽</span></div>
    <p class="aside-duration">Первичная консультация · 60 минут</p>
    <p>Онлайн по видеосвязи. Время согласуем после заявки.</p>
    <a class="btn btn-primary" href="{base}zapis/">Выбрать время</a>
    <a class="aside-note" href="{base}index.html?quiz=1">Не уверены? Ответить на вопросы →</a>
  </div>
  {related_html}
  {toc_html}
</aside>"""


def cta_band(base: str, title: str, text: str) -> str:
    return f"""
<div class="cta-band">
  <div><h2>{esc(title)}</h2><p>{esc(text)}</p></div>
  <a class="btn btn-primary" href="{base}zapis/">Записаться</a>
</div>"""


def related_section(service_slugs: list[str], article_slugs: list[str], base: str) -> str:
    links = []
    for slug in service_slugs:
        item = SERVICES_BY_SLUG.get(slug)
        if item:
            links.append(f'<a href="{base}uslugi/{item["slug"]}/">{esc(item["title"])}</a>')
    for slug in article_slugs:
        item = ARTICLES_BY_SLUG.get(slug)
        if item:
            links.append(f'<a href="{base}stati/{item["slug"]}/">{esc(item["title"])}</a>')
    if not links:
        return ""
    return f'<div class="article-related" aria-label="Связанные материалы">{"".join(links)}</div>'


def page_booking_section(base: str, source: str, topic: str, title: str, text: str, points: list[str]) -> str:
    return f"""
<section class="page-booking" id="booking" aria-labelledby="booking-title">
  <div class="container page-booking-grid">
    <div class="page-booking-copy">
      <p class="page-kicker">Запись</p>
      <h2 id="booking-title">{esc(title)}</h2>
      <p>{esc(text)}</p>
      {lead_list(points)}
      <p class="form-note">Если вы не уверены, подходит ли формат, начните с короткого опроса или напишите в мессенджер.</p>
    </div>
    {booking_form(source, topic, base)}
  </div>
</section>"""


def json_breadcrumbs(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": index + 1, "name": label, "item": url}
            for index, (label, url) in enumerate(items)
        ],
    }


def online_service_page(item: dict) -> None:
    base = "../../"
    canonical = page_url("uslugi/endokrinolog-online")
    content = C.ONLINE_SERVICE
    icon_sprite = (ROOT / "assets/icons.svg").read_text(encoding="utf-8").replace(
        '<svg xmlns=', '<svg class="online-icon-sprite" aria-hidden="true" xmlns=', 1
    )

    def symbol(name: str) -> str:
        return f'<svg aria-hidden="true"><use href="#{esc(name)}"></use></svg>'

    concern_cards = "".join(
        f'<div class="online-concern"><span class="online-concern-icon">{symbol(icon)}</span><div><h3>{esc(title)}</h3><p>{esc(description)}</p></div></div>'
        for icon, title, description in content["concerns"]
    )
    process_cards = "".join(
        f'<div class="online-process-step"><span class="online-step-number">{index}</span><span class="online-step-icon">{symbol(icon)}</span>'
        f'<h3>{esc(title)}</h3><p>{esc(description)}</p></div>'
        for index, (icon, title, description) in enumerate(content["process"], start=1)
    )
    included_items = "".join(f'<li>{esc(value)}</li>' for value in C.PRICES["primary_includes"])
    privacy_items = "".join(
        f'<li>{symbol(icon)}<span>{esc(description)}</span></li>'
        for icon, description in content["privacy"]
    )
    body = f"""
{icon_sprite}
<section class="online-hero" aria-labelledby="online-title">
  <div class="container online-hero-inner">
    {breadcrumbs([("Главная", f"{base}index.html"), ("Услуги", f"{base}uslugi/"), ("Эндокринолог онлайн", None)], base)}
    <div class="online-hero-grid">
      <div class="online-hero-copy">
        <p class="online-pill">Онлайн-консультация</p>
        <h1 id="online-title">{esc(content['hero_title'])}</h1>
        <p class="online-hero-lead">{esc(content['hero_lead'])}</p>
        <div class="online-meta" aria-label="Параметры консультации">
          <span>{symbol('icon-video')}<span><strong>Онлайн</strong><small>по видеосвязи</small></span></span>
          <span>{symbol('icon-clock')}<span><strong>{esc(C.PRICES['primary_duration'])}</strong><small>длительность</small></span></span>
          <span><i class="online-ruble" aria-hidden="true">₽</i><span><strong><span data-price="primary">{price('primary')}</span> ₽</strong><small>стоимость</small></span></span>
          <span>{symbol('icon-shield')}<span><strong>Конфиденциально</strong><small>личные вопросы</small></span></span>
        </div>
        <div class="online-hero-actions">
          <a class="btn btn-primary" href="{base}zapis/">Записаться на консультацию <span aria-hidden="true">→</span></a>
          <a class="online-text-link" href="#process">Как проходит консультация <span aria-hidden="true">→</span></a>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="container online-content">
      <aside class="online-doctor-card" aria-label="Врач">
        <div class="online-doctor-identity"><h2>{esc(C.BRAND['full_name'])}</h2><p>{esc(C.BRAND['role'])}</p></div>
        <ul>
          <li>{symbol('icon-calendar')}<span>{esc(content['doctor_experience'])}</span></li>
          <li>{symbol('icon-video')}<span>Онлайн-консультации для взрослых</span></li>
          <li>{symbol('icon-shield')}<span>Доказательный подход</span></li>
        </ul>
        <a href="{base}o-vrache/">Подробнее о враче →</a>
      </aside>
  <section class="online-concerns online-panel" id="for-whom" aria-labelledby="concerns-title">
    <div class="online-concerns-main">
      <p class="online-pill">Когда стоит обратиться</p>
      <h2 id="concerns-title">{esc(content['concerns_title'])}</h2>
      <div class="online-concerns-grid">{concern_cards}</div>
    </div>
    <div class="online-feature" id="questions">
      <img src="{base}assets/img/service-online-thyroid.webp" width="1024" height="1536" alt="Иллюстрация щитовидной железы" loading="lazy">
      <div class="online-feature-copy">
        <p class="online-pill">{esc(content['feature_kicker'])}</p>
        <h3>{esc(content['feature_title'])}</h3>
        <p>{esc(content['feature_text'])}</p>
      </div>
    </div>
  </section>

  <section class="online-process online-panel" id="process" aria-labelledby="process-title">
    <p class="online-pill">Просто и удобно</p>
    <h2 id="process-title">Как проходит онлайн-консультация</h2>
    <div class="online-process-grid">{process_cards}</div>
  </section>

  <section class="online-details" aria-label="Стоимость, результат и конфиденциальность">
    <div class="online-detail-card online-price" id="price">
      <p class="online-pill">Первичная консультация</p>
      <h2>Стоимость и формат</h2>
      <div class="online-price-line"><strong><span data-price="primary">{price('primary')}</span> ₽</strong><span>{esc(C.PRICES['primary_duration'])}<br>по видеосвязи</span></div>
      <ul class="online-checks">{included_items}</ul>
      <a class="btn btn-primary" href="{base}zapis/">Записаться на консультацию →</a>
      <p class="online-price-note">{esc(C.PRICES['payment'])}</p>
    </div>
    <div class="online-detail-card online-result" id="outcomes">
      <p class="online-pill">Результат консультации</p>
      <h2>{esc(content['result_title'])}</h2>
      <p class="online-result-text">{esc(content['result_text'])}</p>
      <ul class="online-checks">{''.join(f'<li>{esc(value)}</li>' for value in item['outcomes'])}</ul>
    </div>
    <div class="online-detail-card online-privacy">
      <p class="online-pill">Важно</p>
      <h2>{esc(content['privacy_title'])}</h2>
      <ul>{privacy_items}</ul>
    </div>
  </section>

  <section class="online-help" aria-labelledby="online-help-title">
    <div>
      <p class="online-pill">Есть вопросы?</p>
      <h2 id="online-help-title">{esc(content['help_title'])}</h2>
      <p>{esc(content['help_text'])}</p>
    </div>
    <div class="online-help-links">
      <a class="btn btn-primary" href="{esc(C.CONTACT['whatsapp'])}" target="_blank" rel="noopener">Задать вопрос в WhatsApp</a>
      <a class="btn btn-outline" href="{base}kontakty/">Все контакты →</a>
    </div>
  </section>

  <section class="online-faq" id="faq" aria-labelledby="online-faq-title">
    <h2 id="online-faq-title">Частые вопросы</h2>
    {faq_html(item['faq'], 'faq-' + item['slug'])}
  </section>
</div>
"""
    ld = [
        json_breadcrumbs([("Главная", f"{BASE_URL}/"), ("Услуги", page_url("uslugi")), (item["title"], canonical)]),
        {
            "@context": "https://schema.org",
            "@type": "MedicalWebPage",
            "name": item["title"],
            "description": content["hero_lead"],
            "url": canonical,
            "inLanguage": "ru-RU",
            "about": {"@type": "MedicalProcedure", "name": item["title"]},
            "provider": {"@type": "Physician", "name": C.BRAND["full_name"]},
            "audience": {"@type": "Patient"},
        },
    ]
    write("uslugi/endokrinolog-online/index.html", page_shell(
        title=f"{item['title']} — Анна Миронова, врач-эндокринолог",
        description=f"{content['hero_lead']} Стоимость — {price('primary')} ₽ за {C.PRICES['primary_duration']}.",
        canonical=canonical, base=base, body=body, body_class="inner-page service-online-page",
        json_ld=ld, og_type="article",
        extra_head=f'  <link rel="stylesheet" href="{base}service-online.css?v=20261020b">',
    ))


def service_page(item: dict) -> None:
    if item["slug"] == "endokrinolog-online":
        online_service_page(item)
        return
    base = "../../"
    canonical = page_url(f"uslugi/{item['slug']}")
    title = f"{item['title']} — Анна Миронова, врач-эндокринолог"
    description = f"{item['lead']} Стоимость — {price('primary')} ₽ за 60 минут. Онлайн-запись."
    toc = [
        ("for-whom", "Кому подходит"),
        ("questions", "Какие вопросы"),
        ("outcomes", "Что вы получите"),
        ("process", "Как проходит"),
        ("price", "Стоимость"),
        ("faq", "Частые вопросы"),
    ]
    related = [
        (DISEASES_BY_SLUG[slug]["title"], f"{base}zabolevaniya/{slug}/")
        for slug in item["related_diseases"]
        if slug in DISEASES_BY_SLUG
    ]
    body = f"""
<div class="container">
  {breadcrumbs([("Главная", f"{base}index.html"), ("Услуги", f"{base}uslugi/"), (item["title"], None)], base)}
  <header class="page-hero">
    <p class="page-kicker">Услуга</p>
    <h1>{esc(item.get('h1', item['title']))}</h1>
    <p class="lead">{esc(item['lead'])}</p>
    <div class="page-meta">
      <span>Онлайн</span>
      <span><span data-price="primary">{price('primary')}</span> ₽</span>
      <span>60 минут</span>
      <span>Взрослые</span>
    </div>
    <div class="page-hero-actions">
      <a class="btn btn-primary" href="{base}zapis/">Записаться на консультацию</a>
      <a class="btn btn-ghost" href="{base}index.html?quiz=1">Ответить на вопросы</a>
    </div>
  </header>
  <div class="inner-layout">
    <article class="inner-main prose">
      <section id="for-whom">
        <h2>Кому подходит консультация</h2>
        <p>Формат рассчитан на взрослых, которым нужен разбор ситуации без поездки в клинику. Он не заменяет очный приём, если требуется осмотр.</p>
        {lead_list(item['for_whom'])}
      </section>
      <section id="questions">
        <h2>Какие вопросы рассматриваются</h2>
        {lead_list(item['questions'])}
      </section>
      <section id="outcomes">
        <h2>Что вы получите</h2>
        {lead_list(item['outcomes'])}
      </section>
      <section id="process">
        <h2>Как проходит консультация</h2>
        {process_list(item['process'])}
      </section>
      {cta_band(base, "Нужен разбор именно вашей ситуации?", "Оставьте заявку — согласуем время и формат. Если вопрос не входит в специализацию, я скажу об этом прямо.")}
      <section id="price">
        <h2>Стоимость</h2>
        <p>Первичная онлайн-консультация — <strong><span data-price="primary">{price('primary')}</span> ₽</strong> за 60 минут. Повторная — <strong><span data-price="followup">{price('followup')}</span> ₽</strong> за 30 минут.</p>
        <p>В стоимость входит разбор жалоб и результатов, объяснение показателей, план дальнейших шагов и краткое резюме. Оплата — после согласования времени. <a href="{base}ceny/">Все цены и условия</a>.</p>
      </section>
      <section class="doctor-mini-card">
        <div class="doctor-mini-photo"><img src="{base}assets/img/doctor-about-330.webp?v=20261020b" srcset="{base}assets/img/doctor-about-330.webp?v=20261020b 330w, {base}assets/img/doctor-about-660.webp?v=20261020b 660w" sizes="104px" alt="Анна Викторовна Миронова, врач-эндокринолог" width="660" height="825" loading="lazy"></div>
        <div>
          <p class="page-kicker">Врач</p>
          <h2>Анна Викторовна Миронова</h2>
          <p>Врач-эндокринолог с 12-летним опытом. Консультирую взрослых онлайн, объясняю результаты анализов и помогаю составить понятный план действий.</p>
          <a class="text-link" href="{base}o-vrache/">Подробнее о враче и документах →</a>
        </div>
      </section>
      <section id="faq">
        <h2>Частые вопросы</h2>
        {faq_html(item['faq'], 'faq-' + item['slug'])}
      </section>
      <section>
        <h2>Связанные материалы</h2>
        <p>Продолжите изучение темы или посмотрите страницы заболеваний, с которыми чаще всего обращаются.</p>
        {related_section(item['related_diseases'], item['related_articles'], base)}
      </section>
    </article>
    {aside_booking(base, topic=item['title'], toc=toc, related=related)}
  </div>
</div>
{page_booking_section(base, f"uslugi/{item['slug']}", item['title'], "Записаться на консультацию", "Оставьте контакт, и я согласую с вами удобное время. Если сомневаетесь в формате, это можно обсудить до записи.", ["Первичная консультация — 60 минут", "Повторная — 30 минут", "Оплата после подтверждения времени"])}
"""
    ld = [
        json_breadcrumbs([
            ("Главная", f"{BASE_URL}/"),
            ("Услуги", page_url("uslugi")),
            (item["title"], canonical),
        ]),
        {
            "@context": "https://schema.org",
            "@type": "MedicalWebPage",
            "name": item["title"],
            "description": description,
            "url": canonical,
            "inLanguage": "ru-RU",
            "about": {"@type": "MedicalProcedure", "name": item["title"]},
            "provider": {"@type": "Physician", "name": C.BRAND["full_name"]},
            "audience": {"@type": "Patient"},
        },
    ]
    write(f"uslugi/{item['slug']}/index.html", page_shell(
        title=title, description=description, canonical=canonical, base=base,
        body=body, json_ld=ld, og_type="article",
    ))


def disease_page(item: dict) -> None:
    base = "../../"
    canonical = page_url(f"zabolevaniya/{item['slug']}")
    title = f"{item['title']}: симптомы, диагностика и когда обращаться — Анна Миронова"
    description = f"{item['lead']} Разбор симптомов, причин, диагностики и возможностей онлайн-консультации."
    toc = [
        ("what", "Что это"),
        ("symptoms", "Симптомы"),
        ("causes", "Причины"),
        ("diagnostics", "Диагностика"),
        ("treatment", "Лечение"),
        ("when", "Когда к врачу"),
        ("online", "Онлайн-формат"),
        ("help", "Чем поможет врач"),
        ("faq", "Вопросы"),
    ]
    related = [
        (SERVICES_BY_SLUG[slug]["title"], f"{base}uslugi/{slug}/")
        for slug in item["related_services"]
        if slug in SERVICES_BY_SLUG
    ]
    body = f"""
<div class="container">
  {breadcrumbs([("Главная", f"{base}index.html"), ("Заболевания", f"{base}zabolevaniya/"), (item["title"], None)], base)}
  <header class="page-hero">
    <p class="page-kicker">Заболевание · {esc(item['group'])}</p>
    <h1>{esc(item['title'])}</h1>
    <p class="lead">{esc(item['lead'])}</p>
    <div class="page-meta">
      <span>Информационная страница</span>
      <span>Онлайн-консультация</span>
    </div>
    <div class="page-hero-actions">
      <a class="btn btn-primary" href="{base}zapis/">Записаться на консультацию</a>
      <a class="btn btn-ghost" href="{base}index.html?quiz=1">Ответить на вопросы</a>
    </div>
  </header>
  <div class="inner-layout">
    <article class="inner-main prose">
      <section id="what">
        <h2>Что это за заболевание</h2>
        <p>{esc(item['what'])}</p>
      </section>
      <section id="symptoms">
        <h2>Основные признаки и симптомы</h2>
        {lead_list(item['symptoms'])}
        <div class="callout"><strong>Важно</strong><p>Симптомы неспецифичны и могут встречаться при других состояниях. Эта страница не заменяет диагностику.</p></div>
      </section>
      <section id="causes">
        <h2>Возможные причины и факторы риска</h2>
        {lead_list(item['causes'])}
      </section>
      <section id="diagnostics">
        <h2>Как проводится диагностика</h2>
        {lead_list(item['diagnostics'])}
      </section>
      <section id="treatment">
        <h2>Общие принципы лечения и наблюдения</h2>
        <p>{esc(item['treatment'])}</p>
      </section>
      <section id="when">
        <h2>Когда необходимо обратиться к врачу</h2>
        {lead_list(item['when'])}
        <div class="callout"><strong>Неотложная помощь</strong><p>При боли в груди, выраженной одышке, спутанности сознания, очень высокой глюкозе, рвоте, потере сознания или резком ухудшении состояния звоните в скорую помощь, а не записывайтесь на онлайн-консультацию.</p></div>
      </section>
      <section id="online">
        <h2>Возможности и ограничения онлайн-консультации</h2>
        <p>{esc(item['online'])}</p>
      </section>
      <section id="help">
        <h2>Как врач может помочь с конкретным запросом</h2>
        {lead_list(item['help'])}
      </section>
      {cta_band(base, "Обсудить ситуацию на консультации", "Можно прийти с уже готовыми анализами или без них. Начнём с того, что важно именно вам.")}
      <section>
        <h2>Стоимость консультации</h2>
        <p>Первичная онлайн-консультация — <strong><span data-price="primary">{price('primary')}</span> ₽</strong> за 60 минут. Повторная — <strong><span data-price="followup">{price('followup')}</span> ₽</strong> за 30 минут. <a href="{base}ceny/">Подробнее об условиях</a>.</p>
      </section>
      <section id="faq">
        <h2>Частые вопросы</h2>
        {faq_html(item['faq'], 'faq-' + item['slug'])}
      </section>
      <section>
        <h2>Связанные услуги и материалы</h2>
        {related_section(item['related_services'], item['related_articles'], base)}
      </section>
    </article>
    {aside_booking(base, topic=item['title'], toc=toc, related=related)}
  </div>
</div>
{page_booking_section(base, f"zabolevaniya/{item['slug']}", item['title'], "Запись на консультацию", "Оставьте контакт, чтобы согласовать время. Онлайн-формат подходит для обсуждения результатов и плана, но не для экстренной помощи.", ["Первичная консультация — 60 минут", "Повторная — 30 минут", "Оплата после подтверждения времени"])}
"""
    ld = [
        json_breadcrumbs([
            ("Главная", f"{BASE_URL}/"),
            ("Заболевания", page_url("zabolevaniya")),
            (item["title"], canonical),
        ]),
        {
            "@context": "https://schema.org",
            "@type": "MedicalWebPage",
            "name": item["title"],
            "description": description,
            "url": canonical,
            "inLanguage": "ru-RU",
            "about": {"@type": "MedicalCondition", "name": item["title"]},
            "audience": {"@type": "Patient"},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in item["faq"]
            ],
        },
    ]
    write(f"zabolevaniya/{item['slug']}/index.html", page_shell(
        title=title, description=description, canonical=canonical, base=base,
        body=body, json_ld=ld, og_type="article",
    ))


def article_page(item: dict) -> None:
    base = "../../"
    dates = {
        "povyshen-ttg": ("2026-02-12", "2026-03-18"),
        "insulinorezistentnost": ("2026-03-03", "2026-03-20"),
        "voprosy-endokrinologu": ("2026-03-18", "2026-03-25"),
    }
    date_published, date_modified = dates.get(item["slug"], ("2026-01-01", "2026-01-01"))
    canonical = page_url(f"stati/{item['slug']}")
    title = f"{item['title']} — Анна Миронова"
    description = item["lead"]
    sections_html = []
    for section in item["sections"]:
        paragraphs = "".join(f"<p>{esc(p)}</p>" for p in section["paragraphs"])
        sections_html.append(f'<section><h2>{esc(section["h2"])}</h2>{paragraphs}</section>')
    faq = faq_html(item["faq"], "faq-" + item["slug"])
    sources = "".join(
        f'<li><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>'
        for label, url in item["sources"]
    )
    body = f"""
<div class="container article-page">
  {breadcrumbs([("Главная", f"{base}index.html"), ("Статьи", f"{base}stati/"), (item["title"], None)], base)}
  <header class="page-hero">
    <p class="page-kicker">{esc(item['category'])}</p>
    <h1>{esc(item['title'])}</h1>
    <p class="lead">{esc(item['lead'])}</p>
    <div class="article-meta">
      <span>Автор: <strong>Анна Викторовна Миронова</strong>, врач-эндокринолог</span>
      <span>Опубликовано: {esc(item['date'])}</span>
      <span>Обновлено: {esc(item['updated'])}</span>
    </div>
  </header>
  <div class="article-layout">
    <article class="inner-main prose">
      {''.join(sections_html)}
      <div class="callout"><strong>Когда обратиться к эндокринологу</strong><p>Если симптомы сохраняются, анализы выходят за пределы нормы или вы не понимаете, что делать дальше, обсудите ситуацию на консультации. При острых состояниях нужна неотложная помощь.</p></div>
      <section class="article-faq"><h2>Частые вопросы</h2>{faq}</section>
      <section><h2>Источники</h2><ul class="article-source-list">{sources}</ul></section>
      <section><h2>Похожие материалы</h2>{related_section(item['related_services'], item['related_articles'], base)}</section>
    </article>
    <aside class="article-aside">
      <div class="aside-card aside-card-mint">
        <h2>Обсудить статью со врачом</h2>
        <p>Онлайн-консультация помогает связать общие рекомендации с вашей ситуацией.</p>
        <div class="aside-price"><strong data-price="primary">{price('primary')}</strong><span>₽</span></div>
        <p class="aside-duration">60 минут · видеосвязь</p>
        <a class="btn btn-primary" href="{base}zapis/">Записаться</a>
      </div>
      <div class="aside-card">
        <h2>Связанные услуги</h2>
        <div class="aside-links">
          {''.join(f'<a href="{base}uslugi/{slug}/">{esc(SERVICES_BY_SLUG[slug]["title"])}</a>' for slug in item['related_services'] if slug in SERVICES_BY_SLUG)}
        </div>
      </div>
    </aside>
  </div>
</div>
{page_booking_section(base, f"stati/{item['slug']}", item['title'], "Записаться на консультацию", "Если после статьи остались вопросы, их можно обсудить на консультации. Это не экстренная помощь и не замена очному приёму.", ["Разбор вашей ситуации", "План обследования", "Ответы на вопросы"])}
"""
    ld = [
        json_breadcrumbs([
            ("Главная", f"{BASE_URL}/"),
            ("Статьи", page_url("stati")),
            (item["title"], canonical),
        ]),
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": item["title"],
            "description": description,
            "datePublished": date_published,
            "dateModified": date_modified,
            "author": {"@type": "Person", "name": C.BRAND["full_name"], "jobTitle": C.BRAND["role"]},
            "publisher": {"@type": "Organization", "name": C.BRAND["full_name"]},
            "mainEntityOfPage": canonical,
            "image": f"{BASE_URL}/assets/img/og-cover.jpg",
        },
    ]
    write(f"stati/{item['slug']}/index.html", page_shell(
        title=title, description=description, canonical=canonical, base=base,
        body=body, json_ld=ld, og_type="article", image="assets/img/og-cover.jpg",
    ))


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def section_page(
    *,
    path: str,
    title: str,
    h1: str,
    lead: str,
    body: str,
    base: str = "../",
    description: str | None = None,
    json_ld: list[dict] | None = None,
) -> None:
    canonical = page_url(path)
    kickers = {
        "uslugi": "Онлайн-консультации для взрослых",
        "zabolevaniya": "Эндокринологические темы",
        "stati": "Материалы врача",
        "ceny": "Стоимость консультации",
        "otzyvy": "Обратная связь",
        "kontakty": "Связь с врачом",
        "faq": "Частые вопросы",
        "dokumenty": "Образование и квалификация",
    }
    content = f"""
<div class="container">
  {breadcrumbs([("Главная", f"{base}index.html"), (h1, None)], base)}
  <header class="page-hero">
    <p class="page-kicker">{esc(kickers.get(path, "Информация"))}</p>
    <h1>{esc(h1)}</h1>
    <p class="lead">{esc(lead)}</p>
  </header>
  {body}
</div>"""
    write(f"{path}/index.html", page_shell(
        title=title,
        description=description or lead,
        canonical=canonical,
        base=base,
        body=content,
        json_ld=json_ld,
    ))


def icon_placeholder(name: str) -> str:
    return f'<svg class="icon" aria-hidden="true"><use href="../assets/icons.svg#{name}"></use></svg>'


def services_index() -> None:
    base = "../"
    cards = []
    for item in C.SERVICES:
        cards.append(f"""
<a class="service-card" href="{base}uslugi/{item['slug']}/">
  <span class="service-card-icon">{icon_placeholder(item['icon'])}</span>
  <h3>{esc(item['title'])}</h3>
  <p>{esc(item['short'])}</p>
  <div class="card-foot"><span><strong><span data-price="{item.get('price_key', 'primary')}">{price(item.get('price_key', 'primary'))}</span> ₽</strong></span><span class="card-arrow" aria-hidden="true">→</span></div>
</a>""")
    body = f"""
<div class="cards-grid cards-grid-3">{''.join(cards)}</div>
<div class="cta-band">
  <div><h2>Не знаете, какая услуга подходит?</h2><p>Начните с первичной консультации: на ней можно определить дальнейшие шаги.</p></div>
  <a class="btn btn-primary" href="{base}zapis/">Записаться</a>
</div>
<h2 class="section-title">Как выбрать формат</h2>
<div class="prose">
  <p>Первичная консультация подходит, если вы впервые обращаетесь или хотите разобрать ситуацию целиком. Повторная — если вы уже были на приёме и нужно обсудить динамику. Отдельные направления помогают сосредоточиться на щитовидной железе, диабете, весе или гормональных вопросах.</p>
  <p>Если сомневаетесь, начните с первичной консультации или короткого опроса. Я скажу, если вопрос не входит в мою специализацию.</p>
</div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Оставьте контакт — согласуем время и формат.</p>{lead_list(['Первичная консультация — 60 минут', 'Повторная — 30 минут', 'Оплата после подтверждения времени'])}</div>{booking_form('uslugi', 'Выбор услуги', base)}</div></section>
"""
    ld = [
        json_breadcrumbs([("Главная", f"{BASE_URL}/"), ("Услуги", page_url("uslugi"))]),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Услуги врача-эндокринолога",
            "description": "Онлайн-консультации, разбор анализов и направления эндокринологии.",
            "url": page_url("uslugi"),
        },
    ]
    section_page(
        path="uslugi",
        title="Услуги врача-эндокринолога — онлайн-консультации | Анна Миронова",
        h1="Услуги",
        lead="Онлайн-консультации для взрослых: первичный разбор, повторная встреча, анализы и отдельные эндокринологические направления.",
        body=body, base=base, json_ld=ld,
    )


def diseases_index() -> None:
    base = "../"
    groups = []
    for group in ["Щитовидная железа", "Обмен веществ", "Углеводный обмен", "Гормональные нарушения"]:
        items = [item for item in C.DISEASES if item["group"] == group]
        if not items:
            continue
        cards = "".join(f"""
<a class="disease-card" href="{base}zabolevaniya/{item['slug']}/">
  <span class="disease-card-icon">{icon_placeholder(item['icon'])}</span>
  <h3>{esc(item['title'])}</h3>
  <p>{esc(item['lead'])}</p>
</a>""" for item in items)
        groups.append(f'<section class="disease-group"><h2>{esc(group)}</h2><div class="disease-grid">{cards}</div></section>')
    body = f"""
<div class="prose"><p>Информационные страницы помогают разобраться в симптомах и обследованиях, но не заменяют консультацию. Выберите тему или посмотрите услуги, если нужен разбор вашей ситуации.</p></div>
{''.join(groups)}
<div class="cta-band"><div><h2>Нужен разбор вашей ситуации?</h2><p>На консультации можно обсудить результаты и составить план.</p></div><a class="btn btn-primary" href="{base}zapis/">Записаться</a></div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Оставьте контакт, чтобы согласовать время.</p>{lead_list(['Онлайн-формат', 'Первичная и повторная консультация', 'Оплата после подтверждения'])}</div>{booking_form('zabolevaniya', 'Выбор заболевания', base)}</div></section>
"""
    section_page(
        path="zabolevaniya",
        title="Заболевания эндокринной системы — информация для пациентов | Анна Миронова",
        h1="Заболевания",
        lead="Понятные материалы о щитовидной железе, обмене веществ, диабете и гормональных нарушениях.",
        body=body, base=base,
    )


def articles_index() -> None:
    base = "../"
    cards = []
    for item in C.ARTICLES:
        cards.append(f"""
<a class="article-card" href="{base}stati/{item['slug']}/">
  <img src="{base}assets/img/{item['image']}" alt="{esc(item['title'])}" width="600" height="380" loading="lazy">
  <div class="article-card-body">
    <span class="article-card-cat">{esc(item['category'])}</span>
    <h3>{esc(item['title'])}</h3>
    <p>{esc(item['lead'])}</p>
    <div class="article-card-foot"><span>{esc(item['date'])}</span><span>Читать →</span></div>
  </div>
</a>""")
    body = f"""
<div class="article-list">{''.join(cards)}</div>
<div class="cta-band"><div><h2>Хотите обсудить статью?</h2><p>Общие принципы не заменяют индивидуальный разбор.</p></div><a class="btn btn-primary" href="{base}zapis/">Записаться</a></div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Оставьте контакт — согласуем время.</p>{lead_list(['Разбор анализов и жалоб', 'Понятный план действий', 'Онлайн-формат'])}</div>{booking_form('stati', 'Статьи', base)}</div></section>
"""
    section_page(
        path="stati",
        title="Статьи врача-эндокринолога — экспертный блог | Анна Миронова",
        h1="Статьи",
        lead="Экспертные материалы о щитовидной железе, обмене веществ и подготовке к консультации.",
        body=body, base=base,
    )


def about_page() -> None:
    base = "../"
    profile = C.ABOUT_PROFILE
    icon_sprite = (ROOT / "assets/icons.svg").read_text(encoding="utf-8").replace(
        '<svg xmlns=', '<svg class="profile-icon-sprite" aria-hidden="true" xmlns=', 1
    )

    def icon(name: str) -> str:
        return f'<svg aria-hidden="true"><use href="#{esc(name)}"></use></svg>'

    docs = [
        ("Диплом", "о высшем образовании"),
        ("Ординатура", "по эндокринологии"),
        ("Аккредитация", "по специальности"),
        ("Обучение", "повышение квалификации"),
    ]
    doc_cards = "".join(
        f'<a class="profile-doc" href="{base}dokumenty/" aria-label="Подробнее: {esc(title)}">'
        f'<span class="profile-doc-paper"><img src="{base}assets/img/about-document-0{index}.webp" width="235" height="345" alt="" loading="lazy"><span>ОБРАЗЕЦ</span><strong>{esc(title)}</strong><small>{esc(subtitle)}</small></span>'
        f'<b>{esc(title)}</b><small>{esc(subtitle)}</small></a>'
        for index, (title, subtitle) in enumerate(docs, start=1)
    )
    principle_cards = "".join(
        f'<div class="profile-principle"><span>{icon(symbol)}</span><b>{esc(label)}</b></div>'
        for symbol, label in profile["principles"]
    )
    experience_cards = "".join(
        f'<li><strong>{esc(title)}</strong><span>{esc(description)}</span></li>'
        for title, description in profile["experience"]
    )
    education_cards = "".join(
        f'<div class="profile-education-item"><span>{icon(symbol)}</span><div><strong>{esc(title)}</strong><small>{esc(description)}</small></div></div>'
        for symbol, title, description in profile["education"]
    )
    interest_cards = "".join(
        f'<div class="profile-interest"><span>{icon(symbol)}</span><p>{esc(label)}</p></div>'
        for symbol, label in profile["interests"]
    )
    body = f"""
{icon_sprite}
<section class="profile-hero" aria-labelledby="profile-title">
  <div class="container profile-hero-inner">
    {breadcrumbs([('Главная', f'{base}index.html'), ('О враче', None)], base)}
    <div class="profile-hero-copy">
      <h1 id="profile-title">Анна Викторовна <br>Миронова — <br><em>врач-эндокринолог</em></h1>
      <p>{esc(profile['hero_lead'])}</p>
      <div class="profile-facts">
        <span>{icon('icon-video')}<span><strong>Онлайн</strong><small>для взрослых</small></span></span>
        <span>{icon('icon-calendar')}<span><strong>12 лет</strong><small>практики</small></span></span>
        <span>{icon('icon-clock')}<span><strong>60 минут</strong><small>первая консультация</small></span></span>
      </div>
      <div class="profile-hero-actions"><a class="btn btn-primary" href="{base}zapis/">Записаться на консультацию →</a><a class="btn btn-outline" href="{base}kontakty/">Связаться</a></div>
    </div>
  </div>
</section>
<div class="container profile-content">
  <section class="profile-intro profile-card" aria-labelledby="profile-about-title">
    <div class="profile-bio"><h2 id="profile-about-title">Обо мне</h2><span class="profile-heading-line"></span>{''.join(f'<p>{esc(paragraph)}</p>' for paragraph in profile['about_paragraphs'])}</div>
    <div class="profile-principles"><blockquote>{icon('icon-quote')}<p>Внимательно слушаю, подробно объясняю, помогаю найти решение.</p></blockquote><h3>Мои главные принципы</h3><div class="profile-principles-grid">{principle_cards}</div></div>
  </section>

  <section class="profile-experience profile-card" aria-labelledby="profile-experience-title">
    <div><h2 id="profile-experience-title">Клинический опыт</h2><ol>{experience_cards}</ol></div>
    <div class="profile-experience-badge">{icon('icon-calendar')}<strong>12 лет</strong><span>клинической практики</span></div>
  </section>

  <div class="profile-pair">
    <section class="profile-education profile-card" aria-labelledby="profile-education-title"><h2 id="profile-education-title">Образование и квалификация</h2><div class="profile-education-grid">{education_cards}</div></section>
    <section class="profile-approach profile-card" aria-labelledby="profile-approach-title"><h2 id="profile-approach-title">Мой подход к работе</h2><blockquote>{icon('icon-quote')}<p>{esc(profile['approach_quote'])}</p></blockquote><div class="profile-approach-tags"><span>{icon('icon-heart-hand')}Внимательное отношение</span><span>{icon('icon-shield')}Обоснованные решения</span></div></section>
  </div>

  <section class="profile-interests profile-card" aria-labelledby="profile-interests-title"><div><h2 id="profile-interests-title">Профессиональные интересы</h2><span class="profile-heading-line"></span><p>{esc(profile['interests_intro'])}</p></div><div class="profile-interest-grid">{interest_cards}</div></section>

  <section class="profile-documents profile-card" id="documents" aria-labelledby="profile-documents-title"><div><h2 id="profile-documents-title">Документы</h2><p>{esc(profile['documents_note'])}</p><a href="{base}dokumenty/">Подробнее о документах →</a></div><div class="profile-doc-grid">{doc_cards}</div></section>

  <div class="profile-pair profile-media-row">
    <section class="profile-video profile-card" aria-labelledby="profile-video-title"><div><h2 id="profile-video-title">Видеообращение врача</h2><p>{esc(profile['video_note'])}</p><a href="{base}kontakty/">Задать вопрос →</a></div><img src="{base}assets/img/doctor-about-330.webp" width="330" height="412" alt="Портрет врача-эндокринолога" loading="lazy"></section>
    <section class="profile-reviews profile-card" aria-labelledby="profile-reviews-title"><h2 id="profile-reviews-title">Отзывы пациентов</h2><p>{esc(profile['reviews_note'])}</p><a class="btn btn-outline" href="{base}otzyvy/">Перейти к отзывам →</a></section>
  </div>

  <section class="profile-booking" id="booking" aria-labelledby="profile-booking-title"><div class="profile-booking-copy"><h2 id="profile-booking-title">Записаться<br>на консультацию</h2><p>Выберите удобное время на странице записи или оставьте контакт здесь.</p><p>Первичная консультация — 60 минут. Оплата после подтверждения времени.</p></div>{booking_form('o-vrache', 'Консультация', base)}</section>
</div>
"""
    write("o-vrache/index.html", page_shell(
        title="Анна Викторовна Миронова — врач-эндокринолог | Биография и образование",
        description="Биография, специализация, образование и подход к работе врача-эндокринолога Анны Мироновой.",
        canonical=page_url("o-vrache"), base=base, body=body,
        body_class="inner-page about-profile-page",
        extra_head=f'  <link rel="stylesheet" href="{base}about-profile.css?v=20261020c">',
    ))


def booking_page() -> None:
    base = "../"
    canonical = page_url("zapis")
    faq_html = "".join(
        f'<details{" open" if index == 0 else ""}><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>'
        for index, (question, answer) in enumerate(C.BOOKING["faq"])
    )
    steps_html = "".join(
        f'<div class="booking-step"><span>{index}</span><h3>{esc(title)}</h3><p>{esc(description)}</p></div>'
        for index, (title, description) in enumerate(C.BOOKING["steps"], start=1)
    )
    benefits_html = "".join(
        f'<div class="booking-benefit"><span class="booking-benefit-icon"><svg aria-hidden="true"><use href="{base}assets/icons.svg#{esc(icon)}"></use></svg></span>'
        f'<h3>{esc(title)}</h3><p>{esc(description)}</p></div>'
        for icon, title, description in C.BOOKING["benefits"]
    )
    prep_html = "".join(
        f'<div class="booking-prep-card"><h3>{esc(title)}</h3><p>{esc(description)}</p></div>'
        for title, description in C.BOOKING["prep"]
    )
    includes_html = "".join(f'<li>{esc(item)}</li>' for item in C.PRICES["primary_includes"])
    body = f"""
<section class="booking-hero" aria-labelledby="booking-title">
  <div class="container booking-hero-inner">
    {breadcrumbs([("Главная", f"{base}index.html"), ("Онлайн-запись", None)], base)}
    <div class="booking-hero-grid">
      <div class="booking-hero-copy">
        <p class="page-kicker">Онлайн-консультация</p>
        <h1 id="booking-title">Выберите день и время консультации</h1>
        <p class="lead">{esc(C.BOOKING['hero_lead'])}</p>
        <div class="booking-meta" aria-label="Параметры консультации">
          <span><svg aria-hidden="true"><use href="{base}assets/icons.svg#icon-video"></use></svg><span><strong>Онлайн</strong><small>по видеосвязи</small></span></span>
          <span><svg aria-hidden="true"><use href="{base}assets/icons.svg#icon-clock"></use></svg><span><strong>{esc(C.PRICES['primary_duration'])}</strong><small>длительность</small></span></span>
          <span><span class="booking-ruble" aria-hidden="true">₽</span><span><strong><span data-price="primary">{price('primary')}</span> ₽</strong><small>стоимость</small></span></span>
          <span><svg aria-hidden="true"><use href="{base}assets/icons.svg#icon-calendar"></use></svg><span><strong>МСК, UTC+3</strong><small>часовой пояс</small></span></span>
        </div>
      </div>
      <aside class="booking-hero-card" aria-label="Врач">
        <div>
          <p class="booking-hero-name">Анна Викторовна Миронова</p>
          <p class="booking-hero-role">Врач-эндокринолог · стаж 12 лет</p>
          <p class="booking-hero-card-note">Онлайн-консультации для взрослых · доказательный подход</p>
          <a class="text-link" href="{base}o-vrache/">Подробнее о враче →</a>
        </div>
      </aside>
    </div>
  </div>
</section>

<div class="container booking-content">

  <section class="booking-section" id="booking-form" aria-labelledby="schedule-title">
    <div class="booking-layout">
      <div class="booking-schedule">
        <div class="booking-schedule-head">
          <div>
            <p class="page-kicker">Расписание</p>
            <h2 id="schedule-title">Выберите день и время</h2>
          </div>
          <span class="booking-tz">МСК, UTC+3</span>
        </div>
        <p class="booking-schedule-intro">{esc(C.BOOKING['schedule_intro'])}</p>

        <div class="booking-days-row">
          <button class="booking-week-nav" type="button" data-booking-prev aria-label="Предыдущая неделя">‹</button>
          <div class="booking-days" data-booking-days role="group" aria-label="Дни недели"></div>
          <button class="booking-week-nav" type="button" data-booking-next aria-label="Следующая неделя">›</button>
        </div>
        <noscript><p class="booking-empty">Для выбора дня и времени включите JavaScript или напишите мне в мессенджер.</p></noscript>

        <div class="booking-times-head">
          <h3 data-booking-times-title>Варианты времени</h3>
          <span class="booking-available" data-booking-available></span>
        </div>
        <div class="booking-slot-groups" data-booking-slots></div>
        <p class="booking-slot-error" data-slot-error hidden>Сначала выберите день и время.</p>
        <p class="booking-empty" data-booking-empty hidden></p>

        <div class="booking-legend" aria-label="Обозначения">
          <span><i class="booking-dot booking-dot-free"></i>Можно выбрать</span>
          <span><i class="booking-dot booking-dot-selected"></i>Выбрано</span>
          <span><i class="booking-dot booking-dot-closed"></i>Недоступно</span>
        </div>
        <p class="booking-demo-note">{esc(C.BOOKING['schedule_note'])}</p>
      </div>

      <aside class="booking-side" aria-labelledby="booking-form-title">
        <div class="page-form-card final-form-card booking-page-card">
          <div class="booking-summary" aria-live="polite">
            <div class="booking-summary-top">
              <strong>Вы выбрали</strong>
              <a class="booking-proceed" href="#booking-form" data-booking-proceed>Изменить</a>
            </div>
            <p class="booking-summary-line"><svg aria-hidden="true"><use href="{base}assets/icons.svg#icon-calendar"></use></svg><span class="booking-summary-date" data-booking-summary-date>Сначала выберите день</span></p>
            <p class="booking-summary-line"><svg aria-hidden="true"><use href="{base}assets/icons.svg#icon-clock"></use></svg><span class="booking-summary-time" data-booking-summary-time>Затем — удобное время</span></p>
            <p class="booking-summary-line"><svg aria-hidden="true"><use href="{base}assets/icons.svg#icon-video"></use></svg><span>Онлайн-консультация (видеосвязь)</span></p>
            <p class="booking-summary-line"><span class="booking-summary-ruble" aria-hidden="true">₽</span><strong><span data-price="primary">{price('primary')}</span> ₽</strong></p>
          </div>

          <h2 id="booking-form-title">Ваши данные</h2>

          <div class="page-form-success" data-form-success tabindex="-1" hidden>
            <h3>Заявка сохранена</h3>
            <p>Вы выбрали: <strong data-booking-success-slot>время не выбрано</strong>.</p>
            <p>{esc(C.BOOKING['success'])}</p>
            <button class="btn btn-ghost" type="button" data-form-reset>Выбрать другое время</button>
          </div>

          <form class="page-form" data-form="booking-page" data-requires-slot="true" novalidate>
            <input type="hidden" name="source" value="booking-page">
            <input type="hidden" name="date" value="">
            <input type="hidden" name="time" value="">
            <input type="hidden" name="weekday" value="">

            <div class="page-field">
              <label for="booking-name">Имя <span class="booking-required">*</span></label>
              <input id="booking-name" name="name" type="text" autocomplete="name" placeholder="Например, Екатерина" required>
            </div>
            <div class="page-field">
              <label for="booking-phone">Телефон <span class="booking-required">*</span></label>
              <input id="booking-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" data-phone required>
            </div>
            <div class="page-field">
              <label for="booking-email">Email <span>необязательно</span></label>
              <input id="booking-email" name="email" type="email" autocomplete="email" placeholder="example@mail.ru">
            </div>

            <label class="consent-line">
              <input type="checkbox" name="consent" required>
              <span>Согласен с <a href="{base}politika-konfidencialnosti/">политикой конфиденциальности</a> и <a href="{base}soglasie-na-obrabotku-dannyh/">обработкой персональных данных</a>.</span>
            </label>

            <button class="btn btn-primary booking-submit" type="submit" data-booking-submit disabled>Сначала выберите время</button>
            <p class="form-error" data-form-error hidden>Проверьте имя, телефон, email и согласие на обработку данных.</p>
            <p class="booking-slot-error" data-slot-error-form hidden>Выберите день и время в расписании.</p>
            <p class="form-note">{esc(C.BOOKING['form_note'])}</p>
          </form>
        </div>
      </aside>
    </div>
  </section>

  <section class="booking-benefits" aria-label="Преимущества онлайн-консультации">
    {benefits_html}
  </section>

  <section class="booking-section booking-process" aria-labelledby="booking-steps-title">
    <img src="{base}assets/img/booking-video-v2.webp" width="1448" height="1086" alt="Иллюстрация видеоконсультации с врачом-эндокринологом" loading="lazy">
    <div class="booking-process-content">
      <p class="page-kicker">Просто и удобно</p>
      <h2 id="booking-steps-title">Как проходит<br>онлайн-консультация</h2>
      <div class="booking-steps-grid">{steps_html}</div>
    </div>
  </section>

  <section class="booking-section booking-includes" aria-labelledby="booking-includes-title">
    <div>
      <p class="page-kicker">Стоимость консультации</p>
      <h2 id="booking-includes-title">Что входит в первичный приём</h2>
      <p>{esc(C.BOOKING['includes_intro'])}</p>
      <a class="text-link" href="{base}ceny/">Все цены и условия →</a>
    </div>
    <ul class="check-list">{includes_html}</ul>
  </section>

  <section class="booking-section booking-prep" aria-labelledby="booking-prep-title">
    <div class="booking-section-head">
      <p class="page-kicker">Подготовка</p>
      <h2 id="booking-prep-title">Что может пригодиться</h2>
      <p>{esc(C.BOOKING['prep_intro'])}</p>
    </div>
    <div class="booking-prep-grid">
      {prep_html}
    </div>
    <p class="booking-format-note">{esc(C.BOOKING['format_note'])}</p>
  </section>

  <section class="booking-section booking-info" aria-labelledby="booking-info-title">
    <div class="booking-info-grid">
      <div class="booking-info-card">
        <p class="page-kicker">Оплата и перенос</p>
        <h2 id="booking-info-title">Спокойно и без сюрпризов</h2>
        <ul class="check-list">
          <li>Стоимость первичной консультации — <strong><span data-price="primary">{price('primary')}</span> ₽</strong> за {esc(C.PRICES['primary_duration'])}.</li>
          <li>{esc(C.PRICES['payment'])}</li>
          <li>{esc(C.PRICES['cancel'])}</li>
          <li>На демонстрационном сайте оплата недоступна.</li>
        </ul>
        <p class="booking-emergency">При острой боли, затруднении дыхания, потере сознания или другом неотложном состоянии звоните <a href="tel:103">103</a> или <a href="tel:112">112</a>.</p>
      </div>
      <div class="booking-faq" aria-labelledby="booking-faq-title">
        <p class="page-kicker">Вопросы</p>
        <h2 id="booking-faq-title">Частые вопросы о записи</h2>
        {faq_html}
      </div>
    </div>
  </section>

  <section class="booking-help" id="booking-help" aria-labelledby="booking-help-title">
    <div>
      <p class="page-kicker">Нужна помощь</p>
      <h2 id="booking-help-title">Не нашли удобное время?</h2>
      <p>{esc(C.BOOKING['help'])}</p>
    </div>
    <div class="booking-help-links">
      <a class="btn btn-primary" href="https://wa.me/{esc(C.CONTACT['phone_href'].replace('+', ''))}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="btn btn-outline" href="tel:{esc(C.CONTACT['phone_href'])}">{esc(C.CONTACT['phone'])}</a>
      <a class="text-link" href="{base}kontakty/">Все контакты →</a>
    </div>
  </section>
</div>
"""
    write("zapis/index.html", page_shell(
        title="Онлайн-запись на консультацию эндокринолога | Анна Миронова",
        description="Выберите день и время онлайн-консультации эндокринолога Анны Мироновой. Расписание на неделю, стоимость, подготовка и правила переноса записи.",
        canonical=canonical,
        base=base,
        body=body,
        body_class="inner-page booking-page",
        json_ld=[json_breadcrumbs([("Главная", f"{BASE_URL}/"), ("Онлайн-запись", canonical)])],
        extra_head=f'  <link rel="stylesheet" href="{base}booking.css?v=20261020m">',
        extra_scripts=f'  <script src="{base}booking.js?v={VERSION}" defer></script>',
    ))


def prices_page() -> None:
    base = "../"
    body = f"""
<div class="price-cards">
  <div class="price-card price-card-primary">
    <h2>Первичная онлайн-консультация</h2>
    <p class="price-note">Для первого разбора ситуации</p>
    <div class="price-line"><strong data-price="primary">{price('primary')}</strong><span>₽ / 60 минут</span></div>
    {lead_list(C.PRICES['primary_includes'])}
    <a class="btn btn-primary" href="{base}zapis/">Записаться</a>
  </div>
  <div class="price-card">
    <h2>Повторная консультация</h2>
    <p class="price-note">Для тех, кто уже был на приёме</p>
    <div class="price-line"><strong data-price="followup">{price('followup')}</strong><span>₽ / 30 минут</span></div>
    {lead_list(C.PRICES['followup_includes'])}
    <a class="btn btn-ghost" href="#booking">Записаться</a>
  </div>
</div>
<div class="prose price-prose">
  <h2>Что входит в стоимость</h2>
  <p>В стоимость входит время консультации, разбор предоставленных материалов, объяснение показателей и краткое резюме с планом дальнейших шагов. Стоимость не зависит от количества вопросов, но если вопросов слишком много, может потребоваться повторная встреча.</p>
  <h2>Порядок оплаты</h2>
  <p>После согласования времени вы получаете подтверждение и ссылку на оплату. Запись считается подтверждённой после оплаты. Не отправляйте оплату по непроверенным реквизитам.</p>
  <h2>Отмена, перенос и возврат</h2>
  <p>{esc(C.PRICES['cancel'])} {esc(C.PRICES['refund'])}</p>
  <p>Если консультация не состоялась по технической причине на стороне врача, время переносится или оплата возвращается по согласованию.</p>
  <h2>Дополнительные услуги</h2>
  <p>Отдельные виды исследований, анализов и очных приёмов в стоимость онлайн-консультации не входят. Если для решения вопроса нужен очный специалист, я объясню, куда обратиться.</p>
</div>
<div class="table-wrap"><table class="price-table"><thead><tr><th>Услуга</th><th>Формат</th><th>Стоимость</th></tr></thead><tbody>
<tr><td>Первичная онлайн-консультация</td><td>60 минут, видеосвязь</td><td><span data-price="primary">{price('primary')}</span> ₽</td></tr>
<tr><td>Повторная онлайн-консультация</td><td>30 минут, видеосвязь</td><td><span data-price="followup">{price('followup')}</span> ₽</td></tr>
</tbody></table></div>
<div class="cta-band"><div><h2>Остались вопросы по оплате?</h2><p>Напишите в мессенджер или оставьте заявку — уточним детали до записи.</p></div><a class="btn btn-primary" href="{base}kontakty/">Связаться</a></div>
<p class="form-note">Цены указаны в рублях. Правила оказания услуг, отмены и возврата уточняются в договоре и документах исполнителя. Перед запуском проверьте юридические формулировки.</p>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Выберите формат и оставьте контакт.</p>{lead_list(['Первичная — 60 минут', 'Повторная — 30 минут', 'Оплата после подтверждения'])}</div>{booking_form('ceny', 'Консультация', base)}</div></section>
"""
    section_page(
        path="ceny",
        title="Цены на онлайн-консультацию эндокринолога | Анна Миронова",
        h1="Цены и условия",
        lead="Прозрачная стоимость первичной и повторной консультации, порядок оплаты и правила переноса.",
        body=body, base=base,
    )


def reviews_page() -> None:
    base = "../"
    body = f"""
<div class="review-empty">
  <h2>Отзывы без вымышленных историй</h2>
  <p>На сайте публикуются только отзывы, которые можно подтвердить и на публикацию которых есть согласие автора. Пока подтверждённых отзывов нет — здесь не будет придуманных оценок, рейтингов и «историй успеха».</p>
  <p>Если вы были на консультации и хотите оставить обратную связь, используйте форму ниже. Отзыв появится после модерации и проверки согласия.</p>
</div>
<div class="review-policy">
  <div><strong>Что публикуем</strong><p>Текст отзыва, разрешённое автором имя или инициалы, дату и тему обращения без медицинских подробностей.</p></div>
  <div><strong>Что не публикуем</strong><p>Диагнозы, результаты анализов, данные третьих лиц и обещания одинакового результата другим пациентам.</p></div>
  <div><strong>Внешние площадки</strong><p>Ссылки на профили появятся после подтверждения. Сейчас можно проверить информацию о враче в открытых источниках.</p></div>
</div>
<div class="review-form-wrap">
  <h2>Оставить отзыв</h2>
  <p>Форма демонстрационная: текст сохраняется только в этой вкладке и не отправляется на сервер.</p>
  <div class="review-success" data-review-success role="status" aria-live="polite" hidden>Спасибо. В рабочей версии отзыв уйдёт на модерацию, а мы свяжемся с вами для подтверждения согласия.</div>
  <form class="page-form" data-review-form>
    <div class="form-row-2">
      <div class="page-field"><label for="review-name">Имя или инициалы</label><input id="review-name" name="review-name" type="text" required placeholder="Как подписать отзыв"></div>
      <div class="page-field"><label for="review-topic">Тема обращения</label><select id="review-topic" name="review-topic"><option>Щитовидная железа</option><option>Вес и обмен веществ</option><option>Диабет</option><option>Гормоны</option><option>Другое</option></select></div>
    </div>
    <div class="page-field"><label for="review-text">Текст отзыва</label><textarea id="review-text" name="review-text" required placeholder="Что было важно для вас? Не указывайте диагнозы и личные медицинские данные."></textarea></div>
    <label class="consent-line"><input type="checkbox" required><span>Согласен на публикацию отзыва после модерации и обработку персональных данных.</span></label>
    <button class="btn btn-primary" type="submit">Отправить на модерацию</button>
    <p class="form-note">Не публикуйте медицинские сведения, которые не хотите раскрывать.</p>
  </form>
  <button class="btn btn-ghost" type="button" data-review-reset hidden>Оставить ещё один отзыв</button>
</div>
<div class="cta-band"><div><h2>Хотите обсудить свой вопрос?</h2><p>Консультация — не публичный отзыв и не обещание результата.</p></div><a class="btn btn-primary" href="{base}zapis/">Записаться</a></div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Оставьте контакт — согласуем время.</p>{lead_list(['Онлайн-формат', 'Без публикации ваших данных', 'Оплата после подтверждения'])}</div>{booking_form('otzyvy', 'Консультация', base)}</div></section>
"""
    section_page(
        path="otzyvy",
        title="Отзывы о консультациях — порядок публикации | Анна Миронова",
        h1="Отзывы",
        lead="Прозрачный порядок обратной связи без вымышленных оценок и медицинских подробностей.",
        body=body, base=base,
    )


def contacts_page() -> None:
    base = "../"
    body = f"""
<div class="contact-grid">
  <div class="contact-card"><h2>Связаться</h2><a class="big-link" href="tel:{C.CONTACT['phone_href']}">{C.CONTACT['phone']}</a><a href="mailto:{C.CONTACT['email']}">{C.CONTACT['email']}</a><p>{C.CONTACT['hours']}</p><p>{C.CONTACT['response']}</p></div>
  <div class="contact-card"><h2>Мессенджеры</h2><a href="{C.CONTACT['whatsapp']}" target="_blank" rel="noopener">WhatsApp</a><a href="{C.CONTACT['telegram']}" target="_blank" rel="noopener">Telegram</a><p class="form-note">Не отправляйте в мессенджер медицинские документы без необходимости. Для консультации предусмотрена отдельная форма.</p></div>
  <div class="contact-card"><h2>Формат</h2><p>{C.CONTACT['region']}</p><p>Онлайн по видеосвязи. Физический адрес и данные исполнителя указываются в соответствии с фактическими юридическими данными.</p></div>
  <div class="contact-card"><h2>Документы</h2><a href="{base}dokumenty/">Документы и лицензии</a><a href="{base}politika-konfidencialnosti/">Политика конфиденциальности</a><a href="{base}soglasie-na-obrabotku-dannyh/">Согласие на обработку данных</a></div>
</div>
<div class="contact-note">Перед публикацией сайта заполните юридические реквизиты, фактический адрес (если он требуется), лицензию и контакты. Сейчас используются демонстрационные данные.</div>
<div class="prose"><h2>Как проходит запись</h2><p>Оставьте заявку на сайте или напишите в мессенджер. Администратор согласует время, формат связи и условия оплаты. После подтверждения вы получите инструкцию по подключению.</p><h2>Экстренные ситуации</h2><p>Сайт не предназначен для неотложной помощи. При боли в груди, выраженной одышке, спутанности сознания, очень высокой глюкозе, рвоте или потере сознания звоните в скорую помощь.</p></div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Обратная связь</p><h2>Написать или записаться</h2><p>Оставьте контакт — согласуем время и ответим на организационные вопросы.</p>{lead_list(['Ответ в течение рабочего дня', 'Онлайн-формат', 'Без отправки медицинских данных через форму'])}</div>{booking_form('kontakty', 'Обратная связь', base)}</div></section>
"""
    section_page(
        path="kontakty",
        title="Контакты врача-эндокринолога Анны Мироновой",
        h1="Контакты",
        lead="Телефон, мессенджеры, почта и часы обработки заявок. Онлайн-консультации для взрослых.",
        body=body, base=base,
    )


def faq_page() -> None:
    base = "../"
    half = (len(C.FAQ) + 1) // 2
    left = faq_html(C.FAQ[:half], "faq-left")
    right = faq_html(C.FAQ[half:], "faq-right", open_first=False)
    body = f"""
<div class="faq-page-grid">{left}{right}</div>
<div class="cta-band"><div><h2>Не нашли ответ?</h2><p>Задайте вопрос на консультации или напишите в мессенджер.</p></div><a class="btn btn-primary" href="{base}zapis/">Записаться</a></div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Оставьте контакт — согласуем время.</p>{lead_list(['Первичная — 60 минут', 'Повторная — 30 минут', 'Оплата после подтверждения'])}</div>{booking_form('faq', 'Вопросы и ответы', base)}</div></section>
"""
    ld = [{
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in C.FAQ],
    }]
    section_page(
        path="faq",
        title="Вопросы и ответы об онлайн-консультации эндокринолога | Анна Миронова",
        h1="Вопросы и ответы",
        lead="Что важно знать о формате, оплате, подготовке и ограничениях онлайн-консультации.",
        body=body, base=base, json_ld=ld,
    )


def documents_page() -> None:
    base = "../"
    docs = [
        ("Диплом врача", "Лечебное дело"),
        ("Аккредитация", "Эндокринология"),
        ("Сертификат специалиста", "Эндокринология"),
        ("Повышение квалификации", "Регулярное обучение"),
    ]
    cards = "".join(f"""
<button class="doc-card" type="button" data-doc-preview data-doc-title="{esc(title)}" data-doc-card>
  <span class="doc-sheet"><span>РОССИЙСКАЯ ФЕДЕРАЦИЯ</span><strong>{esc(title)}</strong><small>{esc(sub)}</small></span>
  <span class="doc-caption">{esc(title)}</span>
</button>""" for title, sub in docs)
    body = f"""
<div class="prose"><p>Здесь собраны документы об образовании и квалификации. Нажмите на карточку, чтобы открыть увеличенный просмотр. Изображения демонстрационные; перед публикацией замените их на реальные сканы.</p></div>
<div class="doc-grid">{cards}</div>
<div class="prose"><h2>Лицензия и юридическая информация</h2><p>{esc(C.BRAND['operator'])}. {esc(C.BRAND['license'])}. {esc(C.BRAND['inn'])}. {esc(C.BRAND['ogrnip'])}.</p><p>Медицинская деятельность ведётся в соответствии с законодательством РФ. Онлайн-консультация не заменяет очный приём, если он необходим.</p><h2>Правовые документы</h2><ul><li><a href="{base}politika-konfidencialnosti/">Политика конфиденциальности</a></li><li><a href="{base}soglasie-na-obrabotku-dannyh/">Согласие на обработку персональных данных</a></li><li><a href="{base}ceny/">Цены, оплата и возврат</a></li></ul></div>
<section class="page-booking" id="booking"><div class="container page-booking-grid"><div class="page-booking-copy"><p class="page-kicker">Запись</p><h2>Записаться на консультацию</h2><p>Оставьте контакт — согласуем время.</p></div>{booking_form('dokumenty', 'Консультация', base)}</div></section>
"""
    section_page(
        path="dokumenty",
        title="Документы и квалификация врача | Анна Миронова",
        h1="Документы и квалификация",
        lead="Образование, аккредитация и юридическая информация исполнителя.",
        body=body, base=base,
    )


def legal_page(path: str, title: str, lead: str, content: str, nav: list[tuple[str, str]]) -> None:
    base = "../"
    nav_html = "".join(f'<a href="#{anchor}">{esc(label)}</a>' for anchor, label in nav)
    body = f"""
<div class="container">
  {breadcrumbs([('Главная', f'{base}index.html'), (title, None)], base)}
  <header class="page-hero"><p class="page-kicker">Правовая информация</p><h1>{esc(title)}</h1><p class="lead">{esc(lead)}</p></header>
  <div class="legal-layout">
    <nav class="legal-nav" aria-label="Содержание документа">{nav_html}</nav>
    <article class="prose">{content}</article>
  </div>
</div>"""
    write(f"{path}/index.html", page_shell(
        title=f"{title} | Анна Миронова",
        description=lead,
        canonical=page_url(path),
        base=base,
        body=body,
        body_class="inner-page legal-page",
    ))


def privacy_page() -> None:
    content = f"""
<h2 id="general">1. Общие положения</h2>
<p>Настоящая политика описывает, какие данные может получать сайт персонального сайта врача-эндокринолога, как они используются и какие права есть у пользователя. Документ является демонстрационным шаблоном: перед публикацией его нужно адаптировать под фактические процессы, CMS, аналитику и требования законодательства РФ.</p>
<h2 id="data">2. Какие данные обрабатываются</h2>
<p>Через форму записи могут обрабатываться имя, телефон, предпочтительный способ связи и тема обращения. Не отправляйте через форму медицинские документы, результаты анализов и подробности здоровья. Если такие данные потребуются для консультации, используйте согласованный защищённый канал.</p>
<h2 id="purpose">3. Цели обработки</h2>
<ul><li>Связаться по заявке и согласовать время консультации.</li><li>Ответить на организационные вопросы.</li><li>Вести документацию, если это требуется по закону и договору.</li><li>Улучшать работу сайта в обезличенном виде.</li></ul>
<h2 id="basis">4. Правовые основания</h2>
<p>Обработка осуществляется на основании согласия пользователя, а также в случаях, предусмотренных законодательством. Согласие оформляется отдельно и может быть отозвано.</p>
<h2 id="storage">5. Хранение и защита</h2>
<p>Данные хранятся не дольше, чем необходимо для целей обработки, если закон не требует иного. Доступ ограничивается уполномоченными лицами. При использовании сторонних сервисов должны применяться договоры и меры защиты, соответствующие требованиям.</p>
<h2 id="cookies">6. Cookies и аналитика</h2>
<p>Сайт может использовать технические cookies для работы интерфейса. Аналитика в демонстрационной версии не подключена. Перед добавлением аналитики нужно обновить политику и получить необходимые согласия.</p>
<h2 id="rights">7. Права пользователя</h2>
<p>Вы можете запросить информацию об обработке своих данных, уточнение, исправление или удаление, а также отозвать согласие, направив запрос на {esc(C.CONTACT['email'])}.</p>
<h2 id="contacts">8. Контакты</h2>
<p>Оператор: {esc(C.BRAND['operator'])}. Электронная почта: {esc(C.CONTACT['email'])}. Телефон: {esc(C.CONTACT['phone'])}. Реквизиты и адрес уточняются.</p>
<p class="form-note">Шаблон не является юридической консультацией. Перед запуском проверьте документ у юриста и укажите фактические данные.</p>
"""
    legal_page("politika-konfidencialnosti", "Политика конфиденциальности", "Какие данные обрабатываются на сайте и как их защитить.", content, [
        ("general", "Общие положения"), ("data", "Какие данные"), ("purpose", "Цели"), ("basis", "Основания"), ("storage", "Хранение"), ("cookies", "Cookies"), ("rights", "Права"), ("contacts", "Контакты"),
    ])


def consent_page() -> None:
    content = f"""
<h2 id="subject">1. Предмет согласия</h2>
<p>Пользователь даёт согласие на обработку персональных данных: имени, телефона, предпочтительного способа связи и темы обращения — для рассмотрения заявки и согласования консультации.</p>
<h2 id="actions">2. Действия с данными</h2>
<p>Сбор, запись, систематизация, хранение, уточнение, использование, обезличивание, блокирование и удаление данных. Обработка может выполняться как с использованием средств автоматизации, так и без них.</p>
<h2 id="purpose">3. Цель</h2>
<p>Связаться по заявке, согласовать время и формат консультации, ответить на организационные вопросы. Данные не используются для рекламы без отдельного согласия.</p>
<h2 id="medical">4. Медицинские данные</h2>
<p>Форма не предназначена для передачи медицинских документов и подробностей здоровья. Для обсуждения клинической информации используется согласованный защищённый канал после записи.</p>
<h2 id="term">5. Срок и отзыв</h2>
<p>Согласие действует до его отзыва. Отозвать согласие можно, направив запрос на {esc(C.CONTACT['email'])}. Отзыв не влияет на обработку, которая уже выполнена на законных основаниях.</p>
<h2 id="operator">6. Оператор</h2>
<p>{esc(C.BRAND['operator'])}. Контакты: {esc(C.CONTACT['email'])}, {esc(C.CONTACT['phone'])}. Реквизиты уточняются.</p>
<p class="form-note">Демонстрационный шаблон. Перед запуском проверьте формулировки у юриста и настройте фактический сбор согласий.</p>
"""
    legal_page("soglasie-na-obrabotku-dannyh", "Согласие на обработку персональных данных", "Условия обработки данных, которые вы отправляете через формы сайта.", content, [
        ("subject", "Предмет"), ("actions", "Действия"), ("purpose", "Цель"), ("medical", "Медицинские данные"), ("term", "Срок и отзыв"), ("operator", "Оператор"),
    ])


def not_found_page() -> None:
    base = ""
    body = f"""
<div class="container">
  <header class="page-hero"><p class="page-kicker">404</p><h1>Страница не найдена</h1><p class="lead">Возможно, ссылка устарела или в адресе есть опечатка. Начните с главной или выберите нужный раздел.</p></header>
  <div class="cards-grid">
    <a class="service-card" href="{base}uslugi/"><h3>Услуги</h3><p>Онлайн-консультации и разбор анализов.</p><div class="card-foot"><span>Перейти</span><span class="card-arrow">→</span></div></a>
    <a class="service-card" href="{base}zabolevaniya/"><h3>Заболевания</h3><p>Информация о щитовидной железе, диабете и обмене веществ.</p><div class="card-foot"><span>Перейти</span><span class="card-arrow">→</span></div></a>
    <a class="service-card" href="{base}stati/"><h3>Статьи</h3><p>Экспертные материалы и ответы на вопросы.</p><div class="card-foot"><span>Перейти</span><span class="card-arrow">→</span></div></a>
    <a class="service-card" href="{base}kontakty/"><h3>Контакты</h3><p>Связаться и записаться на консультацию.</p><div class="card-foot"><span>Перейти</span><span class="card-arrow">→</span></div></a>
  </div>
</div>"""
    write("404.html", page_shell(
        title="Страница не найдена | Анна Миронова",
        description="Страница не найдена. Перейдите к услугам, заболеваниям, статьям или контактам.",
        canonical=f"{BASE_URL}/404.html",
        base=base, body=body,
    ))


def write_site_data() -> None:
    payload = {
        "brand": C.BRAND,
        "contact": C.CONTACT,
        "prices": C.PRICES,
        "services": [
            {"slug": item["slug"], "title": item["title"], "short": item["short"], "group": item["group"], "icon": item["icon"]}
            for item in C.SERVICES
        ],
        "diseases": [
            {"slug": item["slug"], "title": item["title"], "short": item.get("short", item["lead"]), "group": item["group"], "icon": item["icon"]}
            for item in C.DISEASES
        ],
        "articles": [
            {"slug": item["slug"], "title": item["title"], "category": item["category"]}
            for item in C.ARTICLES
        ],
    }
    js = "window.SITE_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    write("assets/js/site-data.js", js)


def write_sitemap() -> None:
    urls = [f"{BASE_URL}/"]
    urls += [f"{BASE_URL}/{path}/" for path in [
        "uslugi", "zabolevaniya", "o-vrache", "ceny", "otzyvy", "stati", "kontakty", "faq", "zapis",
        "politika-konfidencialnosti", "soglasie-na-obrabotku-dannyh", "dokumenty",
    ]]
    urls += [f"{BASE_URL}/uslugi/{item['slug']}/" for item in C.SERVICES]
    urls += [f"{BASE_URL}/zabolevaniya/{item['slug']}/" for item in C.DISEASES]
    urls += [f"{BASE_URL}/stati/{item['slug']}/" for item in C.ARTICLES]
    entries = "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n')


def write_redirects() -> None:
    redirects = {
        "blog.html": "stati/",
        "article-ttg.html": "stati/povyshen-ttg/",
        "article-insulin.html": "stati/insulinorezistentnost/",
        "article-questions.html": "stati/voprosy-endokrinologu/",
        "privacy.html": "politika-konfidencialnosti/",
        "consent.html": "soglasie-na-obrabotku-dannyh/",
        "legal.html": "ceny/",
    }
    for old, new in redirects.items():
        target = f"{BASE_URL}/{new}"
        write(old, f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="{target}"><title>Переход…</title></head><body><p>Страница переехала: <a href="{new}">{new}</a></p></body></html>""")


def main() -> None:
    write_site_data()
    services_index()
    diseases_index()
    for item in C.SERVICES:
        service_page(item)
    for item in C.DISEASES:
        disease_page(item)
    articles_index()
    for item in C.ARTICLES:
        article_page(item)
    about_page()
    booking_page()
    prices_page()
    reviews_page()
    contacts_page()
    faq_page()
    documents_page()
    privacy_page()
    consent_page()
    not_found_page()
    write_sitemap()
    write_redirects()
    count = len(C.SERVICES) + len(C.DISEASES) + len(C.ARTICLES) + 13
    print(f"OK: generated {count} pages + site-data.js + sitemap.xml")


if __name__ == "__main__":
    main()
