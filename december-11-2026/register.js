(function (root) {
  "use strict";

  var CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/december-11-2026/";
  var TO = "carl.e.nissen@gmail.com";
  var SUBJECT = "RSVP House Party Dec 11 2026";
  var DISHES = ["Chicken", "Beef", "Lamb", "Soups", "Vegetables"];

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

    if (!name) return { error: "Enter your name." };
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { error: "Enter your email." };
    if (!/^[1-9]\d{0,2}$/.test(guests)) {
      return { error: "Enter a whole number of guests, including you." };
    }
    if (DISHES.indexOf(dish) === -1) return { error: "Choose what you\u2019ll bring." };

    var lines = [
      "Event: House party",
      "Free head count.",
      "When: Friday, December 11, 2026. Time to be confirmed.",
      "Where: Same address as the December 12 AI event. Location details to be confirmed.",
      "The night before the December 12 AI Ninjas Mastermind.",
      "Live DJ.",
      "Potluck: " + dish,
      "Ovens, stove, and smoker available on site.",
      "Sound magic in the cabin. Sauna. Pond cold plunge. Fire pit.",
      "Name: " + name,
      "Email: " + email,
      "Guests, including you: " + guests,
      "Sending this email counts you. Preparing it does not."
    ];
    var body = lines.join("\n");
    var href = "mailto:" + TO + "?subject=" + encodeURIComponent(SUBJECT) + "&body=" + encodeURIComponent(body);
    return {
      to: TO,
      subject: SUBJECT,
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
    DISHES: DISHES,
    buildRegistration: buildRegistration
  };

  if (typeof document !== "undefined" && document.getElementById) {
    var form = document.getElementById("reg");
    if (form) wire(form);
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
