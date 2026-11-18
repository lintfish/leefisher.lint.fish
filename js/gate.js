/* Preview password gate. A light deterrent only, not real security. */
(function () {
  var SALT = "91921c2f276d95bc5281536f784fd521";
  var HASH = "7cf4bf706cbb59c5979ba127d4f2d667e8d775475f161121b72f6992ed53fc16";
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
