
document.addEventListener('DOMContentLoaded', function() {
	var header = document.getElementById('profile-header-animated');
	if (header) {
		setTimeout(function() {
			header.classList.add('animated');
		}, 100);
	}
});
