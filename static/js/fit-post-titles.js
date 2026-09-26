(() => {
  window.__titleFitInitialized = true;
  const selector = '.post-header__title-row > h1';
  let title;
  let resizeObserver;
  let frame;
  let fontReady = false;

  function fit() {
    frame = null;
    if (!fontReady || !title || !title.isConnected) return;

    title.style.fontSize = '';
    title.style.whiteSpace = 'nowrap';

    const available = title.clientWidth;
    if (!available) {
      title.style.whiteSpace = '';
      return;
    }

    const rootSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    const defaultSize = parseFloat(getComputedStyle(title).fontSize);
    const isDailyNote = /^\d{4}-\d{2}-\d{2} Notes$/.test(title.textContent.trim());
    const minimum = Math.min(defaultSize, rootSize * (isDailyNote ? 1.3 : 2.25));
    const maximum = defaultSize * 1.08;
    const range = document.createRange();
    range.selectNodeContents(title);

    function fits(size) {
      title.style.fontSize = `${size}px`;
      return range.getBoundingClientRect().width <= available - 2;
    }

    if (fits(maximum)) {
      title.style.fontSize = `${maximum}px`;
    } else if (!fits(minimum)) {
      title.style.fontSize = `${minimum}px`;
      title.style.whiteSpace = '';
      title.dataset.titleFitted = '';
      return;
    } else {
      let low = minimum;
      let high = maximum;
      for (let i = 0; i < 10; i++) {
        const middle = (low + high) / 2;
        if (fits(middle)) low = middle;
        else high = middle;
      }
      title.style.fontSize = `${low}px`;
    }

    title.style.whiteSpace = '';
    title.dataset.titleFitted = '';
  }

  function scheduleFit() {
    if (frame) cancelAnimationFrame(frame);
    frame = requestAnimationFrame(fit);
  }

  function connect() {
    const nextTitle = document.querySelector(selector);
    if (nextTitle === title) return;

    resizeObserver?.disconnect();
    title = nextTitle;
    if (!title) return;

    document.documentElement.classList.add('title-fit-enabled');
    resizeObserver = new ResizeObserver(scheduleFit);
    resizeObserver.observe(title);
    if (fontReady) fit();
  }

  connect();
  const fontLoad = document.fonts.load('300 72px "Playwrite VN"').catch(() => {});
  Promise.race([fontLoad, new Promise(resolve => setTimeout(resolve, 3000))])
    .then(() => {
      fontReady = true;
      scheduleFit();
    });
  fontLoad.then(scheduleFit);
  new MutationObserver(connect).observe(document.body, { childList: true, subtree: true });
  window.addEventListener('view-transition-complete', connect);
})();
