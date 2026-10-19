/* Shared site shell: header, mega menu, footer, prices, document preview. */
(function () {
  "use strict";

  const data = window.SITE_DATA;
  if (!data) return;

  const base = document.body.dataset.base || "";
  const url = (path) => `${base}${path}`;
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

  const icon = (name, className = "") =>
    `<svg class="icon ${className}" aria-hidden="true"><use href="${url("assets/icons.svg?v=20261020h")}#${name}"></use></svg>`;
  const chevron = '<svg class="nav-chevron" width="10" height="6" viewBox="0 0 10 6" aria-hidden="true"><path d="m1 1 4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const formatPrice = (value) => new Intl.NumberFormat("ru-RU").format(value);
  const bookingHref = document.body.classList.contains("booking-page") ? "#booking-form" : url("zapis/");

  const services = data.services || [];
  const diseases = data.diseases || [];
  const servicesGroups = ["Консультации", "Направления"].map((group) => ({
    title: group,
    items: services.filter((item) => item.group === group),
  }));
  const diseaseColumns = [
    { title: "Щитовидная железа", items: diseases.filter((item) => item.group === "Щитовидная железа") },
    {
      title: "Обмен веществ и углеводный обмен",
      items: diseases.filter((item) => item.group === "Обмен веществ" || item.group === "Углеводный обмен"),
    },
    { title: "Гормональные нарушения", items: diseases.filter((item) => item.group === "Гормональные нарушения") },
  ];

  function serviceLink(item, className = "mega-link") {
    return `<a class="${className}" href="${url(`uslugi/${item.slug}/`)}">${icon(item.icon, "mega-icon")}<span><strong>${item.title}</strong><small>${item.short}</small></span></a>`;
  }

  function diseaseLink(item) {
    return `<a class="mega-link mega-link-compact" href="${url(`zabolevaniya/${item.slug}/`)}"><span class="mega-dot" aria-hidden="true"></span><span>${item.title}</span></a>`;
  }

  function renderHeader() {
    const host = $("#site-header");
    if (!host) return;

    const nav = `
      <nav class="site-nav" aria-label="Основная навигация">
        <div class="nav-item nav-item-mega">
          <button class="nav-link nav-mega-toggle" type="button" data-mega-toggle="services" aria-expanded="false" aria-controls="mega-services" aria-haspopup="true">Услуги${chevron}</button>
          <div class="mega-panel" id="mega-services" data-mega-panel="services" hidden>
            <div class="mega-top">
              <p class="mega-kicker">Направления консультаций</p>
              <a class="mega-all" href="${url("uslugi/")}">Все услуги ${icon("icon-arrow", "mega-arrow")}</a>
            </div>
            <div class="mega-grid mega-grid-services">
              ${servicesGroups.map((group) => `
                <div class="mega-column">
                  <p class="mega-column-title">${group.title}</p>
                  <div class="mega-links">${group.items.map((item) => serviceLink(item)).join("")}</div>
                </div>`).join("")}
              <div class="mega-promo">
                <span class="mega-promo-icon">${icon("icon-calendar-fill")}</span>
                <strong>Не знаете, с чего начать?</strong>
                <p>Первичная консультация поможет разобраться в ситуации и определить следующие шаги.</p>
                <a class="btn btn-primary" href="${url("uslugi/endokrinolog-online/")}">Подробнее об услуге</a>
                <a class="mega-promo-quiz" href="${url("index.html?quiz=1")}">Ответить на вопросы ${icon("icon-arrow")}</a>
              </div>
            </div>
          </div>
        </div>
        <div class="nav-item nav-item-mega">
          <button class="nav-link nav-mega-toggle" type="button" data-mega-toggle="diseases" aria-expanded="false" aria-controls="mega-diseases" aria-haspopup="true">Заболевания${chevron}</button>
          <div class="mega-panel" id="mega-diseases" data-mega-panel="diseases" hidden>
            <div class="mega-top">
              <p class="mega-kicker">Эндокринологические направления</p>
              <a class="mega-all" href="${url("zabolevaniya/")}">Все заболевания ${icon("icon-arrow", "mega-arrow")}</a>
            </div>
            <div class="mega-grid mega-grid-diseases">
              ${diseaseColumns.map((column) => `
                <div class="mega-column">
                  <p class="mega-column-title">${column.title}</p>
                  <div class="mega-links">${column.items.map((item) => diseaseLink(item)).join("")}</div>
                  ${column.title === "Гормональные нарушения" ? `<a class="mega-all mega-all-inline" href="${url("zabolevaniya/")}">Все заболевания ${icon("icon-arrow", "mega-arrow")}</a>` : ""}
                </div>`).join("")}
            </div>
          </div>
        </div>
        <a class="nav-link" href="${url("o-vrache/")}">О враче</a>
        <a class="nav-link" href="${url("ceny/")}">Цены</a>
        <a class="nav-link" href="${url("stati/")}">Статьи</a>
        <a class="nav-link" href="${url("kontakty/")}">Контакты</a>
      </nav>`;

    host.innerHTML = `
      <header class="site-header" data-header>
        <div class="container header-inner">
          <a class="brand" href="${url("index.html")}" aria-label="${data.brand.full_name} — на главную">
            <span class="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 40 40" fill="none"><path d="M31.8 8.2C22.7 8.9 14.9 12.3 11.1 19.3c-2.7 5-1.4 10.1 3 12.2 4.7 2.2 9.5-.2 11.4-5.2 2-5.2 1.1-11 5.3-18.1Z" stroke="currentColor" stroke-width="1.4"/><path d="M8.2 33.1c3.5-8.5 9.7-14.3 18.2-18.1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
            </span>
            <span class="brand-text"><strong>${data.brand.name}</strong><small>${data.brand.role}</small></span>
          </a>
          ${nav}
          <div class="header-actions">
            <a class="header-phone" href="tel:${data.contact.phone_href}">${icon("icon-phone")}<span><strong>${data.contact.phone}</strong><small>${data.contact.hours}</small></span></a>
            <a class="btn btn-primary header-cta" href="${bookingHref}">Записаться</a>
            <button class="menu-toggle" type="button" data-menu-toggle aria-controls="mobile-menu" aria-expanded="false">
              <span class="sr-only">Открыть меню</span>
              <svg class="icon" aria-hidden="true"><use href="${url("assets/icons.svg?v=20261020h")}#icon-menu"></use></svg>
            </button>
          </div>
        </div>
      </header>
      <div class="mobile-menu" id="mobile-menu" hidden>
        <div class="mobile-menu-head">
          <span>Меню</span>
          <button class="mobile-close" type="button" data-menu-close aria-label="Закрыть меню">${icon("icon-close")}</button>
        </div>
        <nav class="mobile-nav" aria-label="Мобильная навигация">
          <div class="mobile-group">
            <button type="button" class="mobile-group-toggle" data-mobile-accordion aria-expanded="false" aria-controls="mobile-services">Услуги${chevron}</button>
            <div class="mobile-submenu" id="mobile-services" hidden>
              <a href="${url("uslugi/")}">Все услуги</a>
              ${services.map((item) => `<a href="${url(`uslugi/${item.slug}/`)}">${item.title}</a>`).join("")}
            </div>
          </div>
          <div class="mobile-group">
            <button type="button" class="mobile-group-toggle" data-mobile-accordion aria-expanded="false" aria-controls="mobile-diseases">Заболевания${chevron}</button>
            <div class="mobile-submenu" id="mobile-diseases" hidden>
              <a href="${url("zabolevaniya/")}">Все заболевания</a>
              ${diseases.map((item) => `<a href="${url(`zabolevaniya/${item.slug}/`)}">${item.title}</a>`).join("")}
            </div>
          </div>
          <a href="${url("o-vrache/")}">О враче</a>
          <a href="${url("ceny/")}">Цены</a>
          <a href="${url("stati/")}">Статьи</a>
          <a href="${url("kontakty/")}">Контакты</a>
        </nav>
        <div class="mobile-menu-footer">
          <a class="btn btn-primary" href="${bookingHref}">Записаться на консультацию</a>
          <a class="mobile-phone" href="tel:${data.contact.phone_href}">${data.contact.phone}</a>
          <p>${data.contact.hours}</p>
        </div>
      </div>`;

    const normalise = (pathname) => pathname.replace(/index\.html$/, "").replace(/\/+$/, "") || "/";
    const currentPath = normalise(window.location.pathname);
    const homePath = normalise(new URL(url("index.html"), window.location.href).pathname);
    $$(".site-nav .nav-link", host).forEach((link) => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#")) return;
      const linkPath = normalise(new URL(href, window.location.href).pathname);
      if (linkPath === currentPath || (linkPath !== homePath && currentPath.startsWith(`${linkPath}/`))) {
        link.classList.add("is-active");
        link.setAttribute("aria-current", "page");
      }
    });
    $$("[data-mega-toggle]", host).forEach((button) => {
      const section = button.dataset.megaToggle === "services" ? "/uslugi" : "/zabolevaniya";
      if (currentPath.endsWith(section) || currentPath.includes(`${section}/`)) {
        button.classList.add("is-active");
      }
    });
  }

  function closeMega(panelKey, restoreFocus) {
    $$("[data-mega-panel]").forEach((panel) => {
      if (panelKey && panel.dataset.megaPanel !== panelKey) return;
      panel.hidden = true;
    });
    $$("[data-mega-toggle]").forEach((button) => {
      const isCurrent = !panelKey || button.dataset.megaToggle === panelKey;
      if (isCurrent) {
        button.setAttribute("aria-expanded", "false");
        if (restoreFocus) button.focus();
      }
    });
  }

  function openMega(button) {
    const key = button.dataset.megaToggle;
    const panel = $(`[data-mega-panel="${key}"]`);
    if (!panel) return;
    const willOpen = button.getAttribute("aria-expanded") !== "true";
    closeMega();
    if (!willOpen) return;
    panel.hidden = false;
    button.setAttribute("aria-expanded", "true");
  }

  function initMegaMenus() {
    $$("[data-mega-toggle]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        openMega(button);
      });
      button.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openMega(button);
          const panel = $(`[data-mega-panel="${button.dataset.megaToggle}"]`);
          const first = panel ? $("a, button", panel) : null;
          if (first) first.focus();
        }
      });
    });

    $$("[data-mega-panel]").forEach((panel) => {
      panel.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          const key = panel.dataset.megaPanel;
          closeMega(key, true);
          return;
        }
        if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
        const links = $$("a, button", panel).filter((item) => !item.hidden);
        if (!links.length) return;
        const current = links.indexOf(document.activeElement);
        let next = current;
        if (event.key === "ArrowDown") next = current < 0 ? 0 : (current + 1) % links.length;
        if (event.key === "ArrowUp") next = current <= 0 ? links.length - 1 : current - 1;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = links.length - 1;
        event.preventDefault();
        links[next].focus();
      });
      panel.addEventListener("click", (event) => {
        if (event.target.closest("a")) closeMega();
      });
    });

    document.addEventListener("click", (event) => {
      if (!event.target.closest(".site-header")) closeMega();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMega(null, false);
    });
  }

  function initMobileAccordions() {
    $$("[data-mobile-accordion]").forEach((button) => {
      button.addEventListener("click", () => {
        const panel = document.getElementById(button.getAttribute("aria-controls"));
        if (!panel) return;
        const open = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!open));
        panel.hidden = open;
      });
    });
    $$("[data-menu-close]").forEach((button) => {
      button.addEventListener("click", () => {
        const toggle = $("[data-menu-toggle]");
        if (toggle) toggle.click();
      });
    });
  }

  function renderFooter() {
    const host = $("#site-footer");
    if (!host) return;
    host.innerHTML = `
      <footer class="site-footer">
        <div class="container">
          <div class="footer-top">
            <div class="footer-brand">
              <a class="brand brand-footer" href="${url("index.html")}">
                <span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 40 40" fill="none"><path d="M31.8 8.2C22.7 8.9 14.9 12.3 11.1 19.3c-2.7 5-1.4 10.1 3 12.2 4.7 2.2 9.5-.2 11.4-5.2 2-5.2 1.1-11 5.3-18.1Z" stroke="currentColor" stroke-width="1.4"/><path d="M8.2 33.1c3.5-8.5 9.7-14.3 18.2-18.1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg></span>
                <span class="brand-text"><strong>${data.brand.name}</strong><small>${data.brand.role}</small></span>
              </a>
              <p>Онлайн-консультации для взрослых. Доказательная медицина, внимательный разговор и понятный план действий.</p>
              <a class="footer-quote" href="${url("index.html?quiz=1")}">Не знаете, нужен ли эндокринолог? Ответить на вопросы ${icon("icon-arrow")}</a>
            </div>
            <div class="footer-col">
              <h2>Услуги</h2>
              <a href="${url("uslugi/endokrinolog-online/")}">Онлайн-консультация</a>
              <a href="${url("uslugi/razbor-analizov/")}">Разбор анализов</a>
              <a href="${url("uslugi/povtornaya-konsultaciya/")}">Повторная консультация</a>
              <a href="${url("uslugi/")}">Все услуги</a>
            </div>
            <div class="footer-col">
              <h2>Информация</h2>
              <a href="${url("o-vrache/")}">О враче</a>
              <a href="${url("zabolevaniya/")}">Заболевания</a>
              <a href="${url("ceny/")}">Цены</a>
              <a href="${url("zapis/")}">Онлайн-запись</a>
              <a href="${url("stati/")}">Статьи</a>
              <a href="${url("faq/")}">Вопросы и ответы</a>
            </div>
            <div class="footer-col">
              <h2>Контакты</h2>
              <a href="tel:${data.contact.phone_href}">${data.contact.phone}</a>
              <a href="mailto:${data.contact.email}">${data.contact.email}</a>
              <a href="${data.contact.whatsapp}" target="_blank" rel="noopener">WhatsApp</a>
              <a href="${data.contact.telegram}" target="_blank" rel="noopener">Telegram</a>
              <span>${data.contact.hours}</span>
              <a class="footer-cta" href="${bookingHref}">Записаться на приём ${icon("icon-arrow")}</a>
            </div>
          </div>
          <div class="footer-legal">
            <div class="footer-legal-main">
              <p>${data.brand.operator}. ${data.brand.license}. ${data.contact.region}.</p>
              <p>Информация на сайте не заменяет консультацию врача и не является медицинской рекомендацией. При острых состояниях обращайтесь за неотложной помощью.</p>
            </div>
            <div class="footer-legal-links">
              <a href="${url("politika-konfidencialnosti/")}">Политика конфиденциальности</a>
              <a href="${url("soglasie-na-obrabotku-dannyh/")}">Согласие на обработку данных</a>
              <a href="${url("dokumenty/")}">Документы и лицензии</a>
            </div>
            <p class="footer-copy">© <span data-year>2026</span> ${data.brand.full_name}. Все права защищены. Сайт-демонстрация.</p>
          </div>
        </div>
      </footer>`;
  }

  function initPrices() {
    $$("[data-price]").forEach((element) => {
      const key = element.dataset.price;
      const value = data.prices[key];
      if (typeof value === "number") element.textContent = formatPrice(value);
    });
    $$("[data-duration]").forEach((element) => {
      const key = element.dataset.duration;
      if (data.prices[key]) element.textContent = data.prices[key];
    });
  }

  function initDocumentPreview() {
    if (!$("[data-doc-preview]")) return;
    const dialog = document.createElement("dialog");
    dialog.className = "site-doc-dialog";
    dialog.id = "site-doc-dialog";
    dialog.setAttribute("aria-label", "Просмотр документа");
    dialog.innerHTML = `
      <div class="site-doc-inner">
        <div class="site-doc-head">
          <div><p class="site-doc-kicker">Документ</p><h2 data-site-doc-title>Документ</h2></div>
          <button class="icon-btn" type="button" data-site-doc-close aria-label="Закрыть">${icon("icon-close")}</button>
        </div>
        <div class="site-doc-stage" data-site-doc-stage></div>
        <p class="site-doc-note">Демонстрационный просмотр. Оригиналы документов предоставляются по запросу.</p>
      </div>`;
    document.body.appendChild(dialog);

    $$("[data-doc-preview]").forEach((button) => {
      button.addEventListener("click", () => {
        const card = button.closest("[data-doc-card]") || button;
        const sheet = $(".doc-sheet", card);
        const stage = $("[data-site-doc-stage]", dialog);
        const title = $("[data-site-doc-title]", dialog);
        if (stage && sheet) stage.replaceChildren(sheet.cloneNode(true));
        if (title) title.textContent = button.dataset.docTitle || "Документ";
        dialog.showModal();
        document.body.classList.add("dialog-open");
        const close = $("[data-site-doc-close]", dialog);
        if (close) close.focus({ preventScroll: true });
      });
    });
    const close = () => {
      dialog.close();
      if (!document.querySelector("dialog[open]")) document.body.classList.remove("dialog-open");
    };
    $$("[data-site-doc-close]", dialog).forEach((button) => button.addEventListener("click", close));
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) close();
    });
    dialog.addEventListener("close", () => document.body.classList.remove("dialog-open"));
  }

  function initYear() {
    $$("[data-year]").forEach((element) => {
      element.textContent = String(new Date().getFullYear());
    });
  }

  renderHeader();
  renderFooter();
  initMegaMenus();
  initMobileAccordions();
  initPrices();
  initDocumentPreview();
  initYear();
})();
