(function (root) {
  "use strict";

  var CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/ehf-level-1/";
  var TO = "carl.e.nissen@gmail.com";
  var SUBJECT = "Register EHF Level 1 January 2027";
  var ATTENDANCE = [
    "First time ($444)",
    "2nd ($222, 50% off)",
    "3rd ($111)",
    "4th ($55)",
    "5th+ (by donation)"
  ];
  var OVERNIGHT = ["No", "1 night", "2 nights"];

  function clean(value, max) {
    var text = String(value == null ? "" : value).replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim();
    if (max && text.length > max) text = text.slice(0, max).trim();
    return text;
  }

  function digits(value) {
    return clean(value, 32).replace(/\D/g, "");
  }

  function buildRegistration(input) {
    var name = clean(input.name, 60);
    var email = clean(input.email, 80);
    var phone = clean(input.phone, 32);
    var city = clean(input.city, 48);
    var attendance = clean(input.attendance, 40);
    var overnight = clean(input.overnight, 12);
    var questions = clean(input.questions, 200);

    if (!name) return { error: "Enter your full name." };
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { error: "Enter your email." };
    var phoneDigits = digits(phone);
    if (phoneDigits.length < 7 || phoneDigits.length > 15) return { error: "Enter a phone number." };
    if (city.length < 2) return { error: "Enter your town or city." };
    if (ATTENDANCE.indexOf(attendance) === -1) {
      return { error: "Choose first time, 2nd, 3rd, 4th, or 5th+." };
    }
    if (OVERNIGHT.indexOf(overnight) === -1) {
      return { error: "Choose No, 1 night, or 2 nights for the overnight stay." };
    }

    var lines = [
      "Course: EHF Level 1 Certification Course",
      "When: January 2027, date to be confirmed",
      "Where: The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
      "Name: " + name,
      "Email: " + email,
      "Phone: " + phone,
      "Town/city: " + city,
      "Attendance: " + attendance,
      "Overnight stay: " + overnight,
      "Questions: " + (questions || "None"),
      "Payment: Online payment is being set up. We'll confirm your spot and send payment details after you register.",
      "Sending this email registers you. Preparing it does not."
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

  root.EhfLevel1 = {
    CANONICAL: CANONICAL,
    TO: TO,
    SUBJECT: SUBJECT,
    ATTENDANCE: ATTENDANCE,
    OVERNIGHT: OVERNIGHT,
    buildRegistration: buildRegistration
  };

  if (typeof document !== "undefined" && document.getElementById) {
    var form = document.getElementById("reg");
    if (form) wire(form);
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
