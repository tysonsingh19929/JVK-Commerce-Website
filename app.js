/**
 * JVK COMMERCE - OFFICIAL APPLICATION SCRIPT
 * Replit Minimal Approved Design + Enterprise FAQ & Interactive Features
 * 100% Vector SVGs, Zero Emojis
 */

document.addEventListener('DOMContentLoaded', () => {

  // ==========================================================================
  // 1. MOBILE NAVIGATION DRAWER
  // ==========================================================================
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');
  const iconMenu = menuToggle ? menuToggle.querySelector('.icon-menu') : null;
  const iconClose = menuToggle ? menuToggle.querySelector('.icon-close') : null;

  function toggleMobileNav() {
    if (!navLinks || !menuToggle) return;
    const isOpen = navLinks.classList.toggle('open');
    document.body.classList.toggle('nav-open', isOpen);
    menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    menuToggle.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
    if (iconMenu && iconClose) {
      iconMenu.style.display = isOpen ? 'none' : 'block';
      iconClose.style.display = isOpen ? 'block' : 'none';
    }
  }

  function closeMobileNav() {
    if (!navLinks || !menuToggle) return;
    navLinks.classList.remove('open');
    document.body.classList.remove('nav-open');
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Open menu');
    if (iconMenu && iconClose) {
      iconMenu.style.display = 'block';
      iconClose.style.display = 'none';
    }
  }

  if (menuToggle) {
    menuToggle.addEventListener('click', toggleMobileNav);
  }

  // Close mobile nav when clicking any nav link inside drawer
  if (navLinks) {
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('click', () => {
        closeMobileNav();
      });
    });
  }

  // Close mobile drawer on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navLinks && navLinks.classList.contains('open')) {
      closeMobileNav();
    }
  });

  // Automatically close mobile nav if window expands to desktop size
  window.addEventListener('resize', () => {
    if (window.innerWidth > 720 && navLinks && navLinks.classList.contains('open')) {
      closeMobileNav();
    }
  });

  // ==========================================================================
  // 2. CONTACT ENQUIRY FORM -> DIRECT WHATSAPP LINK GENERATOR
  // Company WhatsApp: +971 554741125
  // ==========================================================================
  const WHATSAPP_COMPANY_NUMBER = '971554741125';

  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('contactName')?.value.trim() || '';
      const company = document.getElementById('contactCompany')?.value.trim() || 'Not provided';
      const email = document.getElementById('contactEmail')?.value.trim() || '';
      const market = document.getElementById('contactMarket')?.value.trim() || 'Not specified';
      const message = document.getElementById('contactMessage')?.value.trim() || '';

      const lines = [
        'Hello JVK Commerce, I would like to enquire about marketplace growth support.',
        '',
        `*Name:* ${name}`,
        `*Company / Brand:* ${company}`,
        `*Email:* ${email}`,
        `*Market of Interest:* ${market}`,
        `*Message:* ${message}`,
        '',
        'Sent via JVK Commerce Portal (https://jvkcommerce.com)'
      ];

      // 1. Asynchronously persist enquiry record in backend database
      fetch('/api/enquiries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, company, email, market, message })
      }).catch(err => console.warn('Backend enquiry sync:', err));

      // 2. Open WhatsApp directly to company number with pre-filled enquiry
      const waUrl = `https://wa.me/${WHATSAPP_COMPANY_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`;
      window.open(waUrl, '_blank', 'noopener,noreferrer');
    });
  }

  // ==========================================================================
  // 3. LEARNING OPT-IN FORM (BUILD IN-HOUSE CAPABILITY)
  // ==========================================================================
  const learningForm = document.getElementById('learningForm');
  const learningStatus = document.getElementById('learningStatusSuccess');

  if (learningForm) {
    learningForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = document.getElementById('learning-email');
      const whatsappInput = document.getElementById('learning-whatsapp');
      const consentInput = document.getElementById('learning-consent');

      const email = emailInput ? emailInput.value.trim() : '';
      const phone = whatsappInput ? whatsappInput.value.trim() : '';
      const consent = consentInput ? consentInput.checked : false;

      if (email && consent) {
        try {
          const stored = JSON.parse(localStorage.getItem('jvk_learning_optins') || '[]');
          stored.push({ email, phone, consent, date: new Date().toISOString() });
          localStorage.setItem('jvk_learning_optins', JSON.stringify(stored));
        } catch (err) {
          console.warn('Storage unavailable:', err);
        }

        // Asynchronously persist learning opt-in in backend database
        fetch('/api/learning', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, whatsapp: phone, consent: true })
        }).catch(err => console.warn('Backend learning sync:', err));

        if (learningStatus) {
          learningStatus.style.display = 'block';
          setTimeout(() => {
            learningStatus.style.display = 'none';
          }, 6000);
        }

        learningForm.reset();
      }
    });
  }

  // ==========================================================================
  // 4. ENTERPRISE FAQ ACCORDION
  // ==========================================================================
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      if (!item) return;
      const isExpanded = btn.getAttribute('aria-expanded') === 'true';

      // Close other open FAQ items for a clean accordion flow
      document.querySelectorAll('.faq-item').forEach(other => {
        if (other !== item) {
          other.classList.remove('active');
          const otherBtn = other.querySelector('.faq-question');
          if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
        }
      });

      if (isExpanded) {
        item.classList.remove('active');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        item.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // Open the first FAQ item by default for visual affordance
  if (faqQuestions.length > 0) {
    const firstItem = faqQuestions[0].closest('.faq-item');
    if (firstItem) {
      firstItem.classList.add('active');
      faqQuestions[0].setAttribute('aria-expanded', 'true');
    }
  }

});
