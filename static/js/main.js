document.addEventListener('DOMContentLoaded', () => {
  const header = document.getElementById('siteHeader');
  const navLinks = document.querySelectorAll('.nav-links a');
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.getElementById('navLinks');

  const revealItems = document.querySelectorAll('.reveal');
  const staggerContainers = document.querySelectorAll('.reveal-stagger');
  const timelineItems = document.querySelectorAll('.timeline-item');

  const revealElements = () => {
    const triggerPoint = window.innerHeight * 0.9;

    revealItems.forEach((item) => {
      const itemTop = item.getBoundingClientRect().top;
      if (itemTop < triggerPoint) {
        item.classList.add('in-view');
      }
    });

    staggerContainers.forEach((container) => {
      const containerTop = container.getBoundingClientRect().top;
      if (containerTop < triggerPoint) {
        container.classList.add('in-view');
      }
    });

    timelineItems.forEach((item, index) => {
      const itemTop = item.getBoundingClientRect().top;
      if (itemTop < triggerPoint) {
        item.classList.add('visible');
        item.style.transitionDelay = `${index * 60}ms`;
      }
    });
  };

  const setActiveLink = () => {
    const sections = document.querySelectorAll('main section[id]');
    let current = '';

    sections.forEach((section) => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 140 && rect.bottom > 140) {
        current = section.id;
      }
    });

    navLinks.forEach((link) => {
      link.classList.toggle('active', link.getAttribute('href') === `#${current}`);
    });
  };

  window.toggleMenu = () => {
    const isOpen = navMenu.classList.toggle('active');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  };

  window.addEventListener('scroll', () => {
    if (header) {
      header.classList.toggle('scrolled', window.scrollY > 20);
    }
    setActiveLink();
    revealElements();
  }, { passive: true });

  window.addEventListener('resize', revealElements);

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('active');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });
  }

  document.querySelectorAll('.nav-links a').forEach((link) => {
    link.addEventListener('click', () => {
      if (navMenu) {
        navMenu.classList.remove('active');
      }
      if (navToggle) {
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  });

  revealElements();
  setActiveLink();
});
