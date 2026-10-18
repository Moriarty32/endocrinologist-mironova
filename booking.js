/* Booking page: week strip, available slots and selected-time summary. */
(function () {
  "use strict";

  const page = document.querySelector(".booking-page");
  if (!page) return;

  const $ = (selector, context = document) => context.querySelector(selector);
  const daysHost = $("[data-booking-days]");
  const slotsHost = $("[data-booking-slots]");
  const timesTitle = $("[data-booking-times-title]");
  const availableLabel = $("[data-booking-available]");
  const emptyBox = $("[data-booking-empty]");
  const summaryDate = $("[data-booking-summary-date]");
  const summaryTime = $("[data-booking-summary-time]");
  const proceed = $("[data-booking-proceed]");
  const form = $('[data-form="booking-page"]');
  const submit = $("[data-booking-submit]");
  const dateInput = form ? $('input[name="date"]', form) : null;
  const timeInput = form ? $('input[name="time"]', form) : null;
  const weekdayInput = form ? $('input[name="weekday"]', form) : null;
  const successSlot = $("[data-booking-success-slot]");
  const errors = document.querySelectorAll("[data-slot-error], [data-slot-error-form]");

  if (!daysHost || !slotsHost || !form) return;

  const TZ = "Europe/Moscow";
  const WEEKDAY = ["09:30", "11:00", "12:30", "14:00", "15:30", "17:00", "18:30"];
  const SATURDAY = ["10:00", "11:30", "13:00"];
  const weekdayShort = new Intl.DateTimeFormat("ru-RU", { weekday: "short", timeZone: "UTC" });
  const weekdayLong = new Intl.DateTimeFormat("ru-RU", { weekday: "long", timeZone: "UTC" });
  const monthShort = new Intl.DateTimeFormat("ru-RU", { month: "short", timeZone: "UTC" });
  const dayMonthLong = new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "long", timeZone: "UTC" });
  const moscowDate = new Intl.DateTimeFormat("en-CA", {
    timeZone: TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const moscowTime = new Intl.DateTimeFormat("en-GB", {
    timeZone: TZ,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const capitalize = (value) => value.charAt(0).toUpperCase() + value.slice(1);
  const clean = (value) => value.replace(/\.$/, "");
  const pad = (value) => String(value).padStart(2, "0");
  const keyOf = (date) =>
    `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`;

  function moscowParts() {
    const parts = moscowDate.formatToParts(new Date());
    const get = (type) => parts.find((part) => part.type === type)?.value;
    return { year: Number(get("year")), month: Number(get("month")), day: Number(get("day")) };
  }

  function moscowNowMinutes() {
    const [hour, minute] = moscowTime.format(new Date()).split(":").map(Number);
    return hour * 60 + minute;
  }

  function slotsFor(weekday, isToday, nowMinutes) {
    if (weekday === 0) return [];
    const base = weekday === 6 ? SATURDAY : WEEKDAY;
    return base.filter((value) => {
      if (!isToday) return true;
      const [hour, minute] = value.split(":").map(Number);
      return hour * 60 + minute >= nowMinutes + 120;
    });
  }

  function buildDays() {
    const { year, month, day } = moscowParts();
    const todayKey = `${year}-${pad(month)}-${pad(day)}`;
    const base = Date.UTC(year, month - 1, day);
    const nowMinutes = moscowNowMinutes();
    return Array.from({ length: 7 }, (_, index) => {
      const date = new Date(base + index * 86400000);
      const weekday = date.getUTCDay();
      const key = keyOf(date);
      const isToday = key === todayKey;
      const slots = slotsFor(weekday, isToday, nowMinutes);
      return {
        date,
        key,
        weekday,
        dayNumber: date.getUTCDate(),
        weekdayShort: capitalize(clean(weekdayShort.format(date))),
        weekdayLong: capitalize(weekdayLong.format(date)),
        monthShort: clean(monthShort.format(date)),
        dateLong: clean(dayMonthLong.format(date)),
        isToday,
        isTomorrow: key === keyOf(new Date(base + 86400000)),
        closed: weekday === 0,
        slots,
      };
    });
  }

  const days = buildDays();
  let selectedDay = null;
  let selectedTime = null;

  function findDay(key) {
    return days.findIndex((day) => day.key === key);
  }

  function firstAvailableDay() {
    const index = days.findIndex((day) => day.slots.length);
    return index === -1 ? null : index;
  }

  function setSelectedDay(index) {
    if (index === null || index < 0 || !days[index] || !days[index].slots.length) return;
    const restoreFocus = daysHost.contains(document.activeElement);
    selectedDay = index;
    selectedTime = null;
    hideErrors();
    renderDays();
    renderSlots();
    sync();
    if (restoreFocus) {
      daysHost.querySelector(`[data-booking-day="${index}"]`)?.focus({ preventScroll: true });
    }
  }

  function setSelectedTime(time) {
    if (selectedDay === null) return;
    if (!days[selectedDay].slots.includes(time)) return;
    const restoreFocus = slotsHost.contains(document.activeElement);
    selectedTime = time;
    hideErrors();
    renderSlots();
    sync();
    if (restoreFocus) {
      slotsHost.querySelector(`[data-booking-time="${time}"]`)?.focus({ preventScroll: true });
    }
  }

  function hideErrors() {
    errors.forEach((error) => {
      error.hidden = true;
    });
  }

  function dayTag(day) {
    if (day.closed) return "выходной";
    if (!day.slots.length) return "нет слотов";
    if (day.isToday) return "сегодня";
    if (day.isTomorrow) return "завтра";
    return "";
  }

  function renderDays() {
    daysHost.innerHTML = days
      .map((day, index) => {
        const selected = index === selectedDay;
        const disabled = !day.slots.length;
        const tag = dayTag(day);
        const label = `${day.weekdayLong}, ${day.dateLong}${disabled ? ", запись недоступна" : ", есть свободное время"}`;
        return `
          <button class="booking-day${selected ? " is-selected" : ""}" type="button" data-booking-day="${index}" aria-pressed="${selected}" aria-label="${label}"${disabled ? " disabled" : ""}>
            <span class="booking-day-name">${day.weekdayShort}</span>
            <strong>${day.dayNumber}</strong>
            <span class="booking-day-month">${day.monthShort}</span>
            <span class="booking-day-tag">${tag || "&nbsp;"}</span>
          </button>`;
      })
      .join("");
  }

  function renderSlots() {
    const day = selectedDay === null ? null : days[selectedDay];
    if (!day) {
      timesTitle.textContent = "Свободное время";
      availableLabel.textContent = "";
      slotsHost.innerHTML = "";
      emptyBox.hidden = true;
      return;
    }

    timesTitle.textContent = `${day.weekdayLong}, ${day.dateLong}`;
    availableLabel.textContent = day.slots.length ? `Свободно: ${day.slots.length}` : "нет свободного времени";
    emptyBox.hidden = day.slots.length > 0;
    emptyBox.textContent = day.slots.length
      ? ""
      : "На этот день свободных слотов нет. Выберите другой день или напишите мне — постараюсь подобрать время.";

    if (!day.slots.length) {
      slotsHost.innerHTML = "";
      return;
    }

    const groups = [
      { label: "Утро", test: (time) => Number(time.slice(0, 2)) < 12 },
      { label: "День", test: (time) => Number(time.slice(0, 2)) >= 12 && Number(time.slice(0, 2)) < 17 },
      { label: "Вечер", test: (time) => Number(time.slice(0, 2)) >= 17 },
    ];

    slotsHost.innerHTML = groups
      .map((group) => {
        const times = day.slots.filter(group.test);
        if (!times.length) return "";
        return `
          <div class="booking-slot-group">
            <h4>${group.label}</h4>
            <div class="booking-slots">
              ${times
                .map((time) => {
                  const selected = time === selectedTime;
                  return `<button class="booking-slot${selected ? " is-selected" : ""}" type="button" data-booking-time="${time}" aria-pressed="${selected}" aria-label="${time}, ${day.weekdayLong}, ${day.dateLong}">
                    <span>${time}</span><small>60 мин</small>
                  </button>`;
                })
                .join("")}
            </div>
          </div>`;
      })
      .join("");
  }

  function endTime(start) {
    const [hour, minute] = start.split(":").map(Number);
    const total = hour * 60 + minute + 60;
    return `${pad(Math.floor(total / 60))}:${pad(total % 60)}`;
  }

  function sync() {
    const day = selectedDay === null ? null : days[selectedDay];
    const time = day && selectedTime ? selectedTime : null;
    const hasSlot = Boolean(day && time);

    if (!day) {
      summaryDate.textContent = "Сначала выберите день";
      summaryTime.textContent = "Затем — удобное время";
    } else if (!time) {
      summaryDate.textContent = `${day.weekdayLong}, ${day.dateLong}`;
      summaryTime.textContent = "Выберите время";
    } else {
      summaryDate.textContent = `${day.weekdayShort}, ${day.dateLong}`;
      summaryTime.textContent = `${time}–${endTime(time)}`;
    }

    if (proceed) proceed.hidden = !hasSlot;
    if (dateInput) dateInput.value = hasSlot ? day.key : "";
    if (timeInput) timeInput.value = hasSlot ? time : "";
    if (weekdayInput) weekdayInput.value = hasSlot ? day.weekdayLong : "";
    if (successSlot) {
      successSlot.textContent = hasSlot
        ? `${day.weekdayLong}, ${day.dateLong}, ${time}–${endTime(time)}`
        : "время не выбрано";
    }
    if (submit) {
      submit.disabled = !hasSlot;
      submit.textContent = hasSlot ? `Записаться на ${time}` : "Сначала выберите время";
    }
  }

  daysHost.addEventListener("click", (event) => {
    const button = event.target.closest("[data-booking-day]");
    if (!button || button.disabled) return;
    setSelectedDay(Number(button.dataset.bookingDay));
  });

  slotsHost.addEventListener("click", (event) => {
    const button = event.target.closest("[data-booking-time]");
    if (!button || button.disabled) return;
    setSelectedTime(button.dataset.bookingTime);
  });

  form.addEventListener("reset", () => {
    window.setTimeout(sync, 0);
  });

  if (proceed) {
    proceed.addEventListener("click", (event) => {
      event.preventDefault();
      const name = $("#booking-name");
      $("#booking-form-title")?.scrollIntoView({ behavior: "smooth", block: "center" });
      window.setTimeout(() => name?.focus({ preventScroll: true }), 350);
    });
  }

  const params = new URLSearchParams(window.location.search);
  const requestedDate = params.get("date");
  const requestedTime = params.get("time");
  const requestedIndex = requestedDate ? findDay(requestedDate) : -1;

  if (requestedIndex >= 0 && days[requestedIndex].slots.length) {
    selectedDay = requestedIndex;
    if (requestedTime && days[requestedIndex].slots.includes(requestedTime)) {
      selectedTime = requestedTime;
    }
  } else {
    selectedDay = firstAvailableDay();
  }

  renderDays();
  renderSlots();
  sync();
})();
