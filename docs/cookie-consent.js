(function () {
  var consentKey = "twitchdl_cookie_consent";
  var adsScriptSrc =
    "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7612805768657333";

  window.dataLayer = window.dataLayer || [];
  window.gtag =
    window.gtag ||
    function () {
      window.dataLayer.push(arguments);
    };

  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    wait_for_update: 500,
  });
  gtag("set", "ads_data_redaction", true);

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

  function updateConsent(value) {
    var granted = value === "accepted";
    gtag("consent", "update", {
      ad_storage: granted ? "granted" : "denied",
      ad_user_data: granted ? "granted" : "denied",
      ad_personalization: granted ? "granted" : "denied",
      analytics_storage: "denied",
    });
    gtag("set", "ads_data_redaction", !granted);
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
    var preferencesButtons = document.querySelectorAll("[data-cookie-preferences]");
    var consent = readConsent();
    var trigger = null;

    if (consent === "accepted") {
      updateConsent(consent);
      loadAdsense();
    } else if (consent === "rejected") {
      updateConsent(consent);
    }

    if (!banner || !acceptButton || !rejectButton) {
      return;
    }

    function closeBanner() {
      banner.hidden = true;
      if (trigger && document.contains(trigger)) trigger.focus();
      trigger = null;
    }

    function choose(value) {
      var wasAccepted = readConsent() === "accepted";
      writeConsent(value);
      updateConsent(value);
      closeBanner();
      if (value === "accepted") {
        loadAdsense();
      } else if (wasAccepted) {
        window.location.reload();
      }
    }

    if (!consent) {
      banner.hidden = false;
    }

    acceptButton.addEventListener("click", function () {
      choose("accepted");
    });

    rejectButton.addEventListener("click", function () {
      choose("rejected");
    });

    Array.prototype.forEach.call(preferencesButtons, function (button) {
      button.addEventListener("click", function () {
        trigger = button;
        banner.hidden = false;
        acceptButton.focus();
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupBanner, { once: true });
  } else {
    setupBanner();
  }
})();
