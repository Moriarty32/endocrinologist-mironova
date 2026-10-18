/* =========================================================
   Анна Миронова — интерактивный прототип
   Vanilla JS, no dependencies.
   ========================================================= */

(() => {
  "use strict";

  const $ = (selector, context = document) => context.querySelector(selector);
  const $$ = (selector, context = document) => Array.from(context.querySelectorAll(selector));
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const liveRegion = $("#live-region");

  window.dataLayer = window.dataLayer || [];

  function track(event, params = {}) {
    window.dataLayer.push({ event, ...params });
    // Analytics integrations belong here (for example, Yandex Metrika).
    // Never pass quiz answers, topics, diagnoses or other medical content.
  }

  function announce(message) {
    if (!liveRegion) return;
    liveRegion.textContent = "";
    window.setTimeout(() => {
      liveRegion.textContent = message;
    }, 40);
  }

  function scrollToElement(element) {
    if (!element) return;
    element.scrollIntoView({
      behavior: prefersReducedMotion.matches ? "auto" : "smooth",
      block: "start",
    });
  }

  /* -------------------------------------------------------
     Header and mobile navigation
     ------------------------------------------------------- */

  const header = $("[data-header]");
  const menuToggle = $("[data-menu-toggle]");
  const mobileMenu = $("#mobile-menu");

  function setMenu(open) {
    if (!menuToggle || !mobileMenu) return;
    menuToggle.setAttribute("aria-expanded", String(open));
    mobileMenu.hidden = !open;
    menuToggle.classList.toggle("is-open", open);
    const label = $(".sr-only", menuToggle);
    if (label) label.textContent = open ? "Закрыть меню" : "Открыть меню";
    const icon = $("use", menuToggle);
    if (icon) {
      icon.setAttribute("href", open ? "assets/icons.svg#icon-close" : "assets/icons.svg#icon-menu");
    }
  }

  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener("click", () => {
      setMenu(menuToggle.getAttribute("aria-expanded") !== "true");
    });
    mobileMenu.addEventListener("click", (event) => {
      if (event.target.closest("a, button")) setMenu(false);
    });
    document.addEventListener("click", (event) => {
      if (mobileMenu.hidden) return;
      if (!header.contains(event.target)) setMenu(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !mobileMenu.hidden) {
        setMenu(false);
        menuToggle.focus();
      }
    });
    window.addEventListener("resize", () => {
      if (window.innerWidth > 980) setMenu(false);
    });
  }

  /* -------------------------------------------------------
     Phone mask and forms
     ------------------------------------------------------- */

  function phoneDigits(value) {
    return value.replace(/\D/g, "").replace(/^8/, "7");
  }

  function formatPhone(value) {
    let digits = phoneDigits(value);
    if (!digits) return "";
    if (!digits.startsWith("7")) digits = `7${digits}`;
    digits = digits.slice(0, 11);

    let result = "+7";
    if (digits.length > 1) result += ` (${digits.slice(1, 4)}`;
    if (digits.length >= 4) result += `) ${digits.slice(4, 7)}`;
    if (digits.length >= 7) result += `-${digits.slice(7, 9)}`;
    if (digits.length >= 9) result += `-${digits.slice(9, 11)}`;
    return result;
  }

  function isValidPhone(value) {
    const digits = phoneDigits(value);
    return digits.length === 11 && digits.startsWith("7");
  }

  $$("input[data-phone]").forEach((input) => {
    input.addEventListener("input", () => {
      const formatted = formatPhone(input.value);
      input.value = formatted;
      input.removeAttribute("aria-invalid");
    });
    input.addEventListener("blur", () => {
      if (input.value && !isValidPhone(input.value)) {
        input.setAttribute("aria-invalid", "true");
      }
    });
  });

  function addUtmFields(form) {
    const params = new URLSearchParams(window.location.search);
    ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"].forEach((key) => {
      const value = params.get(key);
      if (!value) return;
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = key;
      input.value = value.slice(0, 200);
      form.appendChild(input);
    });
  }

  function setFormTopic(topic) {
    $$("form[data-form]").forEach((form) => {
      const input = $('input[name="topic"]', form);
      if (input) input.value = topic;
      const label = $("[data-topic-label]", form);
      if (label) {
        label.textContent = topic ? `Тема обращения: ${topic}` : "";
        label.hidden = !topic;
      }
    });
  }

  function highlightBooking() {
    const card = $("#booking");
    if (!card) return;
    card.classList.remove("is-highlighted");
    // Restart the highlight if the user clicks another topic quickly.
    void card.offsetWidth;
    card.classList.add("is-highlighted");
    window.setTimeout(() => card.classList.remove("is-highlighted"), 1800);
  }

  $$("[data-topic]").forEach((element) => {
    element.addEventListener("click", (event) => {
      const topic = element.getAttribute("data-topic");
      if (!topic) return;
      setFormTopic(topic);
      highlightBooking();
      announce(`Тема обращения «${topic}» добавлена в форму записи.`);
      track("topic_select", { topic_selected: true, source: "card" });

      if (element.tagName !== "A") {
        event.preventDefault();
        scrollToElement($("#booking"));
        window.setTimeout(() => {
          const name = $("#hero-name");
          if (name) name.focus({ preventScroll: true });
        }, prefersReducedMotion.matches ? 50 : 550);
      }
    });
  });

  function bindForm(form) {
    addUtmFields(form);
    const card = form.closest(".booking-card, .final-form-card") || form.parentElement;
    const success = card ? $("[data-form-success]", card) : null;
    const error = $("[data-form-error]", form);
    const nameInput = $('input[name="name"]', form);
    const phoneInput = $('input[name="phone"]', form);
    const consent = $('input[name="consent"]', form);

    function clearError() {
      if (error) error.hidden = true;
      [nameInput, phoneInput].forEach((input) => {
        if (input) input.removeAttribute("aria-invalid");
      });
    }

    [nameInput, phoneInput].forEach((input) => {
      if (!input) return;
      input.addEventListener("input", () => {
        input.removeAttribute("aria-invalid");
        if (error) error.hidden = true;
      });
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!nameInput || !phoneInput || !consent) return;

      clearError();
      const nameValid = nameInput.value.trim().length >= 2;
      const phoneValid = isValidPhone(phoneInput.value);
      const consentValid = consent.checked;

      if (!nameValid) nameInput.setAttribute("aria-invalid", "true");
      if (!phoneValid) phoneInput.setAttribute("aria-invalid", "true");
      if (!consentValid) consent.setAttribute("aria-invalid", "true");

      if (!nameValid || !phoneValid || !consentValid) {
        if (error) error.hidden = false;
        const firstInvalid = !nameValid ? nameInput : !phoneValid ? phoneInput : consent;
        firstInvalid.focus();
        track("form_error", { form: form.dataset.form });
        return;
      }

      const data = new FormData(form);
      const lead = {
        name: String(data.get("name") || "").trim().slice(0, 80),
        phone: String(data.get("phone") || "").trim(),
        contact: String(data.get("contact") || "Телефон"),
        source: String(data.get("source") || form.dataset.form || "unknown"),
        createdAt: new Date().toISOString(),
      };

      try {
        // Demo only: non-medical lead fields stay in this tab's session storage.
        sessionStorage.setItem("demoLead", JSON.stringify(lead));
      } catch (storageError) {
        // Storage can be disabled; the success state still works.
      }

      track("form_submit", {
        form: data.get("source") || form.dataset.form,
        contact: lead.contact,
        topic_selected: Boolean(data.get("topic")),
      });

      form.hidden = true;
      if (card) card.classList.add("is-submitted");
      if (success) {
        success.hidden = false;
        success.focus({ preventScroll: true });
      }
      announce("Спасибо! Заявка сохранена в демонстрационной версии.");
    });

    const reset = card ? $("[data-form-reset]", card) : null;
    if (reset) {
      reset.addEventListener("click", () => {
        form.reset();
        form.hidden = false;
        if (success) success.hidden = true;
        if (card) card.classList.remove("is-submitted");
        setFormTopic("");
        const name = $('input[name="name"]', form);
        if (name) name.focus();
      });
    }
  }

  $$("form[data-form]").forEach(bindForm);

  /* -------------------------------------------------------
     Quiz
     ------------------------------------------------------- */

  const QUESTIONS = [
    {
      question: "Что вас беспокоит?",
      hint: "Можно выбрать несколько вариантов.",
      multi: true,
      options: [
        "Щитовидная железа",
        "Изменение веса",
        "Сахар крови / диабет",
        "Гормональные анализы",
        "Изменения самочувствия",
        "У меня уже есть диагноз",
        "Другая причина обращения",
      ],
    },
    {
      question: "Что лучше описывает вашу ситуацию?",
      hint: "Выберите один вариант.",
      multi: false,
      options: [
        "Хочу впервые разобраться с этим вопросом",
        "Уже обращался к врачу, остались вопросы",
        "Получил результаты анализов",
        "Хочу обсудить динамику ранее установленного заболевания",
        "Не уверен, к какому специалисту обратиться",
      ],
    },
    {
      question: "Есть ли у вас результаты обследований?",
      hint: "Можно выбрать несколько вариантов.",
      multi: true,
      options: [
        "Да, свежие анализы",
        "Есть анализы за предыдущие периоды",
        "Есть УЗИ или другие исследования",
        "Пока ничего не сдавал",
        "Не знаю, какие результаты нужны",
      ],
    },
    {
      question: "Что вы больше всего хотите получить от консультации?",
      hint: "Можно выбрать несколько вариантов.",
      multi: true,
      options: [
        "Понять значение анализов",
        "Обсудить жалобы",
        "Узнать, какие обследования могут понадобиться",
        "Разобраться с уже установленным диагнозом",
        "Получить объяснение дальнейших шагов",
        "Понять, нужен ли очный приём",
      ],
    },
    {
      question: "Как давно возник ваш вопрос?",
      hint: "Это поможет врачу понять контекст, но не определяет срочность.",
      multi: false,
      options: [
        "Недавно",
        "Несколько месяцев назад",
        "Более года назад",
        "Наблюдаюсь у врача регулярно",
        "Сложно ответить",
      ],
    },
    {
      question: "Что сейчас мешает записаться?",
      hint: "Выберите самый близкий вариант — это поможет показать полезную информацию.",
      multi: false,
      options: [
        "Не знаю, поможет ли онлайн-формат",
        "Не понимаю, какие документы подготовить",
        "Хочу сначала узнать стоимость",
        "Сомневаюсь, нужен ли эндокринолог",
        "Не знаю, как проходит консультация",
        "Ничего, готов записаться",
      ],
    },
    {
      question: "Как вам удобнее получить консультацию?",
      hint: "Речь о предпочтении по записи, а не о медицинской срочности.",
      multi: false,
      options: ["В ближайшие дни", "На следующей неделе", "Пока изучаю информацию"],
    },
  ];

  const TOPIC_DATA = {
    "Щитовидная железа": {
      topicLabel: "Щитовидная железа",
      title: "Вопросы по щитовидной железе и результатам обследований",
      about: "щитовидной железой и результатами обследований",
      memo: [
        "Результаты ТТГ, Т3, Т4 и УЗИ, если они есть",
        "Динамику показателей за предыдущие периоды",
        "Необходимость дополнительных исследований",
        "Когда может понадобиться очный осмотр",
      ],
    },
    "Изменение веса": {
      topicLabel: "Изменение веса и обмен веществ",
      title: "Изменения веса и обмен веществ",
      about: "изменением веса и обменом веществ",
      memo: [
        "Возможные эндокринные факторы изменения веса",
        "Метаболические показатели и их динамику",
        "Вопросы об инсулинорезистентности",
        "Какие обследования целесообразно обсудить",
      ],
    },
    "Сахар крови / диабет": {
      topicLabel: "Сахарный диабет и предиабет",
      title: "Показатели глюкозы и дальнейшее наблюдение",
      about: "показателями глюкозы и наблюдением",
      memo: [
        "Показатели глюкозы и HbA1c",
        "Динамику наблюдения и предыдущие результаты",
        "Факторы, которые влияют на показатели",
        "Дальнейшие шаги в рамках дистанционного формата",
      ],
    },
    "Гормональные анализы": {
      topicLabel: "Гормональное здоровье",
      title: "Гормональные показатели и клинический контекст",
      about: "гормональными анализами",
      memo: [
        "Гормональные анализы в контексте жалоб",
        "Эндокринные аспекты нарушений цикла",
        "Вопросы при планировании беременности",
        "Какие обследования стоит обсудить",
      ],
    },
    "Изменения самочувствия": {
      topicLabel: "Изменения самочувствия",
      title: "Самочувствие и возможные эндокринные причины",
      about: "изменениями самочувствия",
      memo: [
        "Возможные причины утомляемости и других симптомов",
        "Связь симптомов с результатами анализов",
        "Какие обследования могут быть целесообразны",
        "Когда нужен очный приём",
      ],
    },
    "У меня уже есть диагноз": {
      topicLabel: "Анализы и второе мнение",
      title: "Наблюдение при установленном диагнозе",
      about: "наблюдением при установленном диагнозе",
      memo: [
        "Текущие результаты и динамику показателей",
        "Вопросы по назначенному лечению",
        "План дальнейшего наблюдения",
        "Когда требуется очный приём",
      ],
    },
    "Другая причина обращения": {
      topicLabel: "Вопрос о записи",
      title: "Как сформулировать запрос к врачу",
      about: "формулированием запроса к врачу",
      memo: [
        "С чего начать разбор ситуации",
        "Какие специалисты могут понадобиться",
        "Какие документы подготовить",
        "Как сформулировать вопросы для консультации",
      ],
    },
  };

  const PREP_BASE = [
    "Результаты анализов и обследований, если они есть",
    "Список лекарств, витаминов и дозировок",
    "Информацию о диагнозах, операциях и аллергиях",
    "Список вопросов, которые важно задать",
  ];

  const BARRIER_NOTES = {
    "Не знаю, поможет ли онлайн-формат":
      "Онлайн-формат подходит для обсуждения жалоб и документов, но не заменяет очный осмотр. На консультации можно понять, достаточно ли дистанционного разбора в вашей ситуации.",
    "Не понимаю, какие документы подготовить":
      "Достаточно того, что уже есть: анализы, заключения, список лекарств и вопросов. Дополнительные исследования не нужно сдавать заранее без обсуждения.",
    "Хочу сначала узнать стоимость":
      "Первичная консультация — 4 500 ₽ за 60 минут. Стоимость известна до записи, а объём услуги описан в разделе «Стоимость».",
    "Сомневаюсь, нужен ли эндокринолог":
      "Опрос не определяет, нужен ли врач. Если сомневаетесь, начните с консультации: на ней можно обсудить, относится ли ваш вопрос к эндокринологии.",
    "Не знаю, как проходит консультация":
      "Консультация проходит по видеосвязи в согласованное время. Вы заранее получаете инструкцию по подключению и список того, что может пригодиться.",
    "Ничего, готов записаться":
      "Можно сразу выбрать удобное время. Форма записи — ниже; точное время согласуем после заявки.",
  };

  const quizDialog = $("#quiz-dialog");
  const quizViews = {
    start: $('[data-quiz-view="start"]', quizDialog),
    question: $('[data-quiz-view="question"]', quizDialog),
    result: $('[data-quiz-view="result"]', quizDialog),
  };
  const questionTitle = $("[data-quiz-question]", quizDialog);
  const questionHint = $("[data-quiz-hint]", quizDialog);
  const optionsHost = $("[data-quiz-options]", quizDialog);
  const stepLabel = $("[data-quiz-step]", quizDialog);
  const progress = $("[data-quiz-progress]", quizDialog);
  const progressBar = $(".quiz-progress", quizDialog);
  const quizError = $("[data-quiz-error]", quizDialog);
  const nextButton = $("[data-quiz-next]", quizDialog);
  const backButton = $("[data-quiz-back]", quizDialog);

  let quizIndex = 0;
  let quizAnswers = Array(QUESTIONS.length).fill(null);
  let quizCompleted = false;
  let lastQuizTrigger = null;

  function answerFor(index) {
    return quizAnswers[index];
  }

  function hasAnswer(index) {
    const answer = answerFor(index);
    if (Array.isArray(answer)) return answer.length > 0;
    return Boolean(answer);
  }

  function saveQuizState() {
    try {
      sessionStorage.setItem(
        "quizState",
        JSON.stringify({ answers: quizAnswers, index: quizIndex, completed: quizCompleted })
      );
    } catch (error) {
      // Session storage is optional.
    }
  }

  function loadQuizState() {
    try {
      const raw = sessionStorage.getItem("quizState");
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.answers) || parsed.answers.length !== QUESTIONS.length) return;
      quizAnswers = parsed.answers;
      quizIndex = Math.min(Math.max(Number(parsed.index) || 0, 0), QUESTIONS.length - 1);
      quizCompleted = Boolean(parsed.completed);
    } catch (error) {
      // Ignore malformed state.
    }
  }

  function showQuizView(name) {
    Object.entries(quizViews).forEach(([key, view]) => {
      if (!view) return;
      view.hidden = key !== name;
    });
    if (name === "question") {
      if (questionTitle) {
        questionTitle.tabIndex = -1;
        questionTitle.focus({ preventScroll: true });
      }
    }
    if (name === "result") {
      const resultTitle = $("[data-result-title]", quizDialog);
      if (resultTitle) {
        resultTitle.tabIndex = -1;
        resultTitle.focus({ preventScroll: true });
      }
    }
    if (name === "start") {
      const start = $("[data-quiz-start]", quizDialog);
      if (start) start.focus({ preventScroll: true });
    }
  }

  function renderQuestion() {
    const data = QUESTIONS[quizIndex];
    if (!data) return;
    quizError.hidden = true;
    questionTitle.textContent = data.question;
    questionHint.textContent = data.hint || "";
    stepLabel.textContent = String(quizIndex + 1);
    const percent = ((quizIndex + 1) / QUESTIONS.length) * 100;
    progress.style.width = `${percent}%`;
    if (progressBar) {
      progressBar.setAttribute("aria-valuenow", String(quizIndex + 1));
    }
    optionsHost.replaceChildren();

    const selected = answerFor(quizIndex);
    data.options.forEach((option, optionIndex) => {
      const label = document.createElement("label");
      label.className = "quiz-option";
      const input = document.createElement("input");
      input.type = data.multi ? "checkbox" : "radio";
      input.name = `quiz-q${quizIndex}`;
      input.value = option;
      input.id = `quiz-q${quizIndex}-${optionIndex}`;
      if (Array.isArray(selected) ? selected.includes(option) : selected === option) {
        input.checked = true;
      }
      input.addEventListener("change", () => {
        quizError.hidden = true;
        if (data.multi) {
          const current = new Set(Array.isArray(quizAnswers[quizIndex]) ? quizAnswers[quizIndex] : []);
          if (input.checked) current.add(option);
          else current.delete(option);
          quizAnswers[quizIndex] = Array.from(current);
        } else {
          quizAnswers[quizIndex] = option;
        }
        saveQuizState();
      });
      const span = document.createElement("span");
      span.textContent = option;
      label.append(input, span);
      optionsHost.appendChild(label);
    });

    showQuizView("question");
    track("quiz_step", { step: quizIndex + 1 });
  }

  function goNext() {
    if (!hasAnswer(quizIndex)) {
      quizError.hidden = false;
      const first = $("input", optionsHost);
      if (first) first.focus();
      return;
    }
    quizError.hidden = true;
    if (quizIndex < QUESTIONS.length - 1) {
      quizIndex += 1;
      saveQuizState();
      renderQuestion();
    } else {
      quizCompleted = true;
      saveQuizState();
      renderResult();
      track("quiz_complete", { steps: QUESTIONS.length });
    }
  }

  function goBack() {
    quizError.hidden = true;
    if (quizIndex > 0) {
      quizIndex -= 1;
      saveQuizState();
      renderQuestion();
    } else {
      showQuizView("start");
    }
  }

  function selectedTopics() {
    return (quizAnswers[0] || []).map((value) => TOPIC_DATA[value]).filter(Boolean);
  }

  function buildResult() {
    const topics = selectedTopics();
    const primary = topics[0] || TOPIC_DATA["Другая причина обращения"];
    const extra = topics.slice(1, 3).map((topic) => topic.about);
    const title = primary.title;
    let lead = `Судя по ответам, вас интересуют вопросы, связанные с ${primary.about}.`;
    if (extra.length) {
      lead = `Судя по ответам, вас интересуют вопросы, связанные с ${primary.about}, а также ${extra.join(" и ")}.`;
    }
    lead += " На консультации можно обсудить значение имеющихся показателей, историю жалоб и необходимость дополнительных действий.";

    const barrier = quizAnswers[5];
    if (barrier && BARRIER_NOTES[barrier]) {
      lead += ` ${BARRIER_NOTES[barrier]}`;
    }

    const memo = [];
    topics.slice(0, 2).forEach((topic) => {
      topic.memo.forEach((item) => {
        if (!memo.includes(item)) memo.push(item);
      });
    });
    if (!memo.length) memo.push(...TOPIC_DATA["Другая причина обращения"].memo);

    const prep = [...PREP_BASE];
    if (quizAnswers[2] && quizAnswers[2].includes("Пока ничего не сдавал")) {
      prep.unshift("Не сдавайте анализы заранее: врач подскажет, что действительно нужно");
    }
    if (quizAnswers[2] && quizAnswers[2].includes("Есть УЗИ или другие исследования")) {
      prep.push("Заключения УЗИ и других исследований");
    }
    if (barrier === "Не понимаю, какие документы подготовить") {
      prep.push("Не нужно собирать всё сразу: возьмите то, что уже есть");
    }
    if (quizAnswers[6] === "Пока изучаю информацию") {
      lead += " Вы можете сохранить памятку и вернуться к записи позже.";
    }

    return { primary, title, lead, memo, prep };
  }

  function renderResult() {
    const result = buildResult();
    $("[data-result-title]", quizDialog).textContent = result.title;
    $("[data-result-lead]", quizDialog).textContent = result.lead;

    const memoList = $("[data-result-list]", quizDialog);
    memoList.replaceChildren();
    result.memo.slice(0, 6).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      memoList.appendChild(li);
    });

    const prepList = $("[data-result-prep]", quizDialog);
    prepList.replaceChildren();
    result.prep.slice(0, 6).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      prepList.appendChild(li);
    });

    const book = $("[data-result-book]", quizDialog);
    if (book) {
      book.dataset.resultTopic = result.primary.topicLabel;
    }
    showQuizView("result");
  }

  function startQuiz() {
    quizIndex = 0;
    quizAnswers = Array(QUESTIONS.length).fill(null);
    quizCompleted = false;
    saveQuizState();
    renderQuestion();
    track("quiz_start");
  }

  function openQuiz(trigger) {
    if (!quizDialog) return;
    lastQuizTrigger = trigger || document.activeElement;
    if (!quizDialog.open) quizDialog.showModal();
    document.body.classList.add("dialog-open");
    if (quizCompleted) {
      renderResult();
    } else if (quizIndex > 0 && quizAnswers.some((answer) => Array.isArray(answer) ? answer.length : answer)) {
      renderQuestion();
    } else {
      showQuizView("start");
    }
    window.setTimeout(() => {
      if (quizCompleted) {
        const resultTitle = $("[data-result-title]", quizDialog);
        if (resultTitle) {
          resultTitle.tabIndex = -1;
          resultTitle.focus({ preventScroll: true });
        }
        return;
      }
      if (quizIndex > 0) {
        if (questionTitle) {
          questionTitle.tabIndex = -1;
          questionTitle.focus({ preventScroll: true });
        }
        return;
      }
      const start = $("[data-quiz-start]", quizDialog);
      if (start) start.focus({ preventScroll: true });
    }, 50);
  }

  function closeQuiz() {
    if (quizDialog && quizDialog.open) quizDialog.close();
    document.body.classList.remove("dialog-open");
    if (lastQuizTrigger && typeof lastQuizTrigger.focus === "function") {
      lastQuizTrigger.focus({ preventScroll: true });
    }
  }

  if (quizDialog) {
    loadQuizState();
    $$("[data-quiz-open]").forEach((button) => {
      button.addEventListener("click", () => openQuiz(button));
    });
    $("[data-quiz-start]", quizDialog).addEventListener("click", startQuiz);
    nextButton.addEventListener("click", goNext);
    backButton.addEventListener("click", goBack);
    $$("[data-quiz-close]", quizDialog).forEach((button) => {
      button.addEventListener("click", closeQuiz);
    });
    const closeLink = $("[data-quiz-close-link]", quizDialog);
    if (closeLink) {
      closeLink.addEventListener("click", (event) => {
        event.preventDefault();
        closeQuiz();
        scrollToElement($("#top"));
      });
    }
    quizDialog.addEventListener("click", (event) => {
      if (event.target === quizDialog) closeQuiz();
    });
    quizDialog.addEventListener("close", () => {
      document.body.classList.remove("dialog-open");
    });
    quizDialog.addEventListener("cancel", () => {
      document.body.classList.remove("dialog-open");
    });

    const restart = $("[data-quiz-restart]", quizDialog);
    if (restart) restart.addEventListener("click", startQuiz);

    const book = $("[data-result-book]", quizDialog);
    if (book) {
      book.addEventListener("click", () => {
        const topic = book.dataset.resultTopic || "Онлайн-консультация";
        setFormTopic(topic);
        track("quiz_booking_click", { topic_selected: true });
        closeQuiz();
        window.setTimeout(() => {
          scrollToElement($("#booking"));
          const name = $("#hero-name");
          if (name) name.focus({ preventScroll: true });
        }, 120);
      });
    }

    const priceLink = $("[data-result-price]", quizDialog);
    if (priceLink) {
      priceLink.addEventListener("click", (event) => {
        event.preventDefault();
        closeQuiz();
        window.setTimeout(() => scrollToElement($("#price")), 120);
      });
    }

    const save = $("[data-result-save]", quizDialog);
    if (save) {
      save.addEventListener("click", () => {
        const result = buildResult();
        const text = [
          "Памятка к консультации эндокринолога",
          `Дата: ${new Intl.DateTimeFormat("ru-RU").format(new Date())}`,
          "",
          `Ваш запрос: ${result.title}`,
          "",
          result.lead,
          "",
          "Что можно обсудить с врачом:",
          ...result.memo.map((item) => `— ${item}`),
          "",
          "Как подготовиться:",
          ...result.prep.map((item) => `— ${item}`),
          "",
          "Первичная консультация — 4 500 ₽ / 60 минут.",
          "Запись и стоимость: https://moriarty32.github.io/endocrinologist-mironova/#booking",
          "",
          "Опрос носит информационный характер, не является диагнозом и не определяет срочность помощи.",
        ].join("\n");
        const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "pamyatka-endokrinolog.txt";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        track("quiz_memo_download");
        announce("Памятка сохранена. Файл скачан на устройство.");
      });
    }
  }

  /* -------------------------------------------------------
     Generic info dialogs
     ------------------------------------------------------- */

  function openInfoDialog(dialog, trigger) {
    if (!dialog) return;
    if (!dialog.open) dialog.showModal();
    document.body.classList.add("dialog-open");
    const close = $("[data-dialog-close]", dialog);
    if (close) close.focus({ preventScroll: true });
  }

  function closeInfoDialogs() {
    $$("dialog.info-dialog[open]").forEach((dialog) => dialog.close());
    if (!document.querySelector("dialog[open]")) document.body.classList.remove("dialog-open");
  }

  const videoDialog = $("#video-dialog");
  $$("[data-video-open]").forEach((button) => {
    button.addEventListener("click", () => openInfoDialog(videoDialog, button));
  });

  const docDialog = $("#doc-dialog");
  const docTitle = $("[data-doc-title]", docDialog);
  const docPreview = $("[data-doc-preview]", docDialog);
  const docNote = $("[data-doc-note]", docDialog);

  $$("[data-doc]").forEach((card) => {
    card.addEventListener("click", () => {
      const sourceSheet = $(".doc-sheet", card);
      if (sourceSheet && docPreview) {
        docPreview.replaceChildren(sourceSheet.cloneNode(true));
      }
      if (docTitle) docTitle.textContent = card.dataset.doc || "Документ";
      if (docNote) docNote.textContent = card.dataset.docNote || "";
      openInfoDialog(docDialog, card);
      track("document_open", { document: card.dataset.doc || "unknown" });
    });
  });

  $$("[data-dialog-close]").forEach((button) => {
    button.addEventListener("click", () => {
      const dialog = button.closest("dialog");
      if (dialog) dialog.close();
      if (!document.querySelector("dialog[open]")) document.body.classList.remove("dialog-open");
    });
  });

  $$("dialog.info-dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener("close", () => {
      if (!document.querySelector("dialog[open]")) document.body.classList.remove("dialog-open");
    });
    dialog.addEventListener("cancel", () => {
      if (!document.querySelector("dialog[open]")) document.body.classList.remove("dialog-open");
    });
  });

  /* -------------------------------------------------------
     Scroll state, sticky CTA, year
     ------------------------------------------------------- */

  const mobileCta = $("[data-mobile-cta]");
  const booking = $("#booking");
  const finalSection = $("#final");
  const footer = $(".site-footer");
  let bookingVisible = false;
  let finalVisible = false;
  let footerVisible = false;
  let ticking = false;

  function updateCta() {
    if (!mobileCta) return;
    const hasDialog = document.body.classList.contains("dialog-open");
    const show = !bookingVisible && !finalVisible && !footerVisible && !hasDialog;
    mobileCta.classList.toggle("is-hidden", !show);
  }

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.target === booking) bookingVisible = entry.isIntersecting;
          if (entry.target === finalSection) finalVisible = entry.isIntersecting;
          if (entry.target === footer) footerVisible = entry.isIntersecting;
        });
        updateCta();
      },
      { rootMargin: "0px 0px -15% 0px", threshold: 0.08 }
    );
    if (booking) observer.observe(booking);
    if (finalSection) observer.observe(finalSection);
    if (footer) observer.observe(footer);
  }

  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 6);
    updateCta();
    ticking = false;
  }

  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(onScroll);
    },
    { passive: true }
  );
  window.addEventListener("resize", updateCta, { passive: true });
  onScroll();

  const year = $("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());

  /* -------------------------------------------------------
     Deep links and small conveniences
     ------------------------------------------------------- */

  const params = new URLSearchParams(window.location.search);
  if (params.get("quiz") === "1" && quizDialog) {
    window.setTimeout(() => openQuiz(null), 350);
  }

  if (params.get("topic") && params.get("topic").trim()) {
    setFormTopic(params.get("topic").trim().slice(0, 120));
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (mobileMenu && !mobileMenu.hidden) {
      setMenu(false);
      if (menuToggle) menuToggle.focus();
    }
  });
})();
