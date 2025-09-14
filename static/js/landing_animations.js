// Animate fade-in sections on scroll
document.addEventListener("DOMContentLoaded", function() {
  const faders = document.querySelectorAll('.fade-in-section');
  const appearOptions = { threshold: 0.15, rootMargin: "0px 0px -40px 0px" };
  const appearOnScroll = new IntersectionObserver(function(entries, observer) {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, appearOptions);

  faders.forEach(fader => appearOnScroll.observe(fader));
});