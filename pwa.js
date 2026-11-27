(() => {
  if (!("serviceWorker" in navigator)) return;
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js", { scope: "./" })
      .then(reg => console.info("[MILCHO HUB] PWA service worker ready", reg.scope))
      .catch(err => console.warn("[MILCHO HUB] PWA registration failed", err));
  });
})();
