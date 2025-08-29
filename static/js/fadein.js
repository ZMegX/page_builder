document.addEventListener("DOMContentLoaded", function () {
  const elements = document.querySelectorAll(".fade-in-element, .feature-card");

  if (!("IntersectionObserver" in window)) {
    elements.forEach(el => el.classList.add("visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        if (entry.target.classList.contains("feature-card")) {
          // staggered animation for feature cards
          const cards = entry.target.parentElement.querySelectorAll(".feature-card");
          cards.forEach((card, index) => {
            setTimeout(() => {
              card.classList.add("visible");
            }, index * 200); // 200ms delay per card
          });
          observer.unobserve(entry.target); // stop observing once animated
        } else {
          // normal fade-in
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      }
    });
  }, { threshold: 0.2 });

  elements.forEach((el) => observer.observe(el));
});
