/**
 * Culture Barbershop - Telegram Web App Interactive Booking Logic
 */

const tg = window.Telegram?.WebApp;

const app = {
  // State
  state: {
    selectedCategory: 'TOP',
    selectedBarber: null,
    selectedServices: [],
    selectedDate: null,
    selectedTime: null,
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

  init() {
    // 1. Initialize Telegram WebApp SDK
    if (tg) {
      try {
        tg.ready();
        tg.expand();
        if (tg.enableClosingConfirmation) {
          tg.enableClosingConfirmation();
        }

        // Get user from Telegram
        const tgUser = tg.initDataUnsafe?.user;
        if (tgUser) {
          this.user.id = tgUser.id;
          this.user.name = [tgUser.first_name, tgUser.last_name].filter(Boolean).join(' ');
          this.user.username = tgUser.username || '';
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

    // 2. Setup event listeners
    this.setupEventListeners();

    // 3. Setup dates in carousel
    this.initDateCarousel();

    // 4. Fetch initial data from server
    this.fetchData();

    // 5. Check user bookings
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
    this.haptic('light');
    document.querySelectorAll('.view-step').forEach(step => {
      step.classList.remove('active');
    });

    const target = document.getElementById(stepId);
    if (target) {
      target.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Manage Telegram BackButton visibility
    if (tg?.BackButton) {
      if (stepId === 'stepCategories') {
        tg.BackButton.hide();
      } else {
        tg.BackButton.show();
      }
    }
  },

  showToast(msg) {
    const toast = document.getElementById('toastMessage');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
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
    } catch (e) {
      console.error('Data fetch error:', e);
    }
  },

  // ================= STEP 1: CATEGORY SELECTION =================
  selectCategory(category) {
    this.haptic('medium');
    this.state.selectedCategory = category;
    
    // Update step 2 pill text
    const pill = document.getElementById('selectedTierPill');
    if (pill) {
      pill.textContent = `${category} BARBER`;
    }

    // Filter and render barbers in step 2
    this.renderBarbers(category);
    this.goToStep('stepBarbers');
  },

  // ================= STEP 2: BARBERS =================
  renderBarbers(category) {
    const container = document.getElementById('barbersListContainer');
    if (!container) return;

    const filtered = this.state.allBarbers.filter(b => b.category === category);
    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="drawer-empty">
          Ushbu toifada hozircha ustalar mavjud emas.<br>
          Iltimos, boshqa toifani tanlang.
        </div>
      `;
      return;
    }

    container.innerHTML = '';
    filtered.forEach(barber => {
      const isSelected = this.state.selectedBarber?.id === barber.id;
      const initial = barber.name.charAt(0).toUpperCase();

      const card = document.createElement('div');
      card.className = `barber-card ${isSelected ? 'selected' : ''}`;
      card.innerHTML = `
        <div class="barber-avatar-wrap">
          <span>${initial}</span>
        </div>
        <div class="barber-details">
          <div class="barber-name-row">
            <span class="barber-name">${barber.name}</span>
            <span class="barber-cat-badge">${barber.category}</span>
          </div>
          <div class="barber-meta">
            <span class="barber-rating">⭐ ${barber.rating || '5.0'}</span>
            <span>•</span>
            <span>${barber.experience_years || 3} yil tajriba</span>
          </div>
        </div>
        <button class="barber-select-btn">${isSelected ? 'Tanlandi' : 'Tanlash'}</button>
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

    // Update pill in step 3
    const pill = document.getElementById('selectedBarberPill');
    if (pill) {
      pill.textContent = barber.name;
    }

    // Render services with this barber's tier pricing
    this.renderServices(barber.category);
    this.goToStep('stepServices');
  },

  // ================= STEP 3: SERVICES =================
  renderServices(category) {
    const container = document.getElementById('servicesListContainer');
    if (!container) return;

    container.innerHTML = '';
    const catCol = `price_${category.toLowerCase()}`;

    this.state.allServices.forEach(srv => {
      const price = srv[catCol] || srv.price_pro || 80000;
      const isChecked = this.state.selectedServices.some(s => s.id === srv.id);
      const priceFormatted = `${price.toLocaleString('ru-RU')} UZS`;

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
            <span class="service-name">${srv.name}</span>
            <span class="service-duration">⏱ ${srv.duration_min || 45} daqiqa</span>
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

    if (countEl) countEl.textContent = `${count} xizmat tanlandi`;
    if (totalEl) totalEl.textContent = `${total.toLocaleString('ru-RU')} UZS`;

    if (btn) {
      btn.disabled = (count === 0);
    }
  },

  // ================= STEP 4: DATE & TIME =================
  initDateCarousel() {
    const carousel = document.getElementById('dateCarousel');
    if (!carousel) return;

    carousel.innerHTML = '';
    const daysUz = ['Yak', 'Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan'];
    const monthsUz = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyun', 'Iyul', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'];

    const today = new Date();

    for (let i = 0; i < 10; i++) {
      const d = new Date();
      d.setDate(today.getDate() + i);

      const yyyy = d.getFullYear();
      const mm = String(d.getMonth() + 1).padStart(2, '0');
      const dd = String(d.getDate()).padStart(2, '0');
      const dateString = `${yyyy}-${mm}-${dd}`;

      let dayLabel = daysUz[d.getDay()];
      if (i === 0) dayLabel = 'Bugun';
      else if (i === 1) dayLabel = 'Erta';

      const pill = document.createElement('div');
      pill.className = `date-pill ${i === 0 ? 'active' : ''}`;
      pill.setAttribute('data-date', dateString);
      pill.innerHTML = `
        <span class="date-day-name">${dayLabel}</span>
        <span class="date-number">${d.getDate()}</span>
        <span class="date-month-name">${monthsUz[d.getMonth()]}</span>
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
      if (i === 0) {
        this.state.selectedDate = dateString;
      }
    }
  },

  async loadSlots() {
    const grid = document.getElementById('slotsGrid');
    if (!grid || !this.state.selectedBarber || !this.state.selectedDate) return;

    grid.innerHTML = '<div style="grid-column: span 3; text-align: center; color: #888;">Vaqtlar yuklanmoqda...</div>';

    try {
      const res = await fetch(`/api/slots?barber_id=${this.state.selectedBarber.id}&date=${this.state.selectedDate}`);
      if (!res.ok) throw new Error('Slotlarni yuklashda xatolik');
      const data = await res.json();

      grid.innerHTML = '';
      const availableSet = new Set(data.available_slots || []);

      data.all_work_hours.forEach(hour => {
        const isAvail = availableSet.has(hour);
        const isSelected = this.state.selectedTime === hour;

        const btn = document.createElement('button');
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
      grid.innerHTML = '<div style="grid-column: span 3; color: red;">Xatolik yuz berdi.</div>';
    }
  },

  updateDateTimeSummary() {
    const infoEl = document.getElementById('dateTimeSelectedInfo');
    const totalEl = document.getElementById('dateTimeTotal');
    const btn = document.getElementById('toConfirmBtn');

    const total = this.state.selectedServices.reduce((sum, s) => sum + s.currentPrice, 0);
    if (totalEl) totalEl.textContent = `${total.toLocaleString('ru-RU')} UZS`;

    if (this.state.selectedDate && this.state.selectedTime) {
      if (infoEl) infoEl.textContent = `${this.state.selectedDate} • ${this.state.selectedTime}`;
      if (btn) btn.disabled = false;
    } else {
      if (infoEl) infoEl.textContent = 'Vaqt tanlanmagan';
      if (btn) btn.disabled = true;
    }
  },

  // ================= STEP 5: SUMMARY & SUBMISSION =================
  renderSummary() {
    const barber = this.state.selectedBarber;
    const total = this.state.selectedServices.reduce((sum, s) => sum + s.currentPrice, 0);

    document.getElementById('sumBarberName').textContent = barber?.name || '—';
    document.getElementById('sumBarberCategory').textContent = barber ? `${barber.category} Barber` : '—';
    document.getElementById('sumDateTime').textContent = `${this.state.selectedDate} | ${this.state.selectedTime}`;
    document.getElementById('sumTotalPrice').textContent = `${total.toLocaleString('ru-RU')} UZS`;

    const servicesContainer = document.getElementById('sumServicesList');
    if (servicesContainer) {
      servicesContainer.innerHTML = '';
      this.state.selectedServices.forEach(s => {
        const item = document.createElement('span');
        item.className = 'summary-service-tag';
        item.textContent = `• ${s.name} (${s.currentPrice.toLocaleString('ru-RU')} UZS)`;
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
      this.showToast('Iltimos, ismingizni kiriting');
      nameInput?.focus();
      return;
    }

    if (!clientPhone || clientPhone.length < 7) {
      this.showToast('Iltimos, to\'g\'ri telefon raqam kiriting');
      phoneInput?.focus();
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
      confirmBtn.innerHTML = '<span>Saqlanmoqda...</span>';
    }

    try {
      const res = await fetch('/api/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Bron qilishda xatolik');
      }

      this.haptic('success');

      // Fill success receipt
      const receipt = document.getElementById('successReceipt');
      if (receipt) {
        receipt.innerHTML = `
          <div class="receipt-row">
            <span class="receipt-label">Buyurtma ID:</span>
            <span class="receipt-val">#BRON-${data.appointment_id}</span>
          </div>
          <div class="receipt-row">
            <span class="receipt-label">Sartarosh:</span>
            <span class="receipt-val">${data.barber} (${data.category})</span>
          </div>
          <div class="receipt-row">
            <span class="receipt-label">Sana va Vaqt:</span>
            <span class="receipt-val">${data.date} • ${data.time}</span>
          </div>
          <div class="receipt-row">
            <span class="receipt-label">Jami summa:</span>
            <span class="receipt-val" style="color: var(--gold-primary);">${data.total_price.toLocaleString('ru-RU')} UZS</span>
          </div>
        `;
      }

      this.goToStep('stepSuccess');
      if (this.user.id) {
        this.fetchMyBookings();
      }
    } catch (e) {
      this.haptic('error');
      this.showToast(e.message || 'Xatolik yuz berdi');
    } finally {
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<span>TASDIQLASH VA BRON QILISH</span>';
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
          Sizda hali hech qanday bron mavjud emas.
        </div>
      `;
      return;
    }

    list.innerHTML = '';
    this.state.myBookings.forEach(b => {
      const statusLabels = {
        pending: 'Kutilmoqda ⏳',
        confirmed: 'Tasdiqlangan ✅',
        completed: 'Bajarilgan 💈',
        cancelled: 'Bekor qilingan ❌'
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
          <div><b>Usta:</b> ${b.barber_name} (${b.barber_category})</div>
          <div><b>Vaqt:</b> ${b.appointment_date} • ${b.appointment_time}</div>
          <div><b>Summa:</b> ${b.total_price.toLocaleString('ru-RU')} UZS</div>
        </div>
        ${canCancel ? `<button class="item-cancel-btn" data-id="${b.id}">Bekor qilish</button>` : ''}
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
    if (!confirm(`#BRON-${appointmentId} buyurtmasini bekor qilishni tasdiqlaysizmi?`)) {
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
      if (!res.ok) throw new Error(data.detail || 'Bekor qilishda xatolik');

      this.showToast('Bron bekor qilindi');
      await this.fetchMyBookings();
      this.renderMyBookingsList();
    } catch (e) {
      this.showToast(e.message || 'Xatolik');
    }
  }
};

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
