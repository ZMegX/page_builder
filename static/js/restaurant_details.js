(function () {
  const form = document.getElementById('restaurantForm');
  if (!form) return;

  const fieldset = document.getElementById('restaurantFieldset');
  const editBtn = document.getElementById('restaurantEditBtn');
  const cancelBtn = document.getElementById('restaurantCancelBtn');
  const saveBtn = document.getElementById('restaurantSaveBtn');

  const logoInput = document.getElementById('restaurantLogoInput');
  const logoPreview = document.getElementById('restaurantLogoPreview');
  const initialLogoSrc = logoPreview && logoPreview.getAttribute('src');

  function enterEdit() {
    if (fieldset) fieldset.disabled = false;
    if (editBtn) editBtn.classList.add('d-none');
    if (cancelBtn) cancelBtn.classList.remove('d-none');
    if (saveBtn) saveBtn.classList.remove('d-none');
  }

  function exitEdit() {
    if (fieldset) fieldset.disabled = true;
    if (editBtn) editBtn.classList.remove('d-none');
    if (cancelBtn) cancelBtn.classList.add('d-none');
    if (saveBtn) saveBtn.classList.add('d-none');
  }

  if (editBtn) editBtn.addEventListener('click', enterEdit);

  if (cancelBtn) {
    cancelBtn.addEventListener('click', function () {
      // Revert form fields to initial values
      form.reset();
      // Restore logo preview
      if (logoPreview) {
        if (initialLogoSrc) {
          logoPreview.src = initialLogoSrc;
          logoPreview.style.display = '';
        } else {
          logoPreview.removeAttribute('src');
          logoPreview.style.display = 'none';
        }
      }
      exitEdit();
    });
  }

  // Image preview
  if (logoInput && logoPreview) {
    logoInput.addEventListener('change', function () {
      const file = logoInput.files && logoInput.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        logoPreview.src = url;
        logoPreview.style.display = '';
      } else {
        if (initialLogoSrc) {
          logoPreview.src = initialLogoSrc;
          logoPreview.style.display = '';
        } else {
          logoPreview.removeAttribute('src');
          logoPreview.style.display = 'none';
        }
      }
    });
  }

  // Start in view mode
  exitEdit();
})();