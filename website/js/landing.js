/**
 * Culture Barbershop - Standalone Luxury Website Engine (Netlify Ready)
 * Interactive Shave-the-Wordmark Canvas, 3-Tier Price Table, Cinematic Preloader, Multilingual
 */

(function () {
  // ================= WEB APP CONFIGURATION =================
  const WEBAPP_URL = "https://culture-barbershop.onrender.com";
  const TELEGRAM_BOT_URL = "https://t.me/culturebarbersbot";

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
      cat_main: "Asosiy xizmatlar",
      cat_extra: "Qo'shimcha xizmatlar",
      cat_complex: "Kompleks xizmatlar",
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
      cat_main: "Основные услуги",
      cat_extra: "Дополнительные услуги",
      cat_complex: "Комплексные услуги",
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

    // Update active tier description note
    updateTierNote();
  }

  function setLandingLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('culture_lang', lang);

    document.getElementById('landingLangUz')?.classList.toggle('active', lang === 'uz');
    document.getElementById('landingLangRu')?.classList.toggle('active', lang === 'ru');

    applyLandingTranslations();
  }

  // ================= PRICE TABLE COMPONENT =================
  const TIER_KEYS = ['PRO', 'TOP', 'VIP'];
  let currentTierIndex = 1; // Default TOP

  function updateTierNote() {
    const noteEl = document.getElementById("tierNote");
    if (!noteEl) return;
    const tier = TIER_KEYS[currentTierIndex].toLowerCase();
    noteEl.textContent = tLanding(`prices_note_${tier}`);
  }

  function setTier(i) {
    currentTierIndex = i;
    const ptable = document.getElementById("ptable");
    if (!ptable) return;

    ptable.setAttribute("data-tier", String(i));

    ptable.querySelectorAll(".phead .tier").forEach((btn, idx) => {
      btn.setAttribute("aria-pressed", idx === i ? "true" : "false");
    });

    updateTierNote();

    // Update CTA button link inside price table
    const ptableCta = ptable.querySelector(".ptable-cta");
    if (ptableCta) {
      const selectedTier = TIER_KEYS[i];
      ptableCta.href = `${WEBAPP_URL}?category=${encodeURIComponent(selectedTier)}`;
      ptableCta.setAttribute("data-tier", selectedTier);
    }
  }

  function initPriceTable() {
    const ptable = document.getElementById("ptable");
    if (!ptable) return;

    ptable.querySelectorAll(".phead .tier").forEach(btn => {
      btn.addEventListener("click", () => {
        const i = parseInt(btn.getAttribute("data-i") || "0", 10);
        setTier(i);
      });
    });

    setTier(1); // Default to TOP
  }

  // ================= SHAVE-THE-WORDMARK CANVAS =================
  const WORD = "CULTURE";
  const FONT_FAMILY = '"Cinzel", "Playfair Display", Georgia, serif';
  const ERASER_R = 46;

  let W = 0, H = 0, DPR = 1;
  let baseCanvas, baseCtx, topCanvas, topCtx;
  let isDown = false, lastPt = null, sweeping = false;
  let totalMaskPx = 0, checkTimer = null;
  let clipper = null, hintEl = null, pctEl = null;

  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function buildCanvas() {
    const stage = document.getElementById("stage");
    baseCanvas = document.getElementById("cBase");
    topCanvas = document.getElementById("cTop");
    clipper = document.getElementById("clipper");
    hintEl = document.getElementById("hint");
    pctEl = document.getElementById("pct");

    if (!stage || !baseCanvas || !topCanvas) return;

    W = stage.clientWidth;
    H = stage.clientHeight;
    DPR = Math.min(window.devicePixelRatio || 1, 2);

    [baseCanvas, topCanvas].forEach(c => {
      c.width = Math.round(W * DPR);
      c.height = Math.round(H * DPR);
      c.style.width = W + "px";
      c.style.height = H + "px";
    });

    baseCtx = baseCanvas.getContext("2d");
    topCtx = topCanvas.getContext("2d");

    baseCtx.setTransform(DPR, 0, 0, DPR, 0, 0);
    topCtx.setTransform(DPR, 0, 0, DPR, 0, 0);

    drawBase();
    drawTop();
    countMaskPixels();
  }

  function pickFontSize(ctx, text, maxW, maxH) {
    let size = Math.floor(maxH * 0.72);
    ctx.font = `700 ${size}px ${FONT_FAMILY}`;
    let m = ctx.measureText(text);
    if (m.width > maxW * 0.94) {
      size = Math.floor(size * (maxW * 0.94) / m.width);
      ctx.font = `700 ${size}px ${FONT_FAMILY}`;
    }
    return size;
  }

  function drawBase() {
    baseCtx.clearRect(0, 0, W, H);
    baseCtx.fillStyle = "#0C0C0D";
    baseCtx.fillRect(0, 0, W, H);

    const size = pickFontSize(baseCtx, WORD, W, H);
    baseCtx.font = `700 ${size}px ${FONT_FAMILY}`;
    baseCtx.textAlign = "center";
    baseCtx.textBaseline = "middle";

    const cx = W / 2, cy = H / 2;

    // Subtle warm golden shadow
    baseCtx.shadowColor = "rgba(212, 175, 55, 0.4)";
    baseCtx.shadowBlur = Math.round(size * 0.22);
    baseCtx.shadowOffsetY = 3;

    // Rich metallic golden gradient
    const grad = baseCtx.createLinearGradient(cx - size * 1.5, cy - size * 0.5, cx + size * 1.5, cy + size * 0.5);
    grad.addColorStop(0, "#FFFFFF");
    grad.addColorStop(0.2, "#F7E7A9");
    grad.addColorStop(0.5, "#D4AF37");
    grad.addColorStop(0.85, "#996515");
    grad.addColorStop(1, "#59380B");

    baseCtx.fillStyle = grad;
    baseCtx.fillText(WORD, cx, cy);

    baseCtx.shadowColor = "transparent";
    baseCtx.shadowBlur = 0;
  }

  function drawTop() {
    topCtx.clearRect(0, 0, W, H);
    topCtx.fillStyle = "#0C0C0D";
    topCtx.fillRect(0, 0, W, H);

    const size = pickFontSize(topCtx, WORD, W, H);
    topCtx.font = `700 ${size}px ${FONT_FAMILY}`;
    topCtx.textAlign = "center";
    topCtx.textBaseline = "middle";

    const cx = W / 2, cy = H / 2;

    // Charcoal outline of wordmark
    topCtx.fillStyle = "#1E1E22";
    topCtx.fillText(WORD, cx, cy);

    topCtx.lineWidth = 1.5;
    topCtx.strokeStyle = "rgba(212, 175, 55, 0.12)";
    topCtx.strokeText(WORD, cx, cy);

    // Realistic stubble/hair follicles overlay
    topCtx.save();
    topCtx.globalCompositeOperation = "source-atop";

    const count = Math.floor((W * H) / 220);
    for (let i = 0; i < count; i++) {
      const x = Math.random() * W;
      const y = Math.random() * H;
      const len = 3 + Math.random() * 6;
      const ang = Math.random() * Math.PI * 2;
      const dark = Math.random() < 0.6;

      topCtx.strokeStyle = dark ? "rgba(10, 10, 12, 0.9)" : "rgba(80, 80, 90, 0.55)";
      topCtx.lineWidth = 1 + Math.random() * 1.5;
      topCtx.beginPath();
      topCtx.moveTo(x, y);
      topCtx.lineTo(x + Math.cos(ang) * len, y + Math.sin(ang) * len);
      topCtx.stroke();
    }
    topCtx.restore();
  }

  function countMaskPixels() {
    try {
      const img = topCtx.getImageData(0, 0, Math.round(W * DPR), Math.round(H * DPR));
      const data = img.data;
      let c = 0;
      for (let i = 3; i < data.length; i += 16) {
        if (data[i] > 30) c++;
      }
      totalMaskPx = c;
    } catch (e) {
      totalMaskPx = 1;
    }
  }

  function erase(x1, y1, x2, y2) {
    topCtx.save();
    topCtx.globalCompositeOperation = "destination-out";
    topCtx.lineCap = "round";
    topCtx.lineJoin = "round";
    topCtx.lineWidth = ERASER_R * 2;

    topCtx.beginPath();
    topCtx.moveTo(x1, y1);
    topCtx.lineTo(x2, y2);
    topCtx.stroke();

    topCtx.beginPath();
    topCtx.arc(x2, y2, ERASER_R, 0, Math.PI * 2);
    topCtx.fill();
    topCtx.restore();
  }

  function placeClipper(x, y) {
    if (!clipper) return;
    clipper.style.transform = `translate(${x}px, ${y}px)`;
  }

  function scheduleCheck() {
    if (checkTimer) return;
    checkTimer = setTimeout(() => {
      checkTimer = null;
      checkCleared();
    }, 120);
  }

  function checkCleared() {
    if (!totalMaskPx) return;
    try {
      const img = topCtx.getImageData(0, 0, Math.round(W * DPR), Math.round(H * DPR));
      const data = img.data;
      let left = 0;
      for (let i = 3; i < data.length; i += 16) {
        if (data[i] > 30) left++;
      }

      const cleared = Math.max(0, Math.min(100, Math.round((1 - left / totalMaskPx) * 100)));
      if (pctEl) pctEl.textContent = tLanding("hero_pct", { n: cleared });

      if (hintEl) {
        if (cleared >= 85) {
          hintEl.textContent = tLanding("hero_hint_done");
        } else if (cleared >= 20) {
          hintEl.textContent = tLanding("hero_hint_progress");
        }
      }
    } catch (e) {}
  }

  function finishShave() {
    topCanvas.classList.add("fade");
    if (clipper) clipper.classList.remove("on");
    setTimeout(() => {
      topCtx.clearRect(0, 0, W, H);
      topCanvas.classList.remove("fade");
      if (pctEl) pctEl.textContent = tLanding("hero_pct", { n: 100 });
      if (hintEl) hintEl.textContent = tLanding("hero_hint_done");
    }, 400);
  }

  function getPos(e, el) {
    const r = el.getBoundingClientRect();
    return {
      x: e.clientX - r.left,
      y: e.clientY - r.top
    };
  }

  function initShaveEvents() {
    const stage = document.getElementById("stage");
    if (!stage) return;

    stage.addEventListener("pointerdown", e => {
      if (sweeping) return;
      isDown = true;
      stage.setPointerCapture?.(e.pointerId);
      const p = getPos(e, stage);
      lastPt = p;
      if (clipper) clipper.classList.add("on");
      erase(p.x, p.y, p.x, p.y);
      placeClipper(p.x, p.y);
      scheduleCheck();
    });

    stage.addEventListener("pointermove", e => {
      const p = getPos(e, stage);
      placeClipper(p.x, p.y);
      if (!isDown || sweeping) return;
      erase(lastPt.x, lastPt.y, p.x, p.y);
      lastPt = p;
      scheduleCheck();
    });

    const leave = () => {
      if (!isDown) return;
      isDown = false;
      lastPt = null;
      if (clipper) clipper.classList.remove("on");
    };

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
    const dur = 2000;
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

  // ================= WEB APP NAVIGATION =================
  window.openBooking = function (tier = null) {
    let url = WEBAPP_URL;
    if (tier) {
      url += "?category=" + encodeURIComponent(tier);
    }
    window.location.href = url;
  };

  function initBookingLinks() {
    // Header CTA, Hero CTA, Price Table CTA, Roadmap CTA
    document.querySelectorAll(".btn-open-booking").forEach(b => {
      b.addEventListener("click", e => {
        const tier = b.getAttribute("data-tier") || null;
        if (tier) {
          e.preventDefault();
          openBooking(tier);
        }
        // If it's a standard link without specific tier, let standard <a> href handle it or navigate
      });
    });
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
    const totalDuration = 1250;
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
    // 1. Language switcher buttons
    document.getElementById("landingLangUz")?.addEventListener("click", () => setLandingLanguage("uz"));
    document.getElementById("landingLangRu")?.addEventListener("click", () => setLandingLanguage("ru"));

    // Apply translations immediately
    applyLandingTranslations();

    // 2. Initialize Price table
    initPriceTable();

    // 3. Initialize Booking Links
    initBookingLinks();

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
