/* Applies SITE_CONFIG (name and phone) and handles the mobile nav. */
(function () {
  "use strict";

  var config = window.SITE_CONFIG || {};
  var name = config.businessName || "Fisher Advanced";
  var phoneDisplay = config.phoneDisplay || "07XXX XXXXXX";
  var phoneTel = config.phoneTel || String(phoneDisplay).replace(/\s+/g, "");

  document.querySelectorAll("[data-business-name]").forEach(function (el) {
    el.textContent = name;
  });

  document.querySelectorAll("[data-phone-display]").forEach(function (el) {
    el.textContent = phoneDisplay;
  });

  document.querySelectorAll("[data-tel-link]").forEach(function (el) {
    el.setAttribute("href", "tel:" + phoneTel);
  });

  document.querySelectorAll("[data-sms-link]").forEach(function (el) {
    el.setAttribute("href", "sms:" + phoneTel);
  });

  var titleEl = document.querySelector("title[data-title-template]");
  if (titleEl) {
    titleEl.textContent = titleEl.getAttribute("data-title-template").replace("%NAME%", name);
  }

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    function setOpen(open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      nav.classList.toggle("is-open", open);
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setOpen(false);
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
  }
})();
