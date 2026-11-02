/**
 * Culture Barbershop - Landing Page Interactive Animations & Booking Modal Integration
 * Shave-the-Wordmark Canvas, Interactive 3-Tier Price Table, Bilingual Support
 */

(function () {
  // ================= BILINGUAL DICTIONARY FOR LANDING PAGE =================
  const LANDING_I18N = {
    uz: {
      nav_prices: "Narxlar",
      nav_booking: "Yozilish",
      nav_location: "Manzil",
      nav_book_btn: "Onlayn yozilish",
      hero_line: "Professional parvarish. Sizning uslubingiz.",
      hero_book_btn: "Onlayn yozilish",
      hero_clear_btn: "Hammasini tozalash",
      hero_hint: "Yozuv soqol bilan qoplangan. Chapga va o‘ngga suring.",
      hero_hint_progress: "Davom eting, qolganini o‘zingiz tozalang.",
      hero_hint_done: "Tayyor. Endi stulga o‘ting.",
      hero_pct: "Tozalandi: {n}%",
      about_title: "More than a haircut",
      about_desc: "Culture Olmaliqdagi zamonaviy va hashamatli barbershop. Barber darajasini o‘zingiz tanlaysiz: PRO, TOP yoki VIP. Xizmatlarni belgilab, qulay vaqtga yoziling va navbatda turmang.",
      prices_title: "Narxlar",
      prices_note_pro: "PRO: kundalik uslublar va klassik soch turmaklari. Boshlang'ich narx 75 000 so'm.",
      prices_note_top: "TOP: tajribali barber, yuqori aniqlik va shaxsiy uslub. Eng ko‘p tanlanadigan toifa.",
      prices_note_vip: "VIP: eksklyuziv parvarish. Mualliflik soch kesimi, soqol parvarishi va spa.",
      prices_table_service: "Xizmat",
      prices_footnote: "Narxlar so‘mda ko‘rsatilgan. Daraja nomini bossangiz, ustun ajralib turadi.",
      booking_title: "Onlayn yozilish",
      booking_desc: "Yozilish qulay interaktiv ilovada ochiladi. Barbershopning bron tizimi barcha bo‘sh vaqtlarni real vaqt rejimida ko‘rsatadi.",
      booking_act_btn: "Yozilish",
      booking_bot_btn: "Telegram bot",
      step_1: "Barber darajasini tanlang: PRO, TOP yoki VIP.",
      step_2: "Shu darajadagi professional ustalardan birini tanlang.",
      step_3: "Kerakli xizmatlarni belgilang, jami narx avtomatik hisoblanadi.",
      step_4: "Sana va qulay vaqtni tanlab, ismingiz va raqamingizni yozing. Usta tasdiqlashi bilan botdan xabar olasiz.",
      location_title: "Qayerda va qachon",
      loc_city_title: "Shahar",
      loc_city_desc: "Olmaliq shahri. Aniq manzil va yo'nalish Instagram sahifamizda.",
      loc_hours_title: "Ish vaqti",
      loc_hours_desc: "Har kuni 10:00 dan 22:00 gacha dam olish kunlarisiz.",
      loc_contact_title: "Bog‘lanish",
      footer_text: "Culture barbershop, Olmaliq",
      preloader_tagline: "PREMIAL BARBERSHOP • OLMALIQ",
      preloader_loading: "Tayyorlanmoqda...",
      preloader_ready: "Xush kelibsiz",
      preloader_skip: "O‘tkazib yuborish ›"
    },
    ru: {
      nav_prices: "Цены",
      nav_booking: "Запись",
      nav_location: "Адрес",
      nav_book_btn: "Онлайн запись",
      hero_line: "Профессиональный уход. Ваш безупречный стиль.",
      hero_book_btn: "Онлайн запись",
      hero_clear_btn: "Очистить всё",
      hero_hint: "Логотип покрыт щетиной. Проведите пальцем или курсором.",
      hero_hint_progress: "Отлично, продолжайте сбривать щетину.",
      hero_hint_done: "Готово! Теперь добро пожаловать в кресло мастера.",
      hero_pct: "Сбрито: {n}%",
      about_title: "More than a haircut",
      about_desc: "Culture — премиальный барбершоп в Алмалыке. Вы сами выбираете категорию барбера: PRO, TOP или VIP. Бронируйте удобное время онлайн без ожидания в очереди.",
      prices_title: "Прайс-лист",
      prices_note_pro: "PRO: повседневный стиль и классические стрижки. Цены от 75 000 сум.",
      prices_note_top: "TOP: опытный мастер, высокая точность и индивидуальный стиль. Самый популярный выбор.",
      prices_note_vip: "VIP: премиальный уход. Авторская стрижка, моделирование бороды и спа.",
      prices_table_service: "Услуга",
      prices_footnote: "Цены указаны в сумах. Нажмите на категорию, чтобы выделить колонку.",
      booking_title: "Онлайн запись",
      booking_desc: "Запись открывается в интерактивном модуле. Доступны все свободные слоты времени в реальном времени.",
      booking_act_btn: "Записаться",
      booking_bot_btn: "Telegram бот",
      step_1: "Выберите категорию мастера: PRO, TOP или VIP.",
      step_2: "Выберите одного из наших профессиональных барберов.",
      step_3: "Отметьте нужные услуги — сумма рассчитается автоматически.",
      step_4: "Выберите дату и удобное время, укажите имя и телефон. После подтверждения мастером вам придёт уведомление.",
      location_title: "Где и когда",
      loc_city_title: "Город",
      loc_city_desc: "г. Алмалык. Точный адрес и геолокация в нашем Instagram.",
      loc_hours_title: "Время работы",
      loc_hours_desc: "Ежедневно с 10:00 до 22:00 без выходных.",
      loc_contact_title: "Контакты",
      footer_text: "Culture barbershop, Алмалык",
      preloader_tagline: "ПРЕМИАЛЬНЫЙ БАРБЕРШОП • АЛМАЛЫК",
      preloader_loading: "Подготовка...",
      preloader_ready: "Добро пожаловать",
      preloader_skip: "Пропустить ›"
    }
  };

  let currentLang = localStorage.getItem('culture_lang') || 'uz';

  function tLanding(key, params = {}) {
    const dict = LANDING_I18N[currentLang] || LANDING_I18N.uz;
    let val = dict[key] || LANDING_I18N.uz[key] || key;
    for (const [k, v] of Object.entries(params)) {
      val = val.replace(`{${k}}`, v);
    }
    return val;
  }

  function applyLandingTranslations() {
    document.querySelectorAll('[data-landing-i18n]').forEach(el => {
      const key = el.getAttribute('data-landing-i18n');
      if (key) {
        el.textContent = tLanding(key);
      }
    });

    // Update active lang buttons on landing page
    const uzBtn = document.getElementById('landingLangUz');
    const ruBtn = document.getElementById('landingLangRu');
    if (uzBtn && ruBtn) {
      uzBtn.classList.toggle('active', currentLang === 'uz');
      ruBtn.classList.toggle('active', currentLang === 'ru');
    }

    // Refresh tier note in price table
    updateTierNote(currentTierIndex);
  }

  window.setLandingLanguage = function (lang) {
    currentLang = lang;
    localStorage.setItem('culture_lang', lang);
    applyLandingTranslations();
    if (window.app && typeof window.app.setLanguage === 'function') {
      window.app.setLanguage(lang);
    }
  };

  // ================= 18 SERVICES & PRICE TABLE =================
  const GROUPS = [
    {
      t_uz: "Asosiy xizmatlar",
      t_ru: "Основные услуги",
      items: [
        { uz: "Erkaklar soch olishi", ru: "Мужская стрижка", p: [75, 95, 125] },
        { uz: "Bolalar soch olishi", ru: "Детская стрижка", p: [45, 60, 75] },
        { uz: "Soqol va britva modellash", ru: "Моделирование бороды", p: [55, 75, 105] },
        { uz: "Okantovka", ru: "Окантовка", p: [30, 50, 70] },
        { uz: "Mashinkada soch olish", ru: "Стрижка машинкой", p: [40, 60, 90] },
        { uz: "Ukladka", ru: "Укладка волос", p: [30, 40, 50] }
      ]
    },
    {
      t_uz: "Qo‘shimcha xizmatlar",
      t_ru: "Дополнительные услуги",
      items: [
        { uz: "Oq sochni kamuflyaj qilish", ru: "Камуфляж седины", p: [40, 60, 80] },
        { uz: "Mum bilan korreksiya (Vosk)", ru: "Удаление волос воском", p: [20, 30, 40] },
        { uz: "Premium soqol modellash", ru: "Премиум борода", p: [85, 105, 135] },
        { uz: "Premium soch olish", ru: "Премиум стрижка", p: [95, 125, 155] },
        { uz: "Premium bosh terisi parvarishi", ru: "Премиум уход за кожей головы", p: [35, 45, 55] },
        { uz: "Premium yuz parvarishi", ru: "Премиум уход за лицом", p: [40, 50, 60] },
        { uz: "SPA bosh terisi parvarishi", ru: "SPA уход за кожей головы", p: [25, 35, 45] },
        { uz: "Qora niqob (Black Mask)", ru: "Черная маска", p: [30, 40, 50] }
      ]
    },
    {
      t_uz: "Kompleks xizmatlar",
      t_ru: "Комплексные услуги",
      items: [
        { uz: "Soch olish + soqol modellash", ru: "Стрижка + моделирование бороды", p: [110, 140, 190] },
        { uz: "Soch olish + SPA bosh terisi", ru: "Стрижка + SPA уход", p: [85, 115, 145] },
        { uz: "Soch olish + qora niqob", ru: "Стрижка + черная маска", p: [90, 120, 150] },
        { uz: "Ota + o‘g‘il (10 yoshgacha)", ru: "Папа + сын (до 10 лет)", p: [115, 145, 185] }
      ]
    }
  ];

  function fmt(n) {
    return (n * 1000).toLocaleString('ru-RU');
  }

  let currentTierIndex = 1; // 0: PRO, 1: TOP, 2: VIP

  function renderPriceTable() {
    const pbody = document.getElementById("pbody");
    if (!pbody) return;
    pbody.innerHTML = '';

    GROUPS.forEach(g => {
      const h = document.createElement("h3");
      h.className = "pgroup";
      h.textContent = currentLang === 'ru' ? g.t_ru : g.t_uz;
      pbody.appendChild(h);

      g.items.forEach(it => {
        const r = document.createElement("div");
        r.className = "prow";
        const name = currentLang === 'ru' ? it.ru : it.uz;
        r.innerHTML = `
          <span class="pn">${name}</span>
          <span class="pv c0">${fmt(it.p[0])}</span>
          <span class="pv c1">${fmt(it.p[1])}</span>
          <span class="pv c2">${fmt(it.p[2])}</span>
        `;
        r.addEventListener("click", () => {
          const tiers = ['PRO', 'TOP', 'VIP'];
          openBooking(tiers[currentTierIndex]);
        });
        pbody.appendChild(r);
      });
    });
  }

  function updateTierNote(i) {
    const noteEl = document.getElementById("tierNote");
    if (!noteEl) return;
    const keys = ['prices_note_pro', 'prices_note_top', 'prices_note_vip'];
    noteEl.textContent = tLanding(keys[i]);
  }

  function setTier(i) {
    currentTierIndex = i;
    const ptable = document.getElementById("ptable");
    if (ptable) ptable.setAttribute("data-tier", String(i));

    const tierBtns = document.querySelectorAll(".tier");
    tierBtns.forEach((b, k) => {
      b.setAttribute("aria-pressed", String(k === i));
    });

    updateTierNote(i);
  }

  function initPriceTable() {
    renderPriceTable();
    const tierBtns = document.querySelectorAll(".tier");
    tierBtns.forEach(b => {
      b.addEventListener("click", () => {
        setTier(Number(b.getAttribute("data-i")));
      });
    });
    setTier(1);
  }

  // ================= SHAVE-THE-WORDMARK CANVAS HERO =================
  let stage, cBase, cTop, clipper, hint, pctEl;
  const WORD = "CULTURE";
  const FONT_FAMILY = '"Cinzel", "Playfair Display", "Times New Roman", serif';
  let W = 0, H = 0, dpr = 1, fs = 0, brush = 40, baseCount = 1, done = false, sweeping = false, timer = null;
  const probe = document.createElement("canvas");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function tok(n) {
    return getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  }

  function buildCanvas() {
    stage = document.getElementById("stage");
    cBase = document.getElementById("cBase");
    cTop = document.getElementById("cTop");
    clipper = document.getElementById("clipper");
    hint = document.getElementById("hint");
    pctEl = document.getElementById("pct");

    if (!stage || !cBase || !cTop || !clipper) return;

    done = false;
    stage.classList.remove("is-done");
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = stage.clientWidth;

    const bctx = cBase.getContext("2d");
    bctx.font = "700 200px " + FONT_FAMILY;
    const m = bctx.measureText(WORD);
    const k0 = (W * 0.96) / m.width;
    fs = Math.min(200 * k0, 420);
    const k = fs / 200;
    const textW = m.width * k;
    const asc = (m.actualBoundingBoxAscent || 140) * k;
    const pad = fs * 0.08;
    H = Math.ceil(asc + pad * 2);
    const x = (W - textW) / 2;
    const y = pad + asc;

    stage.style.height = H + "px";
    brush = Math.max(32, H * 0.32);
    clipper.style.height = brush + "px";

    [cBase, cTop].forEach(c => {
      c.width = Math.round(W * dpr);
      c.height = Math.round(H * dpr);
    });

    const b = cBase.getContext("2d");
    b.setTransform(dpr, 0, 0, dpr, 0, 0);
    b.clearRect(0, 0, W, H);
    b.font = "700 " + fs + "px " + FONT_FAMILY;
    b.fillStyle = tok("--letter") || "#ECECEE";
    b.fillText(WORD, x, y);

    const t = cTop.getContext("2d");
    t.setTransform(dpr, 0, 0, dpr, 0, 0);
    t.clearRect(0, 0, W, H);
    t.font = "700 " + fs + "px " + FONT_FAMILY;
    t.fillStyle = tok("--stub-base") || "#2B2B2F";
    t.fillText(WORD, x, y);
    t.globalCompositeOperation = "source-atop";

    const n = Math.floor((W * H) / 7);
    const stubColors = [tok("--stub-a") || "#5C5C63", tok("--stub-b") || "#19191B"];

    stubColors.forEach(col => {
      t.strokeStyle = col;
      t.lineWidth = 1.1;
      t.beginPath();
      for (let i = 0; i < n; i++) {
        const px = Math.random() * W;
        const py = Math.random() * H;
        const a = -Math.PI / 2 + (Math.random() - 0.5) * 1.3;
        const len = 3 + Math.random() * 6;
        t.moveTo(px, py);
        t.lineTo(px + Math.cos(a) * len, py + Math.sin(a) * len);
      }
      t.stroke();
    });

    t.globalCompositeOperation = "source-over";
    baseCount = Math.max(1, sampleCanvas());
    if (pctEl) pctEl.textContent = tLanding('hero_pct', { n: 0 });
  }

  function sampleCanvas() {
    if (!cTop || !W || !H) return 1;
    const w = 220;
    const h = Math.max(1, Math.round((w * H) / W));
    probe.width = w;
    probe.height = h;
    const p = probe.getContext("2d", { willReadFrequently: true });
    p.clearRect(0, 0, w, h);
    p.drawImage(cTop, 0, 0, w, h);
    const data = p.getImageData(0, 0, w, h).data;
    let c = 0;
    for (let i = 3; i < data.length; i += 4) {
      if (data[i] > 60) c++;
    }
    return c;
  }

  function checkProgress() {
    timer = null;
    const v = Math.min(1, Math.max(0, 1 - sampleCanvas() / baseCount));
    const pct = Math.round(v * 100);
    if (pctEl) pctEl.textContent = tLanding('hero_pct', { n: pct });
    if (v >= 0.86) finishShave();
  }

  function scheduleCheck() {
    if (!timer && !done) timer = setTimeout(checkProgress, 220);
  }

  function finishShave() {
    if (done) return;
    done = true;
    if (stage) stage.classList.add("is-done");
    if (pctEl) pctEl.textContent = tLanding('hero_pct', { n: 100 });
    if (hint) hint.textContent = tLanding('hero_hint_done');
    if (clipper) clipper.classList.remove("on");
  }

  function erase(x0, y0, x1, y1) {
    if (!cTop) return;
    const t = cTop.getContext("2d");
    t.save();
    t.globalCompositeOperation = "destination-out";
    t.lineWidth = brush;
    t.lineCap = "round";
    t.lineJoin = "round";
    t.beginPath();
    t.moveTo(x0, y0);
    t.lineTo(x1, y1);
    t.stroke();
    t.restore();
  }

  function placeClipper(x, y) {
    if (!clipper) return;
    clipper.style.transform = `translate3d(${x - 14}px, ${y - brush / 2}px, 0)`;
  }

  function initShaveEvents() {
    let last = null;
    if (!stage) return;

    stage.addEventListener("pointermove", e => {
      if (done || sweeping) return;
      const r = cTop.getBoundingClientRect();
      const x = e.clientX - r.left;
      const y = e.clientY - r.top;
      clipper.classList.add("on");
      placeClipper(x, y);

      if (last) erase(last.x, last.y, x, y);
      else erase(x, y, x, y);

      last = { x, y };
      if (hint && hint.dataset.t !== "1") {
        hint.dataset.t = "1";
        hint.textContent = tLanding('hero_hint_progress');
      }
      scheduleCheck();
    });

    const leave = () => {
      last = null;
      if (clipper) clipper.classList.remove("on");
      scheduleCheck();
    };

    stage.addEventListener("pointerleave", leave);
    stage.addEventListener("pointerup", leave);
    stage.addEventListener("pointercancel", leave);

    document.getElementById("clearAll")?.addEventListener("click", finishShave);
  }

  function sweepIntro() {
    if (reduce) {
      erase(-10, H / 2, W + 10, H / 2);
      scheduleCheck();
      return;
    }
    sweeping = true;
    const dur = 2200;
    let t0 = null;
    let px = -20;
    if (clipper) clipper.classList.add("on");

    function ease(t) {
      return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }

    function step(ts) {
      if (t0 === null) t0 = ts;
      const p = Math.min(1, (ts - t0) / dur);
      const x = -20 + (W + 40) * ease(p);
      erase(px, H / 2, x, H / 2);
      placeClipper(x, H / 2);
      px = x;

      if (p < 1) {
        requestAnimationFrame(step);
      } else {
        sweeping = false;
        if (clipper) clipper.classList.remove("on");
        scheduleCheck();
      }
    }
    requestAnimationFrame(step);
  }

  // ================= MODAL BOOKING ENGINE =================
  window.openBooking = function (preselectedTier = null) {
    const modal = document.getElementById("bookingModal");
    if (!modal) return;

    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    if (window.app) {
      // If a category was clicked in price table or hero
      if (preselectedTier) {
        window.app.selectCategory(preselectedTier);
      } else {
        window.app.goToStep("stepCategories");
      }
    }
  };

  window.closeBooking = function () {
    const modal = document.getElementById("bookingModal");
    if (!modal) return;

    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  };

  function initBookingModal() {
    // Open buttons
    document.querySelectorAll(".btn-open-booking").forEach(b => {
      b.addEventListener("click", e => {
        e.preventDefault();
        const tier = b.getAttribute("data-tier") || null;
        openBooking(tier);
      });
    });

    // Close button & backdrop click
    document.getElementById("closeBookingModalBtn")?.addEventListener("click", closeBooking);

    const modal = document.getElementById("bookingModal");
    modal?.addEventListener("click", e => {
      if (e.target === modal) {
        closeBooking();
      }
    });

    // Escape key
    window.addEventListener("keydown", e => {
      if (e.key === "Escape" && modal?.classList.contains("active")) {
        closeBooking();
      }
    });

    // Auto-open if Telegram Web App or ?book=1 URL param
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("book") === "1" || window.Telegram?.WebApp?.initData) {
      openBooking();
    }
  }

  // ================= CINEMATIC ENTRANCE PRELOADER =================
  let preloaderDismissed = false;
  let preloaderOnComplete = null;

  function initPreloader(onComplete) {
    preloaderOnComplete = onComplete;
    const preloader = document.getElementById("preloader");
    if (!preloader) {
      document.body.classList.add("entrance-ready");
      if (onComplete) onComplete();
      return;
    }

    const bar = document.getElementById("preloaderBar");
    const pct = document.getElementById("preloaderPct");
    const status = document.getElementById("preloaderStatus");
    const skipBtn = document.getElementById("preloaderSkip");

    let animFrame = null;

    // Check if directly opening booking (?book=1 or Telegram Mini App)
    const urlParams = new URLSearchParams(window.location.search);
    const isDirectBooking = urlParams.get("book") === "1" || !!window.Telegram?.WebApp?.initData;
    const totalDuration = isDirectBooking ? 350 : 1250; // swift for booking, cinematic for regular visit

    const startTime = performance.now();

    function dismissPreloader() {
      if (preloaderDismissed) return;
      preloaderDismissed = true;
      if (animFrame) cancelAnimationFrame(animFrame);

      if (bar) bar.style.width = "100%";
      if (pct) pct.textContent = "100%";
      if (status) status.textContent = tLanding("preloader_ready");

      preloader.classList.add("preloader-dismiss");
      document.body.classList.add("entrance-ready");

      // Trigger callback (sweep intro on canvas) shortly after curtains part
      setTimeout(() => {
        if (preloaderOnComplete) preloaderOnComplete();
      }, 350);

      // Clean up preloader from DOM after transition finishes
      setTimeout(() => {
        preloader.classList.add("preloader-finished");
        preloader.setAttribute("aria-hidden", "true");
      }, 900);
    }

    function updateProgress(now) {
      if (preloaderDismissed) return;
      const elapsed = now - startTime;
      const t = Math.min(1, elapsed / totalDuration);

      // Smooth cubic ease out
      const eased = 1 - Math.pow(1 - t, 3);
      const progress = Math.min(100, Math.round(eased * 100));

      if (bar) bar.style.width = progress + "%";
      if (pct) pct.textContent = progress + "%";

      if (t < 1) {
        animFrame = requestAnimationFrame(updateProgress);
      } else {
        dismissPreloader();
      }
    }

    animFrame = requestAnimationFrame(updateProgress);

    // Skip on button click
    skipBtn?.addEventListener("click", (e) => {
      e.stopPropagation();
      dismissPreloader();
    });

    // Skip on tapping preloader backdrop
    preloader.addEventListener("click", (e) => {
      if (e.target && e.target.id === "preloaderSkip") return;
      dismissPreloader();
    });
  }

  // ================= DOM READY INIT =================
  document.addEventListener("DOMContentLoaded", () => {
    // 1. Language switcher buttons on landing page
    document.getElementById("landingLangUz")?.addEventListener("click", () => setLandingLanguage("uz"));
    document.getElementById("landingLangRu")?.addEventListener("click", () => setLandingLanguage("ru"));

    // Apply translations immediately so preloader displays user language
    applyLandingTranslations();

    // 2. Initialize Price table
    initPriceTable();

    // 3. Initialize Booking Modal
    initBookingModal();

    // 4. Initialize Shave-the-Wordmark Canvas
    let canvasReady = false;
    const fontsReady = (document.fonts && document.fonts.load)
      ? document.fonts.load("700 200px " + FONT_FAMILY, WORD).catch(() => {})
      : Promise.resolve();

    fontsReady.then(() => {
      buildCanvas();
      initShaveEvents();
      canvasReady = true;
    });

    // 5. Initialize Entrance Preloader
    initPreloader(() => {
      if (canvasReady) {
        sweepIntro();
      } else {
        fontsReady.then(() => setTimeout(sweepIntro, 100));
      }
    });

    let lastW = 0, rt = null;
    window.addEventListener("resize", () => {
      clearTimeout(rt);
      rt = setTimeout(() => {
        const s = document.getElementById("stage");
        if (s && s.clientWidth !== lastW) {
          lastW = s.clientWidth;
          buildCanvas();
        }
      }, 200);
    });
  });
})();
