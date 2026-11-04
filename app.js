/**
 * JVK COMMERCE - BESPOKE LUXURY MARKETPLACE PORTAL
 * Interactive Controller: Mobile Menu Drawer, Service Tabs Switcher,
 * FAQ Accordion, WhatsApp Enquiry Generator, and Operator Academy Intake
 * Strict Requirements: 100% Vector SVGs, Zero Emojis
 */

document.addEventListener('DOMContentLoaded', () => {

  // ==========================================================================
  // 1. FULL-VIEWPORT MOBILE MENU DRAWER
  // ==========================================================================
  const menuToggle = document.getElementById('menu-toggle');
  const mobileDrawer = document.getElementById('mobile-nav-drawer');
  const iconMenu = menuToggle ? menuToggle.querySelector('.icon-menu') : null;
  const iconClose = menuToggle ? menuToggle.querySelector('.icon-close') : null;

  function openMobileNav() {
    if (!mobileDrawer || !menuToggle) return;
    mobileDrawer.classList.add('open');
    mobileDrawer.setAttribute('aria-hidden', 'false');
    menuToggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('nav-open');
    if (iconMenu) iconMenu.style.display = 'none';
    if (iconClose) iconClose.style.display = 'block';
  }

  function closeMobileNav() {
    if (!mobileDrawer || !menuToggle) return;
    mobileDrawer.classList.remove('open');
    mobileDrawer.setAttribute('aria-hidden', 'true');
    menuToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('nav-open');
    if (iconMenu) iconMenu.style.display = 'block';
    if (iconClose) iconClose.style.display = 'none';
  }

  if (menuToggle && mobileDrawer) {
    menuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = mobileDrawer.classList.contains('open');
      isOpen ? closeMobileNav() : openMobileNav();
    });

    // Close menu when clicking any link inside the mobile drawer
    mobileDrawer.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        closeMobileNav();
      });
    });

    // Close when clicking outside header & drawer
    document.addEventListener('click', (e) => {
      if (mobileDrawer.classList.contains('open') && !e.target.closest('#site-header')) {
        closeMobileNav();
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileDrawer.classList.contains('open')) {
        closeMobileNav();
      }
    });

    // Close drawer if viewport is resized to desktop width
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900 && mobileDrawer.classList.contains('open')) {
        closeMobileNav();
      }
    });
  }

  // ==========================================================================
  // 2. INTERACTIVE SERVICE DISCIPLINE TABS (FROM ATTACHMENT 1)
  // ==========================================================================
  const serviceTabs = document.querySelectorAll('.service-tab-btn');
  const servicePanels = document.querySelectorAll('.service-panel');

  if (serviceTabs.length > 0 && servicePanels.length > 0) {
    serviceTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetId = tab.getAttribute('data-tab');

        // Deactivate all tabs
        serviceTabs.forEach(t => {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });

        // Deactivate all panels
        servicePanels.forEach(p => {
          p.classList.remove('active');
        });

        // Activate clicked tab
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');

        // Activate corresponding panel
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }
      });
    });
  }

  // ==========================================================================
  // 3. INTERACTIVE FAQ ACCORDION (ENTERPRISE SEO ACCORDION)
  // ==========================================================================
  const faqQuestions = document.querySelectorAll('.faq-question');

  if (faqQuestions.length > 0) {
    faqQuestions.forEach(btn => {
      btn.addEventListener('click', () => {
        const isExpanded = btn.getAttribute('aria-expanded') === 'true';
        const answerId = btn.getAttribute('aria-controls');
        const answerEl = document.getElementById(answerId);

        // Optional: close other FAQs for a clean accordion flow
        faqQuestions.forEach(otherBtn => {
          if (otherBtn !== btn) {
            otherBtn.classList.remove('active');
            otherBtn.setAttribute('aria-expanded', 'false');
            const otherAnsId = otherBtn.getAttribute('aria-controls');
            const otherAnsEl = document.getElementById(otherAnsId);
            if (otherAnsEl) {
              otherAnsEl.classList.remove('open');
            }
          }
        });

        // Toggle current FAQ
        if (isExpanded) {
          btn.classList.remove('active');
          btn.setAttribute('aria-expanded', 'false');
          if (answerEl) answerEl.classList.remove('open');
        } else {
          btn.classList.add('active');
          btn.setAttribute('aria-expanded', 'true');
          if (answerEl) answerEl.classList.add('open');
        }
      });
    });
  }

  // ==========================================================================
  // 4. MAIN ENQUIRY FORM -> WHATSAPP HANDOFF
  // ==========================================================================
  const contactForm = document.getElementById('contact-form');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('contact-name')?.value.trim() || 'Not provided';
      const company = document.getElementById('contact-company')?.value.trim() || 'Not provided';
      const email = document.getElementById('contact-email')?.value.trim() || 'Not provided';
      const market = document.getElementById('contact-market')?.value.trim() || 'Not specified';
      const message = document.getElementById('contact-message')?.value.trim() || '';

      const lines = [
        "Hello JVK Commerce, I would like to enquire about marketplace growth support.",
        "",
        `Name: ${name}`,
        `Company: ${company}`,
        `Corporate Email: ${email}`,
        `Market of Interest: ${market}`,
        `Message: ${message}`,
        "",
        "Please connect me with an account director."
      ];

      const fullMessage = lines.join('\n');
      const waUrl = `https://wa.me/?text=${encodeURIComponent(fullMessage)}`;
      window.open(waUrl, '_blank', 'noopener,noreferrer');
    });
  }

  // ==========================================================================
  // 5. OPERATOR ACADEMY OPT-IN FORM (FEATURE #2: IN-HOUSE LEARNING)
  // ==========================================================================
  const learnForm = document.getElementById('learn-form');
  const learnSuccess = document.getElementById('learn-success');

  if (learnForm) {
    learnForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('learn-name')?.value.trim() || 'Not provided';
      const email = document.getElementById('learn-email')?.value.trim() || 'Not provided';
      const phone = document.getElementById('learn-phone')?.value.trim() || 'Not provided';
      const focus = document.getElementById('learn-focus')?.value || 'Complete Account Operations';

      const lines = [
        "Hello JVK Commerce, I am interested in learning to effectively run marketplace services myself (Operator Academy).",
        "",
        `Name: ${name}`,
        `Corporate Email: ${email}`,
        `WhatsApp / Phone: ${phone}`,
        `Primary Learning Track: ${focus}`,
        "",
        "Please share the operator curriculum, syllabus, and enrollment details."
      ];

      const fullMessage = lines.join('\n');
      const waUrl = `https://wa.me/?text=${encodeURIComponent(fullMessage)}`;

      // Show success feedback state
      learnForm.style.display = 'none';
      if (learnSuccess) {
        learnSuccess.style.display = 'block';
      }

      // Open WhatsApp pre-filled window after brief visual confirmation
      setTimeout(() => {
        window.open(waUrl, '_blank', 'noopener,noreferrer');
      }, 600);
    });
  }

  // ==========================================================================
  // 6. SUBTLE ORBIT HOVER INTERACTION (DESKTOP POINTERS ONLY)
  // ==========================================================================
  const orbit = document.querySelector('.orbit');
  if (orbit && window.matchMedia('(hover: hover)').matches) {
    orbit.addEventListener('mousemove', (e) => {
      const rect = orbit.getBoundingClientRect();
      const x = (e.clientX - rect.left - rect.width / 2) / 30;
      const y = (e.clientY - rect.top - rect.height / 2) / 30;
      orbit.style.transform = `perspective(1000px) rotateY(${x}deg) rotateX(${-y}deg)`;
    });

    orbit.addEventListener('mouseleave', () => {
      orbit.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg)';
      orbit.style.transition = 'transform 0.5s ease-out';
    });

    orbit.addEventListener('mouseenter', () => {
      orbit.style.transition = 'none';
    });
  }

});
