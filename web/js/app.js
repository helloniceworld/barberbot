/**
 * Culture Barbershop - Telegram Web App Interactive Booking Logic
 * Multilingual (UZ / RU), Dynamic 18 Services, 3 Tiers (PRO, TOP, VIP)
 * Obsidian & Gold Luxury Aesthetic
 */

const tg = window.Telegram?.WebApp;

const I18N = {
  uz: {
    // Header & Meta
    app_title: "Culture Barbershop",
    profile_title: "Mening bronlarim",
    currency: "UZS",
    
    // Step 1: Craft category selection
    step1_eyebrow: "1-BOSQICH (4 TADAN)",
    step1_title: "Sartarosh toifasini tanlang",
    step1_desc: "O'zingizga mos bo'lgan mahorat darajasini tanlang",
    tier_pro_name: "PRO Barber",
    tier_pro_sub: "Standart sifat",
    tier_pro_desc: "Kundalik uslub va klassik soch turmaklari",
    tier_pro_price: "75 000 UZS dan",
    badge_popular: "OMMABOP",
    tier_top_name: "TOP Barber",
    tier_top_sub: "Tajribali usta",
    tier_top_desc: "Yuqori aniqlik va individual uslub",
    tier_top_price: "95 000 UZS dan",
    badge_signature: "PREMIUM",
    tier_vip_name: "VIP Barber",
    tier_vip_sub: "Eksklyuziv parvarish",
    tier_vip_desc: "Mualliflik soch kesimi, soqol parvarishi va spa",
    tier_vip_price: "125 000 UZS dan",

    // Step 2: Barbers
    step2_eyebrow: "2-BOSQICH (4 TADAN)",
    step2_title: "Sartaroshni tanlang",
    step2_desc: "O'z mahoratiga ega ustalardan birini tanlang",
    btn_back: "Orqaga",
    years_exp: "yil tajriba",
    select_btn: "Tanlash",
    selected_btn: "Tanlandi",
    no_barbers: "Ushbu toifada hozircha ustalar mavjud emas.",

    // Step 3: Services
    step3_eyebrow: "3-BOSQICH (4 TADAN)",
    step3_title: "Xizmatlarni tanlang",
    step3_desc: "Bir yoki bir nechta xizmat turini tanlang",
    filter_all: "Barchasi",
    filter_main: "Asosiy",
    filter_extra: "Qo'shimcha",
    filter_complex: "Kompleks",
    group_main: "Asosiy xizmatlar",
    group_extra: "Qo'shimcha xizmatlar",
    group_complex: "Kompleks xizmatlar",
    no_services: "Xizmatlar topilmadi",
    mins: "daqiqa",
    services_selected: "{n} ta xizmat tanlandi",
    btn_continue: "Davom etish",

    // Step 4: Date & Time
    step4_eyebrow: "4-BOSQICH (4 TADAN)",
    step4_title: "Sana va Vaqtni tanlang",
    step4_desc: "O'zingizga qulay bo'sh vaqt oralig'ini tanlang",
    pill_datetime: "Sana va Vaqt",
    available_slots: "Mavjud vaqtlar",
    time_not_selected: "Vaqt tanlanmagan",
    btn_to_confirm: "Tasdiqlashga o'tish",
    today: "Bugun",
    tomorrow: "Erta",
    days_short: ['Yak', 'Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan'],
    months_short: ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyun', 'Iyul', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'],

    // Step 5: Confirmation
    pill_review: "Ko'rib chiqish",
    step5_title: "Buyurtma ma'lumotlari",
    step5_desc: "Buyurtma ma'lumotlarini tekshiring va tasdiqlang",
    label_barber: "Sartarosh:",
    label_category: "Toifasi:",
    label_datetime: "Sana va Vaqt:",
    label_services: "Tanlangan xizmatlar:",
    label_total: "Jami to'lov:",
    contact_info_title: "Bog'lanish ma'lumotlari",
    input_name_label: "Ism va Familiya",
    input_name_placeholder: "Masalan: Alisher Karimov",
    input_phone_label: "Telefon raqam",
    input_phone_placeholder: "+998 90 123 45 67",
    btn_submit_booking: "TASDIQLASH VA BRON QILISH",
    submitting: "Saqlanmoqda...",

    // Step 6: Success
    success_title: "Muvaffaqiyatli bron qilindi!",
    success_desc: "Sizning buyurtmangiz qabul qilindi. Sartarosh so'rovni qabul qilishi bilanoq <b>@culturebarbersbot</b> orqali xabarnoma olasiz.",
    receipt_id: "Buyurtma ID:",
    receipt_barber: "Sartarosh:",
    receipt_datetime: "Sana va Vaqt:",
    receipt_total: "Jami to'lov:",
    btn_my_bookings: "Mening bronlarim",
    btn_close: "Yopish",

    // Drawer: Bookings
    my_bookings_title: "Mening bronlarim",
    no_bookings: "Sizda hali hech qanday bron mavjud emas.",
    status_pending: "Kutilmoqda ⏳",
    status_confirmed: "Tasdiqlangan ✅",
    status_completed: "Bajarilgan 💈",
    status_cancelled: "Bekor qilingan ❌",
    cancel_btn: "Bekor qilish",
    cancel_confirm: "#{id} raqamli buyurtmani bekor qilishni tasdiqlaysizmi?",
    booking_cancelled: "Bron muvaffaqiyatli bekor qilindi",

    // Errors & Loading
    err_select_service: "Kamida bitta xizmatni tanlang",
    err_name_req: "Iltimos, ismingizni kiriting",
    err_phone_req: "Iltimos, to'g'ri telefon raqam kiriting",
    loading: "Yuklanmoqda...",
    slots_loading: "Bo'sh vaqtlar tekshirilmoqda..."
  },
  ru: {
    // Header & Meta
    app_title: "Culture Barbershop",
    profile_title: "Мои записи",
    currency: "сум",

    // Step 1: Craft category selection
    step1_eyebrow: "ШАГ 1 ИЗ 4",
    step1_title: "Выберите категорию мастера",
    step1_desc: "Выберите подходящий для вас уровень мастерства",
    tier_pro_name: "PRO Barber",
    tier_pro_sub: "Стандартное качество",
    tier_pro_desc: "Повседневный стиль и классические стрижки",
    tier_pro_price: "от 75 000 сум",
    badge_popular: "ХИТ",
    tier_top_name: "TOP Barber",
    tier_top_sub: "Опытный мастер",
    tier_top_desc: "Высокая точность и индивидуальный стиль",
    tier_top_price: "от 95 000 сум",
    badge_signature: "ПРЕМИУМ",
    tier_vip_name: "VIP Barber",
    tier_vip_sub: "Премиум уход",
    tier_vip_desc: "Авторская стрижка, моделирование бороды и спа",
    tier_vip_price: "от 125 000 сум",

    // Step 2: Barbers
    step2_eyebrow: "ШАГ 2 ИЗ 4",
    step2_title: "Выберите мастера",
    step2_desc: "Выберите одного из наших профессиональных барберов",
    btn_back: "Назад",
    years_exp: "г. опыта",
    select_btn: "Выбрать",
    selected_btn: "Выбрано",
    no_barbers: "В данной категории мастеров пока нет.",

    // Step 3: Services
    step3_eyebrow: "ШАГ 3 ИЗ 4",
    step3_title: "Выберите услуги",
    step3_desc: "Выберите одну или несколько необходимых услуг",
    filter_all: "Все услуги",
    filter_main: "Основные",
    filter_extra: "Дополнительные",
    filter_complex: "Комплексы",
    group_main: "Основные услуги",
    group_extra: "Дополнительные услуги",
    group_complex: "Комплексные услуги",
    no_services: "Услуги не найдены",
    mins: "мин",
    services_selected: "Выбрано услуг: {n}",
    btn_continue: "Продолжить",

    // Step 4: Date & Time
    step4_eyebrow: "ШАГ 4 ИЗ 4",
    step4_title: "Выберите дату и время",
    step4_desc: "Выберите удобный свободный интервал времени",
    pill_datetime: "Дата и время",
    available_slots: "Доступное время",
    time_not_selected: "Время не выбрано",
    btn_to_confirm: "Перейти к подтверждению",
    today: "Сегодня",
    tomorrow: "Завтра",
    days_short: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    months_short: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],

    // Step 5: Confirmation
    pill_review: "Проверка",
    step5_title: "Детали записи",
    step5_desc: "Проверьте данные бронирования и подтвердите запись",
    label_barber: "Барбер:",
    label_category: "Категория:",
    label_datetime: "Дата и время:",
    label_services: "Выбранные услуги:",
    label_total: "Итого к оплате:",
    contact_info_title: "Контактная информация",
    input_name_label: "Имя и Фамилия",
    input_name_placeholder: "Например: Алишер Каримов",
    input_phone_label: "Номер телефона",
    input_phone_placeholder: "+998 90 123 45 67",
    btn_submit_booking: "ПОДТВЕРДИТЬ И ЗАБРОНИРОВАТЬ",
    submitting: "Бронирование...",

    // Step 6: Success
    success_title: "Запись успешно оформлена!",
    success_desc: "Ваша заявка принята. Как только мастер подтвердит запись, вы получите уведомление в боте <b>@culturebarbersbot</b>.",
    receipt_id: "ID брони:",
    receipt_barber: "Барбер:",
    receipt_datetime: "Дата и время:",
    receipt_total: "Итого к оплате:",
    btn_my_bookings: "Мои записи",
    btn_close: "Закрыть",

    // Drawer: Bookings
    my_bookings_title: "Мои записи",
    no_bookings: "У вас пока нет активных записей.",
    status_pending: "В ожидании ⏳",
    status_confirmed: "Подтверждено ✅",
    status_completed: "Выполнено 💈",
    status_cancelled: "Отменено ❌",
    cancel_btn: "Отменить",
    cancel_confirm: "Вы действительно хотите отменить бронь #{id}?",
    booking_cancelled: "Запись успешно отменена",

    // Errors & Loading
    err_select_service: "Выберите хотя бы одну услугу",
    err_name_req: "Пожалуйста, введите ваше имя",
    err_phone_req: "Пожалуйста, введите корректный номер телефона",
    loading: "Загрузка...",
    slots_loading: "Загрузка доступного времени..."
  }
};

const app = {
  // State
  state: {
    lang: localStorage.getItem('culture_lang') || 'uz',
    selectedCategory: 'TOP',
    selectedBarber: null,
    selectedServices: [],
    selectedDate: null,
    selectedTime: null,
    selectedServiceFilter: 'all',
    allBarbers: [],
    allServices: [],
    myBookings: []
  },

  // Telegram User Data
  user: {
    id: null,
    name: '',
    username: ''
  },

  t(key, params = {}) {
    const dict = I18N[this.state.lang] || I18N.uz;
    let val = dict[key] ?? I18N.uz[key] ?? key;
    if (typeof val === 'string') {
      for (const [k, v] of Object.entries(params)) {
        val = val.replace(`{${k}}`, v);
      }
    }
    return val;
  },

  init() {
    // 1. Initialize Telegram WebApp SDK
    if (tg) {
      try {
        tg.ready();
        tg.expand();
        if (tg.enableClosingConfirmation) {
          tg.enableClosingConfirmation();
        }

        const tgUser = tg.initDataUnsafe?.user;
        if (tgUser) {
          this.user.id = tgUser.id;
          this.user.name = [tgUser.first_name, tgUser.last_name].filter(Boolean).join(' ');
          this.user.username = tgUser.username || '';

          // If user's Telegram language code is Russian and no saved preference, default to RU
          if (!localStorage.getItem('culture_lang') && tgUser.language_code?.startsWith('ru')) {
            this.state.lang = 'ru';
          }
        }
      } catch (e) {
        console.warn('Telegram WebApp SDK init warning:', e);
      }
    }

    // Prefill name if available
    const nameInput = document.getElementById('clientNameInput');
    if (nameInput && this.user.name) {
      nameInput.value = this.user.name;
    }

    // 2. Setup language buttons
    this.setupLanguageSwitcher();

    // 3. Setup event listeners
    this.setupEventListeners();

    // 4. Setup dates in carousel
    this.initDateCarousel();

    // 5. Apply translations to current DOM
    this.applyTranslations();

    // 6. Fetch initial data from server
    this.fetchData();

    // 7. Check user bookings
    if (this.user.id) {
      this.fetchMyBookings();
    }
  },

  // Haptic Feedback Helper
  haptic(type = 'light') {
    if (tg?.HapticFeedback) {
      try {
        if (type === 'light') tg.HapticFeedback.impactOccurred('light');
        else if (type === 'medium') tg.HapticFeedback.impactOccurred('medium');
        else if (type === 'success') tg.HapticFeedback.notificationOccurred('success');
        else if (type === 'error') tg.HapticFeedback.notificationOccurred('error');
      } catch (e) {}
    }
  },

  setupLanguageSwitcher() {
    const uzBtn = document.getElementById('langBtnUz');
    const ruBtn = document.getElementById('langBtnRu');

    uzBtn?.addEventListener('click', (e) => {
      e.preventDefault();
      this.setLanguage('uz');
    });

    ruBtn?.addEventListener('click', (e) => {
      e.preventDefault();
      this.setLanguage('ru');
    });

    this.updateLanguageButtons();
  },

  setLanguage(lang) {
    this.haptic('light');
    this.state.lang = lang;
    localStorage.setItem('culture_lang', lang);

    // Update active button state
    this.updateLanguageButtons();

    // Apply translations to all static elements
    this.applyTranslations();

    // Re-render date carousel with localized day and month names
    this.initDateCarousel();

    // Re-render currently active views
    if (this.state.selectedCategory) {
      const pill = document.getElementById('selectedTierPill');
      if (pill) {
        pill.textContent = `${this.state.selectedCategory} BARBER`;
      }
      this.renderBarbers(this.state.selectedCategory);
    }

    if (this.state.selectedBarber) {
      this.renderServices(this.state.selectedBarber.category);
    }

    this.renderSummary();
    this.updateServicesSummary();
    this.updateDateTimeSummary();

    if (document.getElementById('bookingsDrawer')?.classList.contains('active')) {
      this.renderMyBookingsList();
    }
  },

  updateLanguageButtons() {
    const uzBtn = document.getElementById('langBtnUz');
    const ruBtn = document.getElementById('langBtnRu');
    if (uzBtn && ruBtn) {
      if (this.state.lang === 'uz') {
        uzBtn.classList.add('active');
        ruBtn.classList.remove('active');
      } else {
        ruBtn.classList.add('active');
        uzBtn.classList.remove('active');
      }
    }
  },

  applyTranslations() {
    // 1. Text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key) {
        el.innerHTML = this.t(key);
      }
    });

    // 2. Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key) {
        el.placeholder = this.t(key);
      }
    });

    // 3. Titles / tooltips
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (key) {
        el.title = this.t(key);
      }
    });

    this.updateServicesSummary();
    this.updateDateTimeSummary();
  },

  setupEventListeners() {
    // Tier Card clicks
    const tierCards = document.querySelectorAll('.tier-card');
    tierCards.forEach(card => {
      card.addEventListener('click', () => {
        const cat = card.getAttribute('data-category');
        this.selectCategory(cat);
      });
    });

    // Step 3 button -> Step 4
    document.getElementById('toDateTimeBtn')?.addEventListener('click', () => {
      this.haptic('medium');
      this.goToStep('stepDateTime');
      this.loadSlots();
    });

    // Step 4 button -> Step 5
    document.getElementById('toConfirmBtn')?.addEventListener('click', () => {
      this.haptic('medium');
      this.renderSummary();
      this.goToStep('stepConfirm');
    });

    // Step 5 button -> Confirm Booking
    document.getElementById('confirmBookingBtn')?.addEventListener('click', () => {
      this.submitBooking();
    });

    // Service category filter tabs
    document.querySelectorAll('.filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        this.haptic('light');
        document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.state.selectedServiceFilter = btn.getAttribute('data-filter') || 'all';
        if (this.state.selectedBarber) {
          this.renderServices(this.state.selectedBarber.category);
        }
      });
    });

    // Header Profile button -> Bookings Drawer
    document.getElementById('openBookingsBtn')?.addEventListener('click', () => {
      this.haptic('light');
      this.openBookingsDrawer();
    });

    document.getElementById('closeBookingsBtn')?.addEventListener('click', () => {
      this.closeBookingsDrawer();
    });

    document.getElementById('bookingsDrawer')?.addEventListener('click', (e) => {
      if (e.target.id === 'bookingsDrawer') {
        this.closeBookingsDrawer();
      }
    });

    // Success Screen buttons
    document.getElementById('successMyBookingsBtn')?.addEventListener('click', () => {
      this.openBookingsDrawer();
    });

    document.getElementById('successCloseBtn')?.addEventListener('click', () => {
      if (tg) {
        tg.close();
      } else {
        this.goToStep('stepCategories');
      }
    });

    // Brand logo home link
    document.getElementById('brandHomeBtn')?.addEventListener('click', () => {
      this.goToStep('stepCategories');
    });

    // Telegram BackButton handler
    if (tg?.BackButton) {
      tg.BackButton.onClick(() => {
        this.handleTelegramBack();
      });
    }
  },

  handleTelegramBack() {
    const activeStep = document.querySelector('.view-step.active')?.id;
    if (activeStep === 'stepBarbers') {
      this.goToStep('stepCategories');
    } else if (activeStep === 'stepServices') {
      this.goToStep('stepBarbers');
    } else if (activeStep === 'stepDateTime') {
      this.goToStep('stepServices');
    } else if (activeStep === 'stepConfirm') {
      this.goToStep('stepDateTime');
    } else if (activeStep === 'stepSuccess') {
      this.goToStep('stepCategories');
    }
  },

  goToStep(stepId) {
    document.querySelectorAll('.view-step').forEach(el => el.classList.remove('active'));
    const target = document.getElementById(stepId);
    if (target) {
      target.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if (tg?.BackButton) {
      if (stepId === 'stepCategories') {
        tg.BackButton.hide();
      } else {
        tg.BackButton.show();
      }
    }
  },

  // ================= DATA FETCHING =================
  async fetchData() {
    try {
      const [barbersRes, servicesRes] = await Promise.all([
        fetch('/api/barbers'),
        fetch('/api/services')
      ]);

      if (barbersRes.ok) {
        this.state.allBarbers = await barbersRes.json();
      }

      if (servicesRes.ok) {
        this.state.allServices = await servicesRes.json();
      }

      // Pre-select category if specified in URL query params
      const urlParams = new URLSearchParams(window.location.search);
      const catParam = (urlParams.get('category') || urlParams.get('tier') || urlParams.get('cat') || '').toUpperCase();
      if (['PRO', 'TOP', 'VIP'].includes(catParam)) {
        this.selectCategory(catParam);
      }
    } catch (e) {
      console.error('Data fetch error:', e);
      this.showToast(this.t('loading'));
    }
  },

  // ================= STEP 1: CATEGORY SELECTION =================
  selectCategory(category) {
    this.haptic('medium');
    this.state.selectedCategory = category;

    const pill = document.getElementById('selectedTierPill');
    if (pill) {
      pill.textContent = `${category} BARBER`;
    }

    this.renderBarbers(category);
    this.goToStep('stepBarbers');
  },

  // ================= STEP 2: BARBERS LIST =================
  renderBarbers(category) {
    const container = document.getElementById('barbersListContainer');
    if (!container) return;

    container.innerHTML = '';
    const filtered = this.state.allBarbers.filter(b => b.category === category);

    if (filtered.length === 0) {
      container.innerHTML = `
        <div style="grid-column: span 2; text-align: center; color: var(--text-muted); padding: 40px 10px;">
          ${this.t('no_barbers')}
        </div>
      `;
      return;
    }

    filtered.forEach(barber => {
      const isSelected = this.state.selectedBarber?.id === barber.id;
      const card = document.createElement('div');
      card.className = `barber-card ${isSelected ? 'selected' : ''}`;
      card.innerHTML = `
        <div class="barber-avatar-wrap">
          <div class="barber-avatar-placeholder">
            <span>${barber.name.charAt(0)}</span>
          </div>
        </div>
        <div class="barber-details">
          <div class="barber-name-row">
            <span class="barber-name">${barber.name}</span>
            <span class="barber-cat-badge">${barber.category}</span>
          </div>
          <div class="barber-meta">
            <span class="barber-rating">⭐ ${barber.rating || '5.0'}</span>
            <span>•</span>
            <span>${barber.experience_years || 3} ${this.t('years_exp')}</span>
          </div>
        </div>
        <button class="barber-select-btn" type="button">${isSelected ? this.t('selected_btn') : this.t('select_btn')}</button>
      `;

      card.addEventListener('click', () => {
        this.selectBarber(barber);
      });

      container.appendChild(card);
    });
  },

  selectBarber(barber) {
    this.haptic('medium');
    this.state.selectedBarber = barber;

    const pill = document.getElementById('selectedBarberPill');
    if (pill) {
      pill.textContent = barber.name;
    }

    this.renderServices(barber.category);
    this.goToStep('stepServices');
  },

  // ================= STEP 3: SERVICES =================
  renderServices(category) {
    const container = document.getElementById('servicesListContainer');
    if (!container) return;

    container.innerHTML = '';
    const catCol = `price_${category.toLowerCase()}`;
    const filter = this.state.selectedServiceFilter;

    // Filter services
    let services = this.state.allServices;
    if (filter !== 'all') {
      services = services.filter(s => s.type === filter);
    }

    if (services.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; color: var(--text-muted); padding: 40px 10px;">
          ${this.t('no_services')}
        </div>
      `;
      return;
    }

    // Grouping headers if 'all' filter is active
    let currentGroup = null;

    services.forEach(srv => {
      if (filter === 'all' && srv.type !== currentGroup) {
        currentGroup = srv.type;
        const groupTitle = document.createElement('div');
        groupTitle.className = 'services-group-title';
        const groupKey = `group_${currentGroup}`;
        groupTitle.textContent = this.t(groupKey);
        container.appendChild(groupTitle);
      }

      const price = srv[catCol] || srv.price_pro || 75000;
      const isChecked = this.state.selectedServices.some(s => s.id === srv.id);
      const priceFormatted = `${price.toLocaleString('ru-RU')} ${this.t('currency')}`;

      // Localized service name
      const serviceName = (this.state.lang === 'ru' ? (srv.name_ru || srv.name) : (srv.name_uz || srv.name)) || srv.name;

      const card = document.createElement('div');
      card.className = `service-card ${isChecked ? 'selected' : ''}`;
      card.innerHTML = `
        <div class="service-left">
          <div class="service-checkbox">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <div class="service-info">
            <span class="service-name">${serviceName}</span>
            <span class="service-duration">⏱ ${srv.duration_min || 45} ${this.t('mins')}</span>
          </div>
        </div>
        <div class="service-price">${priceFormatted}</div>
      `;

      card.addEventListener('click', () => {
        this.toggleService(srv, price);
        card.classList.toggle('selected');
      });

      container.appendChild(card);
    });

    this.updateServicesSummary();
  },

  toggleService(service, price) {
    this.haptic('light');
    const idx = this.state.selectedServices.findIndex(s => s.id === service.id);
    if (idx > -1) {
      this.state.selectedServices.splice(idx, 1);
    } else {
      this.state.selectedServices.push({
        ...service,
        currentPrice: price
      });
    }
    this.updateServicesSummary();
  },

  updateServicesSummary() {
    const count = this.state.selectedServices.length;
    const total = this.state.selectedServices.reduce((sum, s) => sum + s.currentPrice, 0);

    const countEl = document.getElementById('servicesSelectedCount');
    const totalEl = document.getElementById('servicesSelectedTotal');
    const btn = document.getElementById('toDateTimeBtn');

    if (countEl) countEl.textContent = this.t('services_selected', { n: count });
    if (totalEl) totalEl.textContent = `${total.toLocaleString('ru-RU')} ${this.t('currency')}`;

    if (btn) {
      btn.disabled = (count === 0);
    }
  },

  // ================= STEP 4: DATE & TIME =================
  initDateCarousel() {
    const carousel = document.getElementById('dateCarousel');
    if (!carousel) return;

    carousel.innerHTML = '';
    const dict = I18N[this.state.lang] || I18N.uz;
    const daysArr = dict.days_short;
    const monthsArr = dict.months_short;

    const today = new Date();

    for (let i = 0; i < 10; i++) {
      const d = new Date();
      d.setDate(today.getDate() + i);

      const yyyy = d.getFullYear();
      const mm = String(d.getMonth() + 1).padStart(2, '0');
      const dd = String(d.getDate()).padStart(2, '0');
      const dateString = `${yyyy}-${mm}-${dd}`;

      let dayLabel = daysArr[d.getDay()];
      if (i === 0) dayLabel = dict.today;
      else if (i === 1) dayLabel = dict.tomorrow;

      const isCurrentActive = this.state.selectedDate === dateString || (!this.state.selectedDate && i === 0);

      const pill = document.createElement('div');
      pill.className = `date-pill ${isCurrentActive ? 'active' : ''}`;
      pill.setAttribute('data-date', dateString);
      pill.innerHTML = `
        <span class="date-day-name">${dayLabel}</span>
        <span class="date-number">${d.getDate()}</span>
        <span class="date-month-name">${monthsArr[d.getMonth()]}</span>
      `;

      pill.addEventListener('click', () => {
        this.haptic('light');
        document.querySelectorAll('.date-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.state.selectedDate = dateString;
        this.state.selectedTime = null;
        this.loadSlots();
      });

      carousel.appendChild(pill);
      if (i === 0 && !this.state.selectedDate) {
        this.state.selectedDate = dateString;
      }
    }
  },

  async loadSlots() {
    const grid = document.getElementById('slotsGrid');
    if (!grid || !this.state.selectedBarber || !this.state.selectedDate) return;

    grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 24px 10px;">${this.t('slots_loading')}</div>`;

    try {
      const res = await fetch(`/api/slots?barber_id=${this.state.selectedBarber.id}&date=${this.state.selectedDate}`);
      if (!res.ok) throw new Error('Slot error');
      const data = await res.json();

      grid.innerHTML = '';
      const availableSet = new Set(data.available_slots || []);

      data.all_work_hours.forEach(hour => {
        const isAvail = availableSet.has(hour);
        const isSelected = this.state.selectedTime === hour;

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `slot-btn ${isSelected ? 'selected' : ''}`;
        btn.textContent = hour;
        btn.disabled = !isAvail;

        if (isAvail) {
          btn.addEventListener('click', () => {
            this.haptic('medium');
            document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            this.state.selectedTime = hour;
            this.updateDateTimeSummary();
          });
        }

        grid.appendChild(btn);
      });

      this.updateDateTimeSummary();
    } catch (e) {
      console.error(e);
      grid.innerHTML = `<div style="grid-column: 1 / -1; color: red; padding: 20px 10px; text-align: center;">${this.t('loading')}</div>`;
    }
  },

  updateDateTimeSummary() {
    const infoEl = document.getElementById('dateTimeSelectedInfo');
    const totalEl = document.getElementById('dateTimeTotal');
    const btn = document.getElementById('toConfirmBtn');

    const total = this.state.selectedServices.reduce((sum, s) => sum + s.currentPrice, 0);
    if (totalEl) totalEl.textContent = `${total.toLocaleString('ru-RU')} ${this.t('currency')}`;

    if (this.state.selectedDate && this.state.selectedTime) {
      if (infoEl) infoEl.textContent = `${this.state.selectedDate} • ${this.state.selectedTime}`;
      if (btn) btn.disabled = false;
    } else {
      if (infoEl) infoEl.textContent = this.t('time_not_selected');
      if (btn) btn.disabled = true;
    }
  },

  // ================= STEP 5: SUMMARY & SUBMISSION =================
  renderSummary() {
    const barber = this.state.selectedBarber;
    const total = this.state.selectedServices.reduce((sum, s) => sum + s.currentPrice, 0);

    const nameEl = document.getElementById('sumBarberName');
    const catEl = document.getElementById('sumBarberCategory');
    const dtEl = document.getElementById('sumDateTime');
    const priceEl = document.getElementById('sumTotalPrice');

    if (nameEl) nameEl.textContent = barber?.name || '—';
    if (catEl) catEl.textContent = barber ? `${barber.category} Barber` : '—';
    if (dtEl) dtEl.textContent = `${this.state.selectedDate || '—'} | ${this.state.selectedTime || '—'}`;
    if (priceEl) priceEl.textContent = `${total.toLocaleString('ru-RU')} ${this.t('currency')}`;

    const servicesContainer = document.getElementById('sumServicesList');
    if (servicesContainer) {
      servicesContainer.innerHTML = '';
      this.state.selectedServices.forEach(s => {
        const serviceName = (this.state.lang === 'ru' ? (s.name_ru || s.name) : (s.name_uz || s.name)) || s.name;
        const item = document.createElement('span');
        item.className = 'summary-service-tag';
        item.textContent = `• ${serviceName} (${s.currentPrice.toLocaleString('ru-RU')} ${this.t('currency')})`;
        servicesContainer.appendChild(item);
      });
    }
  },

  async submitBooking() {
    const nameInput = document.getElementById('clientNameInput');
    const phoneInput = document.getElementById('clientPhoneInput');

    const clientName = nameInput?.value.trim();
    const clientPhone = phoneInput?.value.trim();

    if (!clientName) {
      this.showToast(this.t('err_name_req'));
      nameInput?.focus();
      return;
    }

    if (!clientPhone || clientPhone.length < 7) {
      this.showToast(this.t('err_phone_req'));
      phoneInput?.focus();
      return;
    }

    if (this.state.selectedServices.length === 0) {
      this.showToast(this.t('err_select_service'));
      return;
    }

    const payload = {
      telegram_id: this.user.id,
      client_name: clientName,
      client_phone: clientPhone,
      client_username: this.user.username,
      barber_id: this.state.selectedBarber.id,
      service_ids: this.state.selectedServices.map(s => s.id),
      appointment_date: this.state.selectedDate,
      appointment_time: this.state.selectedTime
    };

    const confirmBtn = document.getElementById('confirmBookingBtn');
    if (confirmBtn) {
      confirmBtn.disabled = true;
      confirmBtn.innerHTML = `<span>${this.t('submitting')}</span>`;
    }

    try {
      const res = await fetch('/api/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Booking error');
      }

      this.haptic('success');

      // Fill success receipt
      const receipt = document.getElementById('successReceipt');
      if (receipt) {
        receipt.innerHTML = `
          <div class="receipt-row">
            <span class="receipt-label">${this.t('receipt_id')}</span>
            <span class="receipt-val">#BRON-${data.appointment_id}</span>
          </div>
          <div class="receipt-row">
            <span class="receipt-label">${this.t('receipt_barber')}</span>
            <span class="receipt-val">${data.barber} (${data.category})</span>
          </div>
          <div class="receipt-row">
            <span class="receipt-label">${this.t('receipt_datetime')}</span>
            <span class="receipt-val">${data.date} • ${data.time}</span>
          </div>
          <div class="receipt-row">
            <span class="receipt-label">${this.t('receipt_total')}</span>
            <span class="receipt-val" style="color: var(--gold-primary); font-weight: 800;">${data.total_price.toLocaleString('ru-RU')} ${this.t('currency')}</span>
          </div>
        `;
      }

      this.goToStep('stepSuccess');
      if (this.user.id) {
        this.fetchMyBookings();
      }
    } catch (e) {
      this.haptic('error');
      this.showToast(e.message || 'Error');
    } finally {
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = `<span>${this.t('btn_submit_booking')}</span>`;
      }
    }
  },

  // ================= MY BOOKINGS =================
  async fetchMyBookings() {
    if (!this.user.id) return;
    try {
      const res = await fetch(`/api/my-bookings?telegram_id=${this.user.id}`);
      if (res.ok) {
        this.state.myBookings = await res.json();
        const dot = document.getElementById('bookingsDot');
        if (dot) {
          const activeCount = this.state.myBookings.filter(b => b.status === 'pending' || b.status === 'confirmed').length;
          dot.style.display = activeCount > 0 ? 'block' : 'none';
        }
      }
    } catch (e) {
      console.warn('My bookings fetch error:', e);
    }
  },

  openBookingsDrawer() {
    const drawer = document.getElementById('bookingsDrawer');
    if (!drawer) return;

    this.renderMyBookingsList();
    drawer.classList.add('active');
  },

  closeBookingsDrawer() {
    const drawer = document.getElementById('bookingsDrawer');
    if (drawer) drawer.classList.remove('active');
  },

  renderMyBookingsList() {
    const list = document.getElementById('myBookingsList');
    if (!list) return;

    if (!this.state.myBookings || this.state.myBookings.length === 0) {
      list.innerHTML = `
        <div class="drawer-empty">
          ${this.t('no_bookings')}
        </div>
      `;
      return;
    }

    list.innerHTML = '';
    this.state.myBookings.forEach(b => {
      const statusLabels = {
        pending: this.t('status_pending'),
        confirmed: this.t('status_confirmed'),
        completed: this.t('status_completed'),
        cancelled: this.t('status_cancelled')
      };

      const canCancel = (b.status === 'pending' || b.status === 'confirmed');
      const item = document.createElement('div');
      item.className = 'booking-item-card';
      item.innerHTML = `
        <div class="item-top">
          <span class="item-id">#BRON-${b.id}</span>
          <span class="item-status ${b.status}">${statusLabels[b.status] || b.status}</span>
        </div>
        <div class="item-details">
          <div><b>${this.t('label_barber')}</b> ${b.barber_name} (${b.barber_category})</div>
          <div><b>${this.t('label_datetime')}</b> ${b.appointment_date} • ${b.appointment_time}</div>
          <div><b>${this.t('receipt_total')}</b> ${b.total_price.toLocaleString('ru-RU')} ${this.t('currency')}</div>
        </div>
        ${canCancel ? `<button class="item-cancel-btn" data-id="${b.id}" type="button">${this.t('cancel_btn')}</button>` : ''}
      `;

      if (canCancel) {
        item.querySelector('.item-cancel-btn')?.addEventListener('click', (e) => {
          e.stopPropagation();
          this.cancelBooking(b.id);
        });
      }

      list.appendChild(item);
    });
  },

  async cancelBooking(appointmentId) {
    const confirmText = `${this.t('cancel_confirm', { id: appointmentId })}`;
    if (!confirm(confirmText)) {
      return;
    }

    try {
      const res = await fetch('/api/cancel-booking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          appointment_id: appointmentId,
          telegram_id: this.user.id
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Cancel error');

      this.showToast(this.t('booking_cancelled'));
      await this.fetchMyBookings();
      this.renderMyBookingsList();
    } catch (e) {
      this.showToast(e.message || 'Error');
    }
  },

  // ================= TOAST NOTIFICATION =================
  showToast(message) {
    const toast = document.getElementById('toastMessage');
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add('show');

    if (this._toastTimer) clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }
};

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
