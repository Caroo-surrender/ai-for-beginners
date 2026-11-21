(function (root) {
  "use strict";

  var CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/ehf-level-1/";
  var TO = "quanyin144@gmail.com";
  var SUBJECT = "Register EHF Level 1 January 16-17 2027";
  var LEVELS = [
    "1st ($444 + HST)",
    "2nd ($222 + HST)",
    "3rd ($111 + HST)",
    "4th ($55 + HST)",
    "5th+ (by donation)"
  ];
  var OVERNIGHT = ["None", "Fri", "Sat", "Both"];
  var CATEGORIES = ["Main", "Salad", "Side", "Dessert", "Drinks"];
  var OVERNIGHT_NOTE = {
    "None": "None",
    "Fri": "Fri ($100, breakfast included)",
    "Sat": "Sat ($100, breakfast included)",
    "Both": "Both ($200, breakfast included)"
  };

  function clean(value, max) {
    var text = String(value == null ? "" : value).replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim();
    if (max && text.length > max) text = text.slice(0, max).trim();
    return text;
  }

  function digits(value) {
    return clean(value, 32).replace(/\D/g, "");
  }

  function endpoint() {
    return clean(root.EHF_ENDPOINT, 300);
  }

  function firstToken(value) {
    var part = clean(value, 40).split(" ")[0] || "";
    return part.replace(/[^A-Za-zÀ-ÿ'’-]/g, "").slice(0, 20);
  }

  function buildRegistration(input) {
    var name = clean(input.name, 60);
    var email = clean(input.email, 80);
    var phone = clean(input.phone, 32);
    var level = clean(input.level, 40);
    var overnight = clean(input.overnight, 12);
    var category = clean(input.category, 20);
    var dish = clean(input.dish, 80);
    var company = clean(input.company, 80);

    if (company) return { error: "Leave the extra field blank." };
    if (!name) return { error: "Enter your full name." };
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { error: "Enter your email." };
    if (digits(phone).length < 7 || digits(phone).length > 15) return { error: "Enter a phone number." };
    if (LEVELS.indexOf(level) === -1) return { error: "Choose which time you are taking Level 1." };
    if (OVERNIGHT.indexOf(overnight) === -1) return { error: "Choose none, Fri, Sat, or both for the overnight stay." };
    if (CATEGORIES.indexOf(category) === -1) return { error: "Choose a potluck category." };
    if (dish.length < 2) return { error: "Name the dish you are bringing." };

    var lines = [
      "Course: EHF Level 1 Certification Course",
      "Facilitator: Caroo",
      "When: Saturday, January 16 and Sunday, January 17, 2027. 9 AM-4 PM both days.",
      "Where: The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
      "Name: " + name,
      "Email: " + email,
      "Phone: " + phone,
      "Which time: " + level,
      "Overnight: " + OVERNIGHT_NOTE[overnight],
      "Potluck: " + category + " - " + dish,
      "Limited to 12 spaces. A 50% deposit holds your spot.",
      "Set prices are in CAD, plus HST.",
      "Sending this email registers you. Preparing it does not."
    ];
    var body = lines.join("\n");
    return {
      to: TO,
      subject: SUBJECT,
      body: body,
      href: "mailto:" + TO + "?subject=" + encodeURIComponent(SUBJECT) + "&body=" + encodeURIComponent(body),
      canonical: CANONICAL,
      fields: { name: name, email: email, phone: phone, level: level, overnight: overnight, category: category, dish: dish }
    };
  }

  function showError(message) {
    var slot = document.getElementById("form-error");
    slot.hidden = !message;
    slot.textContent = message || "";
  }

  function jsonp(params) {
    return new Promise(function (resolve, reject) {
      var cb = "ehf_" + Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36);
      var script = document.createElement("script");
      var timer = setTimeout(function () {
        cleanup();
        reject(new Error("The registration service did not respond."));
      }, 15000);
      function cleanup() {
        clearTimeout(timer);
        try { delete root[cb]; } catch (err) { root[cb] = undefined; }
        if (script.parentNode) script.parentNode.removeChild(script);
      }
      root[cb] = function (data) {
        cleanup();
        resolve(data || {});
      };
      var query = Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + "=" + encodeURIComponent(params[key] == null ? "" : params[key]);
      }).join("&");
      var base = endpoint();
      script.src = base + (base.indexOf("?") === -1 ? "?" : "&") + query + "&callback=" + cb;
      script.onerror = function () {
        cleanup();
        reject(new Error("The registration service did not respond."));
      };
      document.head.appendChild(script);
    });
  }

  function renderLive(data) {
    var list = document.getElementById("potluck-list");
    var status = document.getElementById("potluck-status");
    var spots = document.getElementById("spots");
    if (!list || !data) return;
    var dishes = Array.isArray(data.dishes) ? data.dishes : [];
    list.textContent = "";
    if (!dishes.length) {
      list.hidden = true;
      status.hidden = false;
      status.textContent = data.ok === false && data.error && typeof data.spotsRemaining !== "number"
        ? "The shared dish list appears here once registration is connected."
        : "No dishes yet. Yours can be the first.";
    } else {
      status.hidden = true;
      list.hidden = false;
      dishes.forEach(function (item) {
        var li = document.createElement("li");
        var cat = document.createElement("span");
        var rest = document.createElement("span");
        var who = firstToken(item && item.name);
        cat.className = "dish-cat";
        cat.textContent = clean(item && item.category, 20);
        rest.textContent = (who ? who + " · " : "") + clean(item && item.dish, 80);
        li.appendChild(cat);
        li.appendChild(rest);
        list.appendChild(li);
      });
    }
    if (spots && typeof data.spotsRemaining === "number") {
      var capacity = data.capacity || 12;
      spots.textContent = data.spotsRemaining + " of " + capacity + " spots remaining.";
    }
  }

  function useLiveCopy(on) {
    var live = document.getElementById("register-live");
    var mail = document.getElementById("register-mail");
    var button = document.getElementById("submit-reg");
    if (live) live.hidden = !on;
    if (mail) mail.hidden = on;
    if (button) button.textContent = on ? "Register" : "Prepare my registration email";
  }

  function showMailto(built) {
    document.getElementById("confirm-live").hidden = true;
    document.getElementById("confirm-mail").hidden = false;
    document.getElementById("confirm-title").textContent = "Send this email to register";
    document.getElementById("confirm-to").textContent = built.to;
    document.getElementById("confirm-subject").textContent = built.subject;
    document.getElementById("confirm-body").textContent = built.body;
    document.getElementById("mail-open").href = built.href;
    document.getElementById("reg").hidden = true;
    document.getElementById("confirm").hidden = false;
    document.getElementById("confirm-title").focus();
  }

  function showSaved(data) {
    document.getElementById("confirm-mail").hidden = true;
    document.getElementById("confirm-live").hidden = false;
    document.getElementById("confirm-title").textContent = "You're registered";
    var remaining = typeof data.spotsRemaining === "number" ? data.spotsRemaining + " of " + (data.capacity || 12) + " spots remaining." : "";
    document.getElementById("confirm-live-text").textContent = "Your registration is saved and a notice was sent to " + TO + ". " + remaining;
    document.getElementById("reg").hidden = true;
    document.getElementById("confirm").hidden = false;
    document.getElementById("confirm-title").focus();
  }

  function wire(form) {
    var copyButton = document.getElementById("copy-mail");
    var editButton = document.getElementById("edit-reg");
    var copyStatus = document.getElementById("copy-status");
    var connected = false;

    function refresh() {
      if (!endpoint()) return Promise.resolve();
      return jsonp({ action: "list" }).then(function (data) {
        if (!data || data.ok === false && typeof data.spotsRemaining !== "number") throw new Error(data && data.error);
        connected = true;
        useLiveCopy(true);
        renderLive(data);
      }).catch(function () {
        connected = false;
        useLiveCopy(false);
      });
    }

    refresh();

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var input = Object.fromEntries(new FormData(form).entries());
      var built = buildRegistration(input);
      if (built.error) {
        showError(built.error);
        return;
      }
      showError("");
      if (!endpoint()) {
        showMailto(built);
        return;
      }
      var button = document.getElementById("submit-reg");
      button.disabled = true;
      jsonp({
        action: "register",
        name: built.fields.name,
        email: built.fields.email,
        phone: built.fields.phone,
        level: built.fields.level,
        overnight: built.fields.overnight,
        category: built.fields.category,
        dish: built.fields.dish
      }).then(function (data) {
        button.disabled = false;
        if (!data || data.ok === false) {
          if (data && typeof data.spotsRemaining === "number") renderLive(data);
          showError((data && data.error) || "Could not register. You can still send the email.");
          return;
        }
        connected = true;
        useLiveCopy(true);
        renderLive(data);
        showSaved(data);
      }).catch(function () {
        button.disabled = false;
        showMailto(built);
        document.getElementById("form-error").hidden = true;
        var note = document.getElementById("confirm-fallback");
        if (note) note.hidden = false;
      });
    });

    copyButton.addEventListener("click", function () {
      var text = "To: " + document.getElementById("confirm-to").textContent +
        "\nSubject: " + document.getElementById("confirm-subject").textContent +
        "\n\n" + document.getElementById("confirm-body").textContent;
      function done(message) { copyStatus.textContent = message; }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          done("Copied. Paste it into an email to " + TO + " and press Send.");
        }, function () {
          done("Copy was blocked. Select the message above and copy it yourself.");
        });
      } else {
        done("Select the message above and copy it into an email.");
      }
    });

    editButton.addEventListener("click", function () {
      document.getElementById("confirm").hidden = true;
      form.hidden = false;
      var name = form.querySelector("[name=name]");
      if (name) name.focus();
    });
  }

  root.EhfLevel1 = {
    CANONICAL: CANONICAL,
    TO: TO,
    SUBJECT: SUBJECT,
    LEVELS: LEVELS,
    OVERNIGHT: OVERNIGHT,
    CATEGORIES: CATEGORIES,
    endpoint: endpoint,
    buildRegistration: buildRegistration
  };

  if (typeof document !== "undefined" && document.getElementById) {
    var form = document.getElementById("reg");
    if (form) wire(form);
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
