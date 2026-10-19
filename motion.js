/* ==========================================================================
   Motion layer — hero intro, scroll reveal, accordion, gentle parallax.
   No dependencies, no build step. Everything here is progressive enhancement:
   without this file the site stays static and fully readable.
   ========================================================================== */

(function () {
  "use strict";

  // The inline head script hides reveal targets before first paint. If we got
  // this far the script loaded, so the failsafe timer in the head can stand down.
  window.__dshMotion = true;

  const root = document.documentElement;
  const reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const hoverQuery = window.matchMedia("(hover: hover)");
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

  if (reduceQuery.matches) {
    root.classList.remove("has-motion");
    return;
  }

  /* -------------------------------------------------------
     Hero intro
     ------------------------------------------------------- */

  const HERO_COPY = ".ref-hero-copy, .page-hero, .booking-hero-copy, .online-hero-copy, .profile-hero-copy";
  const HERO_EXTRAS = [
    [".ref-hero-doctor", "m-hero-photo", 260],
    [".ref-form-card", "m-hero-item", 300],
    [".ref-quiz", "m-hero-item", 440],
    [".booking-hero-card", "m-hero-item", 260],
    [".page-hero-actions", "m-hero-item", 320],
  ];

  function initHero() {
    let items = 0;

    $$(HERO_COPY).forEach((copy) => {
      Array.from(copy.children).forEach((child, index) => {
        // The landing badges animate as a group of their own.
        if (child.classList.contains("ref-facts")) {
          child.classList.add("m-hero-cascade");
          child.style.setProperty("--m-hero-delay", "380ms");
          items += 1;
          return;
        }
        child.classList.add("m-hero-item");
        child.style.setProperty("--m-hero-delay", `${60 + index * 70}ms`);
        items += 1;
      });
    });

    HERO_EXTRAS.forEach(([selector, className, delay]) => {
      $$(selector).forEach((element) => {
        element.classList.add(className);
        element.style.setProperty("--m-hero-delay", `${delay}ms`);
        items += 1;
      });
    });

    if (!items) return;
    // Two frames: let the browser apply the hidden state before animating.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => root.classList.add("m-hero-in"));
    });
  }

  /* -------------------------------------------------------
     Scroll reveal
     ------------------------------------------------------- */

  // Containers whose direct children are revealed one after another.
  const REVEAL_GROUPS = [
    ".ref-problems-grid",
    ".ref-value-grid",
    ".ref-docs-grid",
    ".ref-steps-grid",
    ".ref-principles-grid",
    ".ref-articles-grid",
    ".ref-faq-list",
    ".ref-price-grid",
    ".ref-final",
    ".cards-grid",
    ".cards-grid-3",
    ".disease-grid",
    ".article-list",
    ".doc-grid",
    ".contact-grid",
    ".price-cards",
    ".faq-accordion",
    ".online-concerns-grid",
    ".online-process-grid",
    ".online-details",
    ".profile-content",
    ".online-content",
    ".booking-content",
    ".footer-top",
  ];

  // Single blocks revealed on their own.
  const REVEAL_LONE = [".ref-head", ".ref-about", ".ref-video", ".section-head"];

  // Photographs get a soft focus pull in addition to the fade.
  const REVEAL_PHOTO = [".ref-article-img", ".profile-video img", ".about-photo img"];

  const targets = [];
  const seen = new WeakSet();

  function mark(element, index, extraClass) {
    if (!element || seen.has(element)) return;
    seen.add(element);
    element.classList.add("m-reveal");
    if (extraClass) element.classList.add(extraClass);
    element.style.setProperty("--m-delay", `${Math.min(index, 6) * 70}ms`);
    targets.push(element);
  }

  function initReveal() {
    REVEAL_GROUPS.forEach((selector) => {
      $$(selector).forEach((group) => {
        Array.from(group.children).forEach((child, index) => {
          if (child.tagName === "SCRIPT" || child.tagName === "STYLE") return;
          mark(child, index);
        });
      });
    });

    REVEAL_LONE.forEach((selector) => {
      $$(selector).forEach((element) => mark(element, 0));
    });

    REVEAL_PHOTO.forEach((selector) => {
      $$(selector).forEach((element) => {
        if (!element.classList.contains("m-reveal")) mark(element, 0);
        element.classList.add("m-reveal--photo");
      });
    });

    if (!targets.length) return;

    const reveal = (element) => element.classList.add("is-in");

    if (!("IntersectionObserver" in window)) {
      targets.forEach(reveal);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          reveal(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.001 }
    );

    targets.forEach((element) => observer.observe(element));
  }

  /* -------------------------------------------------------
     FAQ accordion
     <details> hides its content when closed, so the height is animated by
     hand and `open` is only cleared once the collapse has finished.
     ------------------------------------------------------- */

  function initAccordions() {
    const DURATION = 360;

    $$(".faq-accordion, .ref-faq-list").forEach((list) => {
      $$("details", list).forEach((details) => {
        const summary = $("summary", details);
        const body = details.querySelector(":scope > div");
        if (!summary || !body) return;

        let busy = false;

        // Closed <details> keeps a layout box in current Chrome (content-visibility),
        // so the collapsing height has to be pinned here or the first open snaps.
        body.style.height = details.open ? "auto" : "0px";

        const settle = (callback) => {
          let done = false;
          const finish = () => {
            if (done) return;
            done = true;
            busy = false;
            body.removeEventListener("transitionend", onEnd);
            callback();
          };
          const onEnd = (event) => {
            if (event.target === body && event.propertyName === "height") finish();
          };
          body.addEventListener("transitionend", onEnd);
          window.setTimeout(finish, DURATION + 80);
        };

        const open = () => {
          busy = true;
          details.open = true;
          body.style.height = "0px";
          const target = body.scrollHeight;
          body.style.height = `${target}px`;
          settle(() => {
            body.style.height = "auto";
          });
        };

        const close = () => {
          busy = true;
          body.style.height = `${body.getBoundingClientRect().height}px`;
          void body.offsetHeight;
          body.style.height = "0px";
          settle(() => {
            details.open = false;
          });
        };

        summary.addEventListener("click", (event) => {
          event.preventDefault();
          if (busy) return;
          if (details.open) close();
          else open();
        });
      });
    });
  }

  /* -------------------------------------------------------
     Gentle parallax for the landing portrait
     Uses the individual `translate` property so it composes with the
     transform-based intro animation instead of fighting it.
     ------------------------------------------------------- */

  function initParallax() {
    const photos = $$(".ref-hero-doctor img");
    if (!photos.length || !hoverQuery.matches) return;

    let ticking = false;
    const update = () => {
      ticking = false;
      const viewport = window.innerHeight || 800;
      photos.forEach((photo) => {
        const rect = photo.getBoundingClientRect();
        if (rect.bottom < -200 || rect.top > viewport + 200) return;
        const progress = (rect.top + rect.height / 2 - viewport / 2) / viewport;
        const shift = Math.max(-10, Math.min(10, -progress * 14));
        photo.style.translate = `0 ${shift.toFixed(2)}px`;
      });
    };

    const request = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    };

    if (window.innerWidth < 900) return;
    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request, { passive: true });
    update();
  }

  /* -------------------------------------------------------
     Boot
     ------------------------------------------------------- */

  initHero();
  initReveal();
  initAccordions();
  initParallax();

  // If the visitor flips the system preference mid-session, stop hiding things.
  const onReduceChange = () => {
    if (!reduceQuery.matches) return;
    root.classList.remove("has-motion");
    root.classList.add("m-hero-in");
    $$(".m-reveal").forEach((element) => element.classList.add("is-in"));
  };
  if (typeof reduceQuery.addEventListener === "function") {
    reduceQuery.addEventListener("change", onReduceChange);
  }
})();
