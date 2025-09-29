
document.addEventListener('DOMContentLoaded', function() {
	var heroSection = document.querySelector('.hero-section.landing-restaurant-page');
	if (heroSection) {
		var bgUrl = heroSection.getAttribute('data-bg');
		if (bgUrl) {
			heroSection.style.backgroundImage = 'url("' + bgUrl + '")';
			heroSection.style.backgroundPosition = 'center center';
			heroSection.style.backgroundRepeat = 'no-repeat';
			heroSection.style.backgroundSize = 'cover';
		}
	}
});
