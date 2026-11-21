/**
 * EHF Level 1 registration store for the January 16-17, 2027 course.
 * Deploy as a web app: Execute as Me, Who has access: Anyone.
 * The public response lists first names and dishes only.
 */
var NOTIFY = "quanyin144@gmail.com";
var CAPACITY = 12;
var LEVELS = ["1st ($444 + HST)", "2nd ($222 + HST)", "3rd ($111 + HST)", "4th ($55 + HST)", "5th+ (by donation)"];
var OVERNIGHT = ["None", "Fri", "Sat", "Both"];
var CATEGORIES = ["Main", "Salad", "Side", "Dessert", "Drinks"];
var HEADERS = ["Timestamp", "Name", "Email", "Phone", "Level time", "Overnight", "Potluck category", "Potluck dish"];

function setup() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty("SHEET_ID");
  var ss = id ? SpreadsheetApp.openById(id) : SpreadsheetApp.create("EHF Level 1 January 2027 registrations");
  if (!id) props.setProperty("SHEET_ID", ss.getId());
  var sheet = ss.getSheetByName("Registrations") || ss.getSheets()[0];
  sheet.setName("Registrations");
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  Logger.log(ss.getUrl());
  return ss.getUrl();
}

function doGet(e) {
  return respond_(e || { parameter: {} }, handle_(e && e.parameter ? e.parameter : {}));
}

function doPost(e) {
  return doGet(e);
}

function handle_(params) {
  var action = clean_(params.action, 20) || "list";
  if (clean_(params.company, 80)) return { ok: false, error: "Could not register." };
  if (action === "register") return register_(params);
  if (action === "list") return list_();
  return { ok: false, error: "Unknown action." };
}

function register_(params) {
  var name = clean_(params.name, 60);
  var email = clean_(params.email, 80).toLowerCase();
  var phone = clean_(params.phone, 32);
  var level = clean_(params.level, 40);
  var overnight = clean_(params.overnight, 12);
  var category = clean_(params.category, 20);
  var dish = clean_(params.dish, 80);
  var phoneDigits = phone.replace(/\D/g, "");

  if (!name) return fail_("Enter your full name.");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return fail_("Enter your email.");
  if (phoneDigits.length < 7 || phoneDigits.length > 15) return fail_("Enter a phone number.");
  if (indexOf_(LEVELS, level) === -1) return fail_("Choose which time you are taking Level 1.");
  if (indexOf_(OVERNIGHT, overnight) === -1) return fail_("Choose none, Fri, Sat, or both for the overnight stay.");
  if (indexOf_(CATEGORIES, category) === -1) return fail_("Choose a potluck category.");
  if (dish.length < 2) return fail_("Name the dish you are bringing.");

  var lock = LockService.getScriptLock();
  if (!lock.tryLock(15000)) return fail_("Please try again in a moment.");
  try {
    var sheet = sheet_();
    var rows = dataRows_(sheet);
    if (hasEmail_(rows, email)) return withList_(sheet, { ok: false, error: "This email is already registered." });
    if (rows.length >= CAPACITY) return withList_(sheet, { ok: false, error: "This class is full." });

    sheet.appendRow([new Date(), name, email, phone, level, overnight, category, dish]);
    try {
      MailApp.sendEmail(NOTIFY, "Register EHF Level 1 January 16-17 2027", notice_(name, email, phone, level, overnight, category, dish));
    } catch (mailErr) {
      if (sheet.getLastRow() > 1) sheet.deleteRow(sheet.getLastRow());
      return { ok: false, error: "Could not send the registration notice. Use the email option." };
    }
    return withList_(sheet, { ok: true });
  } catch (err) {
    return { ok: false, error: "Registration storage is not ready yet. Use the email option." };
  } finally {
    lock.releaseLock();
  }
}

function list_() {
  try {
    return withList_(sheet_(), { ok: true });
  } catch (err) {
    return { ok: false, error: "The dish list is not available yet." };
  }
}

function withList_(sheet, result) {
  var rows = dataRows_(sheet);
  var order = { Main: 1, Salad: 2, Side: 3, Dessert: 4, Drinks: 5 };
  var dishes = rows.map(function (row) {
    return { name: firstName_(row[1]), category: String(row[6] || ""), dish: String(row[7] || "") };
  }).filter(function (item) {
    return item.dish;
  });
  dishes.sort(function (a, b) {
    var byCategory = (order[a.category] || 9) - (order[b.category] || 9);
    if (byCategory) return byCategory;
    return a.dish < b.dish ? -1 : a.dish > b.dish ? 1 : 0;
  });
  result.capacity = CAPACITY;
  result.spotsTaken = rows.length;
  result.spotsRemaining = Math.max(0, CAPACITY - rows.length);
  result.dishes = dishes;
  return result;
}

function notice_(name, email, phone, level, overnight, category, dish) {
  return [
    "EHF Level 1 Certification Course",
    "When: Saturday, January 16 and Sunday, January 17, 2027. 9 AM-4 PM both days.",
    "Where: The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
    "Name: " + name,
    "Email: " + email,
    "Phone: " + phone,
    "Which time: " + level,
    "Overnight: " + overnight,
    "Potluck: " + category + " - " + dish,
    "Set prices are in CAD, plus HST. A 50% deposit holds the spot.",
    "Overnight is $100 per night, breakfast included."
  ].join("\n");
}

function fail_(message) {
  return { ok: false, error: message };
}

function sheet_() {
  var id = PropertiesService.getScriptProperties().getProperty("SHEET_ID");
  if (!id) throw new Error("Run setup first.");
  var sheet = SpreadsheetApp.openById(id).getSheetByName("Registrations");
  if (!sheet) throw new Error("Missing Registrations sheet.");
  return sheet;
}

function dataRows_(sheet) {
  var last = sheet.getLastRow();
  if (last < 2) return [];
  return sheet.getRange(2, 1, last - 1, 8).getValues().filter(function (row) {
    return String(row[2] || "").trim();
  });
}

function hasEmail_(rows, email) {
  var wanted = email.toLowerCase();
  for (var i = 0; i < rows.length; i++) {
    if (String(rows[i][2] || "").trim().toLowerCase() === wanted) return true;
  }
  return false;
}

function firstName_(full) {
  var part = String(full || "").trim().split(/\s+/)[0] || "Guest";
  part = part.replace(/[^A-Za-zÀ-ÿ'’-]/g, "");
  if (!part) part = "Guest";
  return part.slice(0, 20);
}

function clean_(value, max) {
  var text = String(value == null ? "" : value).replace(/[\r\n\t]+/g, " ").replace(/\s+/g, " ").replace(/[<>]/g, "").trim();
  if (max && text.length > max) text = text.slice(0, max).trim();
  return text;
}

function indexOf_(list, value) {
  for (var i = 0; i < list.length; i++) if (list[i] === value) return i;
  return -1;
}

function respond_(e, result) {
  var callback = clean_(e.parameter && e.parameter.callback, 40);
  var json = JSON.stringify(result);
  if (/^[A-Za-z_$][\w$]{0,40}$/.test(callback)) {
    return ContentService.createTextOutput(callback + "(" + json + ");").setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}
