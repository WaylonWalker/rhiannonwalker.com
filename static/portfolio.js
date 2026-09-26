(() => {
  document.documentElement.classList.add("portfolio-js");

  function markLoaded(image) {
    if (!image?.closest(".portfolio-photo")) return;
    image.classList.add("is-loaded");
    image.closest(".portfolio-photo").classList.add("is-loaded");
  }

  function revealReadyImages() {
    document.documentElement.classList.add("portfolio-js");
    document.querySelectorAll(".portfolio-photo img").forEach((image) => {
      if (image.complete && image.naturalWidth > 0) markLoaded(image);
    });
  }
  revealReadyImages();
  window.addEventListener("view-transition-complete", revealReadyImages);
  document.addEventListener("load", (event) => {
    if (event.target instanceof HTMLImageElement) markLoaded(event.target);
  }, true);

  function prepareDecryptionInputs() {
    document.querySelectorAll(".page-portfolio .encrypted-content__input[type='password']").forEach((input) => {
      // This is a content passphrase, not an account login; avoid mobile password-manager overlays.
      input.autocomplete = "off";
      input.name = "decryption-passphrase";
      input.inputMode = "text";
      input.enterKeyHint = "go";
    });
  }
  prepareDecryptionInputs();
  window.addEventListener("view-transition-complete", prepareDecryptionInputs);
  document.addEventListener("pointerdown", (event) => {
    const input = document.querySelector(".page-portfolio .encrypted-content__input[type='password']");
    if (!input || input.disabled) return;
    const bounds = input.getBoundingClientRect();
    if (event.clientX >= bounds.left && event.clientX <= bounds.right &&
        event.clientY >= bounds.top && event.clientY <= bounds.bottom) {
      input.focus({ preventScroll: true });
    }
  }, true);

  let dialog;
  let stage;
  let links = [];
  let current = 0;
  let requestId = 0;
  let opener;
  let touchStart;
  let position;
  let currentNumber;
  let totalNumber;
  let progress;
  let progressFill;

  const icons = {
    close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5 19 19M19 5 5 19"/></svg>',
    previous: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>',
    next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>',
  };

  async function show(index, direction = 1) {
    if (!links.length) return;
    current = (index + links.length) % links.length;
    updatePosition();
    const thisRequest = ++requestId;
    const link = links[current];
    const image = document.createElement("img");
    image.alt = link.querySelector("img")?.alt || "";
    image.className = `portfolio-lightbox-image ${direction < 0 ? "from-left" : "from-right"}`;
    image.src = link.href;

    try {
      await image.decode();
    } catch {
      if (thisRequest === requestId) window.location.href = link.href;
      return;
    }
    if (thisRequest !== requestId || !dialog.open) return;

    const previous = stage.querySelector(".is-visible");
    stage.querySelectorAll(".is-exiting").forEach((old) => old.remove());
    stage.append(image);
    image.getBoundingClientRect();
    requestAnimationFrame(() => {
      image.classList.add("is-visible");
      if (!previous) return;
      previous.classList.remove("is-visible");
      previous.classList.add("is-exiting", direction < 0 ? "to-right" : "to-left");
      previous.addEventListener("transitionend", () => previous.remove(), { once: true });
      setTimeout(() => previous.remove(), 450);
    });
  }

  function updatePosition() {
    if (!position || !progress || !progressFill) return;
    const number = current + 1;
    currentNumber.textContent = String(number).padStart(2, "0");
    totalNumber.textContent = String(links.length).padStart(2, "0");
    progress.setAttribute("aria-valuenow", String(number));
    progress.setAttribute("aria-valuemax", String(links.length));
    progress.setAttribute("aria-valuetext", `Image ${number} of ${links.length}`);
    progressFill.style.width = `${(number / links.length) * 100}%`;
  }

  function makeDialog() {
    if (dialog) return;
    dialog = document.createElement("dialog");
    dialog.className = "portfolio-lightbox";
    dialog.setAttribute("aria-label", "Portfolio image viewer");
    dialog.innerHTML = `
      <button class="portfolio-lightbox-close" type="button" aria-label="Close image">${icons.close}</button>
      <button class="portfolio-lightbox-previous" type="button" aria-label="Previous image">${icons.previous}</button>
      <div class="portfolio-lightbox-stage"></div>
      <button class="portfolio-lightbox-next" type="button" aria-label="Next image">${icons.next}</button>
      <div class="portfolio-lightbox-position" aria-label="Gallery position">
        <span class="portfolio-lightbox-count" role="status" aria-live="polite" aria-atomic="true">
          <span class="portfolio-lightbox-current"></span>
          <span class="portfolio-lightbox-divider" aria-hidden="true">/</span>
          <span class="portfolio-lightbox-total"></span>
        </span>
        <div class="portfolio-lightbox-progress" role="progressbar" aria-label="Portfolio images">
          <span class="portfolio-lightbox-progress-fill"></span>
        </div>
      </div>`;
    document.body.append(dialog);
    stage = dialog.querySelector(".portfolio-lightbox-stage");
    position = dialog.querySelector(".portfolio-lightbox-count");
    currentNumber = dialog.querySelector(".portfolio-lightbox-current");
    totalNumber = dialog.querySelector(".portfolio-lightbox-total");
    progress = dialog.querySelector(".portfolio-lightbox-progress");
    progressFill = dialog.querySelector(".portfolio-lightbox-progress-fill");
    dialog.querySelector(".portfolio-lightbox-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".portfolio-lightbox-previous").addEventListener("click", () => show(current - 1, -1));
    dialog.querySelector(".portfolio-lightbox-next").addEventListener("click", () => show(current + 1, 1));
    dialog.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        show(current - 1, -1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        show(current + 1, 1);
      }
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
    stage.addEventListener("touchstart", (event) => {
      const touch = event.changedTouches[0];
      touchStart = touch && { x: touch.screenX, y: touch.screenY };
    }, { passive: true });
    stage.addEventListener("touchend", (event) => {
      if (!touchStart) return;
      const touch = event.changedTouches[0];
      const dx = touch.screenX - touchStart.x;
      const dy = touch.screenY - touchStart.y;
      touchStart = undefined;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        show(current + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
      }
    }, { passive: true });
    dialog.addEventListener("close", () => {
      requestId++;
      stage.replaceChildren();
      opener?.focus();
    });
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest?.(".portfolio [data-portfolio-photo]");
    if (!link || !window.HTMLDialogElement || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    links = [...document.querySelectorAll(".portfolio [data-portfolio-photo]")];
    opener = link;
    makeDialog();
    dialog.showModal();
    show(links.indexOf(link));
    dialog.querySelector(".portfolio-lightbox-close").focus();
  });
})();
