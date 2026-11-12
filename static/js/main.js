document.addEventListener('DOMContentLoaded', () => {
  const header = document.getElementById('siteHeader');
  const navLinks = document.querySelectorAll('.nav-links a');
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.getElementById('navLinks');
  const backToTop = document.getElementById('backToTop');
  const sections = document.querySelectorAll('main section[id]');
  const mobileViewport = window.matchMedia('(max-width: 768px)');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  const closeMenu = (restoreFocus = false) => {
    navMenu.classList.remove('active');
    navToggle.setAttribute('aria-expanded', 'false');
    if (restoreFocus) navToggle.focus();
  };

  navToggle.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('active');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
  navLinks.forEach((link) => link.addEventListener('click', () => closeMenu()));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && navMenu.classList.contains('active')) {
      closeMenu(true);
    }
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav')) closeMenu();
  });
  document.addEventListener('focusin', (event) => {
    if (!event.target.closest('.nav')) closeMenu();
  });
  mobileViewport.addEventListener('change', () => closeMenu());
  document.documentElement.classList.add('nav-ready');

  document.querySelectorAll('.skill-bar-fill').forEach((bar) => {
    bar.style.width = `${bar.dataset.level}%`;
  });

  const updateScrollState = () => {
    header.classList.toggle('scrolled', window.scrollY > 20);
    backToTop.classList.toggle('show', window.scrollY > 500);
    let current = 'home';
    sections.forEach((section) => {
      if (section.getBoundingClientRect().top <= 160) current = section.id;
    });
    navLinks.forEach((link) => {
      const active = link.hash === `#${current}`;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };

  let scrollPending = false;
  const scheduleUpdate = () => {
    if (scrollPending) return;
    scrollPending = true;
    window.requestAnimationFrame(() => {
      updateScrollState();
      scrollPending = false;
    });
  };
  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate);
  window.addEventListener('pageshow', scheduleUpdate);
  updateScrollState();

  // Content stays visible unless the observer is ready to reveal it.
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.remove('reveal-pending');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.reveal, .timeline-item').forEach((item) => {
      item.classList.add('reveal-pending');
      observer.observe(item);
    });
    reducedMotion.addEventListener('change', (event) => {
      if (event.matches) {
        observer.disconnect();
        document.querySelectorAll('.reveal-pending').forEach((item) => {
          item.classList.remove('reveal-pending');
        });
      }
    });
  }
});
