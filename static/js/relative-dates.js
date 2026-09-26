// Keep the server-rendered absolute date visible when JavaScript is unavailable.
(() => {
  const formatter = new Intl.RelativeTimeFormat(document.documentElement.lang || 'en', {
    numeric: 'auto',
  });

  function relativeDate(date, now) {
    const elapsed = (now - date.getTime()) / 1000;
    if (!Number.isFinite(elapsed) || elapsed < 0) return '';
    if (elapsed < 60) return 'just now';
    if (elapsed < 3600) return formatter.format(-Math.floor(elapsed / 60), 'minute');
    if (elapsed < 86400) return formatter.format(-Math.floor(elapsed / 3600), 'hour');
    if (elapsed < 604800) return formatter.format(-Math.floor(elapsed / 86400), 'day');
    if (elapsed < 2592000) return formatter.format(-Math.floor(elapsed / 604800), 'week');
    if (elapsed < 31536000) return formatter.format(-Math.floor(elapsed / 2592000), 'month');
    return formatter.format(-Math.floor(elapsed / 31536000), 'year');
  }

  function updateDates() {
    const now = Date.now();
    document.querySelectorAll('time[data-relative-date], .feed--photo-grid .shot-card-date').forEach((time) => {
      const date = new Date(time.dateTime);
      if (Number.isNaN(date.getTime())) return;
      if (!time.dataset.absoluteDate) time.dataset.absoluteDate = time.textContent.trim();
      const relative = relativeDate(date, now);
      time.textContent = relative ? `${relative} · ${time.dataset.absoluteDate}` : time.dataset.absoluteDate;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateDates);
  } else {
    updateDates();
  }
  window.addEventListener('view-transition-complete', updateDates);
  document.addEventListener('htmx:afterSwap', updateDates);
  window.setInterval(updateDates, 60_000);
})();
