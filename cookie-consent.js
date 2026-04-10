(function () {
  var consentKey = "twitchdl_cookie_consent";
  var adsScriptSrc =
    "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7612805768657333";

  function readConsent() {
    try {
      return window.localStorage.getItem(consentKey);
    } catch (error) {
      return null;
    }
  }

  function writeConsent(value) {
    try {
      window.localStorage.setItem(consentKey, value);
    } catch (error) {
      return;
    }
  }

  function loadAdsense() {
    if (document.querySelector('script[data-cookie-consent="adsense"]')) {
      return;
    }

    var script = document.createElement("script");
    script.async = true;
    script.crossOrigin = "anonymous";
    script.src = adsScriptSrc;
    script.dataset.cookieConsent = "adsense";
    document.head.appendChild(script);
  }

  function setupBanner() {
    var banner = document.getElementById("cookie-banner");
    var acceptButton = document.getElementById("cookie-accept");
    var rejectButton = document.getElementById("cookie-reject");
    var consent = readConsent();

    if (!banner || !acceptButton || !rejectButton) {
      if (consent === "accepted") {
        loadAdsense();
      }
      return;
    }

    if (consent === "accepted") {
      banner.hidden = true;
      loadAdsense();
      return;
    }

    if (consent === "rejected") {
      banner.hidden = true;
      return;
    }

    banner.hidden = false;

    acceptButton.addEventListener("click", function () {
      writeConsent("accepted");
      banner.hidden = true;
      loadAdsense();
    });

    rejectButton.addEventListener("click", function () {
      writeConsent("rejected");
      banner.hidden = true;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupBanner, { once: true });
  } else {
    setupBanner();
  }
})();