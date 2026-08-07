const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

navToggle.addEventListener('click', () => {
  navToggle.classList.toggle('open');
  navLinks.classList.toggle('open');
});

navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navToggle.classList.remove('open');
    navLinks.classList.remove('open');
  });
});

const faqQuestions = document.querySelectorAll('.faq-q');

faqQuestions.forEach((question) => {
  question.addEventListener('click', () => {
    const item = question.parentElement;
    const answer = item.querySelector('.faq-a');
    const isOpen = item.classList.contains('open');

    faqQuestions.forEach((q) => {
      const other = q.parentElement;
      other.classList.remove('open');
      other.querySelector('.faq-a').style.maxHeight = null;
      q.setAttribute('aria-expanded', 'false');
    });

    if (!isOpen) {
      item.classList.add('open');
      answer.style.maxHeight = answer.scrollHeight + 'px';
      question.setAttribute('aria-expanded', 'true');
    }
  });
});

const revealEls = document.querySelectorAll('.card, .fact, .term, .faq-item');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

revealEls.forEach((el) => el.classList.add('reveal'));
revealEls.forEach((el) => observer.observe(el));

const stats = document.querySelectorAll('.stat');

const statsObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const stat = entry.target;
      const numEl = stat.querySelector('.stat-num');
      const target = parseFloat(stat.dataset.count);
      const suffix = stat.dataset.suffix || '';
      const decimals = parseInt(stat.dataset.decimals || '0', 10);
      const duration = 1600;
      const start = performance.now();

      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = target * eased;
        numEl.textContent = value.toFixed(decimals) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      };

      requestAnimationFrame(tick);
      statsObserver.unobserve(stat);
    });
  },
  { threshold: 0.4 }
);

stats.forEach((stat) => statsObserver.observe(stat));
