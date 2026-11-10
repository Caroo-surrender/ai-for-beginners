(function (root) {
  "use strict";

  var CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/december-4-2026/";
  var TO = "carl.e.nissen@gmail.com";
  var SUBJECT = "RSVP House Party Dec 4 2026";
  var SUBJECT_BOTH = "RSVP House Party Dec 4 + AI Ninjas Mastermind Dec 5 2026";
  var DISHES = ["Chicken", "Beef", "Lamb", "Soups", "Vegetables"];
  var SLEEP = ["Yes, sleeping over", "No, going home", "Not sure yet"];
  var MASTERMIND = ["Yes", "No", "Maybe"];
  var SANDWICHES = ["None", "Chicken Parm", "Mortadella", "Vegetarian/Vegan"];

  function clean(value, max) {
    var text = String(value == null ? "" : value).replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim();
    if (max && text.length > max) text = text.slice(0, max).trim();
    return text;
  }

  function buildRegistration(input) {
    var name = clean(input.name, 48);
    var email = clean(input.email, 48);
    var guests = clean(input.guests, 3);
    var dish = clean(input.dish, 12);
    var sleep = clean(input.sleep, 24);
    var staying = clean(input.staying, 3);
    var mastermind = clean(input.mastermind, 8);
    var sandwich = clean(input.sandwich, 20);

    if (!name) return { error: "Enter your name." };
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { error: "Enter your email." };
    if (!/^[1-9]\d{0,2}$/.test(guests)) {
      return { error: "Enter a whole number of guests, including you." };
    }
    if (DISHES.indexOf(dish) === -1) return { error: "Choose what you\u2019ll bring." };
    if (SLEEP.indexOf(sleep) === -1) return { error: "Say whether you are sleeping over." };
    if (sleep === "Yes, sleeping over" && staying && !/^[1-9]\d{0,2}$/.test(staying)) {
      return { error: "Enter a whole number of people staying, or leave that blank." };
    }
    if (MASTERMIND.indexOf(mastermind) === -1) {
      return { error: "Say whether you are staying for the AI Ninjas Mastermind." };
    }
    if (sandwich && SANDWICHES.indexOf(sandwich) === -1) {
      return { error: "Choose a sandwich, or leave that blank." };
    }

    var subject = mastermind === "Yes" ? SUBJECT_BOTH : SUBJECT;
    var stayingLine = sleep === "Yes, sleeping over"
      ? (staying || "Not specified")
      : "Not staying";
    var lines = [
      "Event: House party",
      "Free head count.",
      "When: Friday, December 4, 2026. From 2 PM. Show up anytime after.",
      "Where: 15606 The Gore Rd, Caledon East, ON L7C 3E5.",
      "The next day: AI Ninjas Mastermind, Saturday, December 5, 2026, 10 AM\u20134 PM, $20.",
      "Live DJ.",
      "Potluck: " + dish,
      "Ovens, stove, and smoker available on site.",
      "Sound magic in the cabin. Cold plunge in the pond.",
      "Sleepover spots are limited.",
      "Sleeping over: " + sleep,
      "People in your group staying: " + stayingLine,
      "Staying for the AI Ninjas Mastermind on Sat Dec 5 (10 AM-4 PM, $20): " + mastermind,
      "Sandwich: " + (sandwich || "None"),
      sandwich && sandwich !== "None" ? "Lunch payment: e-transfer $30 to quanyin144@gmail.com by Wednesday Dec 2, with " + sandwich + " in the note." : "",
      "Name: " + name,
      "Email: " + email,
      "Guests, including you: " + guests,
      "Sending this email counts you. Preparing it does not."
    ].filter(function (line) { return line; });
    var body = lines.join("\n");
    var href = "mailto:" + TO + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    return {
      to: TO,
      subject: subject,
      body: body,
      href: href,
      canonical: CANONICAL
    };
  }

  function showError(message) {
    var slot = document.getElementById("form-error");
    slot.hidden = false;
    slot.textContent = message;
  }

  function wire(form) {
    var confirmPanel = document.getElementById("confirm");
    var mailOpen = document.getElementById("mail-open");
    var copyButton = document.getElementById("copy-mail");
    var editButton = document.getElementById("edit-reg");
    var copyStatus = document.getElementById("copy-status");
    var stayingWrap = document.getElementById("staying-wrap");

    function syncStay() {
      var chosen = form.querySelector("input[name=sleep]:checked");
      var yes = chosen && chosen.value === "Yes, sleeping over";
      if (stayingWrap) stayingWrap.hidden = !yes;
    }

    form.addEventListener("change", syncStay);
    syncStay();

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var built = buildRegistration(Object.fromEntries(new FormData(form).entries()));
      if (built.error) {
        showError(built.error);
        return;
      }
      document.getElementById("form-error").hidden = true;
      document.getElementById("confirm-to").textContent = built.to;
      document.getElementById("confirm-subject").textContent = built.subject;
      document.getElementById("confirm-body").textContent = built.body;
      mailOpen.href = built.href;
      form.hidden = true;
      confirmPanel.hidden = false;
      document.getElementById("confirm-title").focus();
    });

    copyButton.addEventListener("click", function () {
      var text = "To: " + document.getElementById("confirm-to").textContent +
        "\nSubject: " + document.getElementById("confirm-subject").textContent +
        "\n\n" + document.getElementById("confirm-body").textContent;
      function done(message) {
        copyStatus.textContent = message;
      }
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
      confirmPanel.hidden = true;
      form.hidden = false;
      var name = form.querySelector("[name=name]");
      if (name) name.focus();
    });
  }

  root.HouseParty = {
    CANONICAL: CANONICAL,
    TO: TO,
    SUBJECT: SUBJECT,
    SUBJECT_BOTH: SUBJECT_BOTH,
    DISHES: DISHES,
    SLEEP: SLEEP,
    MASTERMIND: MASTERMIND,
    buildRegistration: buildRegistration
  };

  if (typeof document !== "undefined" && document.getElementById) {
    var form = document.getElementById("reg");
    if (form) wire(form);
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
