/* Preview password gate. A light deterrent only, not real security. */
(function () {
  var SALT = "f36238d30e96e7ba80af93c5f714ad2e";
  var HASH = "57106b327da99fa0e4c57e5e292c51e85e0aeec38c919047b1119ffd0c87b333";
  var KEY = "lf-preview-ok";
  var root = document.documentElement;
  try { if (localStorage.getItem(KEY) === HASH) return; } catch (e) {}
  root.classList.add("gate-locked");
  function hex(buf) {
    return Array.prototype.map.call(new Uint8Array(buf), function (b) {
      return ("0" + b.toString(16)).slice(-2);
    }).join("");
  }
  function build() {
    var wrap = document.createElement("div");
    wrap.className = "gate";
    wrap.innerHTML =
      '<form class="gate__box" autocomplete="off">' +
      '<p class="gate__kicker">Private preview</p>' +
      '<h1 class="gate__title">Enter password</h1>' +
      '<label class="gate__label" for="gate-pw">Password</label>' +
      '<input id="gate-pw" class="gate__input" type="password" required autofocus>' +
      '<button class="gate__btn" type="submit">View site</button>' +
      '<p class="gate__err" role="alert" hidden>That password isn\u2019t right.</p>' +
      "</form>";
    document.body.appendChild(wrap);
    var form = wrap.querySelector("form");
    var input = wrap.querySelector("input");
    var err = wrap.querySelector(".gate__err");
    input.focus();
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var data = new TextEncoder().encode(SALT + ":" + input.value);
      crypto.subtle.digest("SHA-256", data).then(function (buf) {
        if (hex(buf) === HASH) {
          try { localStorage.setItem(KEY, HASH); } catch (e) {}
          wrap.remove();
          root.classList.remove("gate-locked");
        } else {
          err.hidden = false;
          input.value = "";
          input.focus();
        }
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
