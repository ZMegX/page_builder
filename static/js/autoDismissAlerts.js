// Auto-dismiss, pause-on-hover, progress animation for Bootstrap alerts
(function () {
  const alerts = document.querySelectorAll('.alert-modern[data-autodismiss="true"]');

  alerts.forEach(alert => {
    const timeout = parseInt(alert.getAttribute('data-timeout'), 10) || 10000;
    const wantsProgress = alert.getAttribute('data-progress') === 'true';
    const progressEl = wantsProgress ? alert.querySelector('.alert-progress') : null;

    let startTime = performance.now();
    let remaining = timeout;
    let rafId = null;
    let closed = false;

    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);

    function animateProgress(timestamp) {
      if (!progressEl) return;
      const elapsed = timestamp - startTime;
      const ratio = Math.min(1, elapsed / timeout);
      progressEl.style.transform = `scaleX(${1 - ratio})`;
      if (ratio < 1 && !closed) {
        rafId = requestAnimationFrame(animateProgress);
      }
    }

    function closeAlert() {
      if (closed) return;
      closed = true;
      try { bsAlert.close(); } catch (e) { alert.remove(); }
    }

    let timerId = setTimeout(closeAlert, timeout);

    if (progressEl) {
      // Kick off progress animation
      requestAnimationFrame(animateProgress);
    }

    function pause() {
      if (closed) return;
      clearTimeout(timerId);
      if (progressEl) {
        alert.classList.add('is-paused');
        cancelAnimationFrame(rafId);
        const now = performance.now();
        const elapsed = now - startTime;
        remaining = Math.max(0, timeout - elapsed);
      }
    }

    function resume() {
      if (closed) return;
      if (remaining <= 0) {
        closeAlert();
        return;
      }
      startTime = performance.now() - (timeout - remaining);
      timerId = setTimeout(closeAlert, remaining);
      if (progressEl) {
        alert.classList.remove('is-paused');
        rafId = requestAnimationFrame(animateProgress);
      }
    }

    alert.addEventListener('mouseenter', pause);
    alert.addEventListener('focusin', pause);
    alert.addEventListener('mouseleave', resume);
    alert.addEventListener('focusout', resume);

    // If user clicks close, mark closed
    alert.addEventListener('closed.bs.alert', () => {
      closed = true;
      if (progressEl) cancelAnimationFrame(rafId);
    });
  });
})();