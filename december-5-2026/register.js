(function (root) {
  "use strict";

  var CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/december-5-2026/";
  var TO = "carl.e.nissen@gmail.com";
  var SUBJECT = "RSVP AI Ninjas Mastermind Dec 5 2026";
  var PRICE = "$20 per person";
  var ACCESS = "Cost a barrier? Reach out to Caroo\u2014we can arrange another way to contribute, such as cleanup.";
  var FOOD = "Winter soup and a fruit dish. You\u2019re welcome to bring a potluck dish.";
  var BOTTLENECK = "Bring your biggest bottleneck. We\u2019ll work through it together with practical solutions and tools for your next step that day.";
  var PAY = "Payment details by email after registration.";

  function clean(value, max) {
    var text = String(value == null ? "" : value).replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim();
    if (max && text.length > max) text = text.slice(0, max).trim();
    return text;
  }

  function buildRegistration(input) {
    var name = clean(input.name, 36);
    var contact = clean(input.contact, 48);
    var party = clean(input.party, 3);
    var food = clean(input.food, 40);
    var potluck = clean(input.potluck, 20);
    var share = clean(input.share, 36);
    var bottleneck = clean(input.bottleneck, 48);
    var notes = clean(input.notes, 20);

    if (!name) return { error: "Enter your name." };
    if (!contact) return { error: "Enter an email or phone number." };
    if (party && !/^[1-9]\d{0,2}$/.test(party)) {
      return { error: "Enter a whole number of people, or leave that field blank." };
    }

    var lines = [
      "Event: AI Ninjas Mastermind",
      "When: Saturday, December 5, 2026, 11 AM \u2013 4 PM Toronto time",
      "Where: Location details to be confirmed",
      "Admission: " + PRICE,
      PAY,
      ACCESS,
      FOOD,
      "Potluck (optional, not a commitment): " + (food || "Not specified"),
      "Dish (optional): " + (potluck || "None named"),
      "Bring a five-minute show-and-share.",
      "Topic (optional): " + (share || "Not shared"),
      BOTTLENECK,
      "Bottleneck (optional): " + (bottleneck || "Not shared"),
      "Name: " + name,
      "Email or phone: " + contact,
      "People (optional): " + (party || "Not specified"),
      "Notes: " + (notes || ""),
      "Sending this email registers you. Preparing it does not."
    ];
    var body = lines.join("\n");
    var href = "mailto:" + TO + "?subject=" + encodeURIComponent(SUBJECT) + "&body=" + encodeURIComponent(body);
    return {
      to: TO,
      subject: SUBJECT,
      body: body,
      href: href,
      canonical: CANONICAL,
      price: PRICE
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

  root.DecemberEvent = {
    CANONICAL: CANONICAL,
    TO: TO,
    SUBJECT: SUBJECT,
    PRICE: PRICE,
    ACCESS: ACCESS,
    FOOD: FOOD,
    BOTTLENECK: BOTTLENECK,
    PAY: PAY,
    buildRegistration: buildRegistration
  };

  if (typeof document !== "undefined" && document.getElementById) {
    var form = document.getElementById("reg");
    if (form) wire(form);
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
