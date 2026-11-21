#!/usr/bin/env python3
"""Checks for the EHF Level 1 registration page."""

import json
import re
import subprocess
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "ehf-level-1"
CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/ehf-level-1/"
SUBJECT = "Register EHF Level 1 January 16-17 2027"
TO = "quanyin144@gmail.com"
NODE = "/exec-daemon/node"
OLD_SUBHEAD = "A 2-day hands-on introduction to EHF energy work"

UNTOUCHED = [
    "index.html",
    "advanced",
    "december-4-2026",
    "december-5-2026",
    "december-11-2026",
    "december-12-2026",
    "scripts",
]


def plain_html(html):
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


class EhfLevel1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (PAGE / "index.html").read_text(encoding="utf-8")
        cls.script = (PAGE / "register.js").read_text(encoding="utf-8")
        cls.page = plain_html(cls.html)

    def test_existing_pages_untouched(self):
        result = subprocess.run(
            ["git", "diff", "--exit-code", "main", "--", *UNTOUCHED],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_required_copy(self):
        for fact in (
            "Energy Healing Facilitation",
            "EHF Level 1",
            "EHF Level 1 Certification Course",
            "Caroo",
            "Saturday, January 16 and Sunday, January 17, 2027",
            "9 AM–4 PM both days",
            "The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
            "$444",
            "CAD",
            "plus HST",
            "Last time at this price",
            "1st time",
            "2nd time",
            "$222 + HST",
            "3rd time",
            "$111 + HST",
            "4th time",
            "$55 + HST",
            "5th time and beyond",
            "by donation",
            "Limited to 12 spaces.",
            "A 50% deposit holds your spot.",
            "Complete the Quan Yin Virtual Class (online) first.",
            "Potluck lunch",
            "first names only",
            "Sleeping arrangements",
            "Optional overnight stay at The Light House: $100 per night, breakfast included.",
            "quanyin144@gmail.com",
            "EHF Holistic Services Canada Inc.",
            "https://ehfpath.com",
            SUBJECT,
            "Preparing this email does not register you.",
            "You are registered only after you press Send",
        ):
            self.assertIn(fact, self.page, fact)

    def test_meta_and_images(self):
        self.assertIn("<title>EHF Level 1</title>", self.html)
        self.assertIn(f'rel="canonical" href="{CANONICAL}"', self.html)
        self.assertIn("EHF Level 1 Certification Course", self.html)
        self.assertNotIn(OLD_SUBHEAD, self.html)
        self.assertNotIn(OLD_SUBHEAD, self.script)
        desc = re.search(r'name="description" content="([^"]+)"', self.html).group(1)
        og = re.search(r'property="og:description" content="([^"]+)"', self.html).group(1)
        self.assertIn("EHF Level 1 Certification Course", desc)
        self.assertIn("EHF Level 1 Certification Course", og)
        self.assertNotIn(OLD_SUBHEAD, desc)
        self.assertNotIn(OLD_SUBHEAD, og)
        image = "https://caroo-surrender.github.io/ai-for-beginners/ehf-level-1/img/class.webp"
        self.assertIn(f'property="og:image" content="{image}"', self.html)
        self.assertIn('src="img/logo.png"', self.html)
        self.assertIn('src="img/caroo.jpg"', self.html)
        self.assertIn('src="img/class.webp"', self.html)
        self.assertIn("January 16", self.page)
        self.assertIn("January 17", self.page)
        self.assertNotIn("date to be confirmed", self.html)
        self.assertNotIn("location to be confirmed", self.html)
        self.assertNotIn("location to be confirmed", self.script)
        self.assertNotIn("Details coming soon", self.html)
        self.assertNotIn("10 spots for new students", self.html)
        self.assertNotIn("2 teachers", self.html)
        self.assertNotIn("paying spots", self.html)
        self.assertNotIn("date to be confirmed", self.script)
        config = (PAGE / "config.js").read_text(encoding="utf-8")
        self.assertIn('EHF_ENDPOINT = ""', config)
        script_gs = (PAGE / "apps-script" / "Code.gs").read_text(encoding="utf-8")
        self.assertIn(TO, script_gs)
        self.assertIn("CAPACITY = 12", script_gs)
        self.assertIn("MailApp.sendEmail", script_gs)
        self.assertIsNone(re.search(r"AI for Beginners", self.html, flags=re.I))
        self.assertIsNone(re.search(r"AI for Beginners", self.script, flags=re.I))
        self.assertIn('property="og:title" content="EHF Level 1"', self.html)
        self.assertEqual(self.page.count("(TBD)"), 0)
        self.assertIn(
            "https://www.google.com/maps/search/?api=1&amp;query=The+Light+House+15606+The+Gore+Rd+Caledon+East+ON+L7C+3E5",
            self.html,
        )

    def test_banned_words(self):
        blob = self.html + "\n" + self.script
        for pattern in (
            r"Master Lee",
            r"\bcure\w*",
            r"\btreat\w*",
            r"\bguarantee",
            r"\bSquare\b",
            r"\bstripe\b",
            r"\bpaypal\b",
            r"Carl Nissen",
            r"a quarter",
        ):
            self.assertIsNone(re.search(pattern, blob, flags=re.I), pattern)

    def test_form_fields(self):
        self.assertIn('id="reg"', self.html)
        self.assertIn('name="name" required', self.html)
        self.assertIn('name="email"', self.html)
        self.assertIn('type="email"', self.html)
        self.assertIn('name="phone"', self.html)
        self.assertIn('name="level" value="1st ($444 + HST)" required', self.html)
        self.assertIn('name="overnight" value="None" required', self.html)
        self.assertIn('name="overnight" value="Fri"', self.html)
        self.assertIn('name="overnight" value="Sat"', self.html)
        self.assertIn('name="overnight" value="Both"', self.html)
        self.assertIn('name="category" value="Main" required', self.html)
        self.assertIn('name="dish" required', self.html)
        self.assertIn("Which time taking Level 1?", self.page)
        for value in (
            "1st ($444 + HST)",
            "2nd ($222 + HST)",
            "3rd ($111 + HST)",
            "4th ($55 + HST)",
            "5th+ (by donation)",
            "Salad",
            "Side",
            "Dessert",
            "Drinks",
        ):
            self.assertIn(f'value="{value}"', self.html)
        self.assertIn('src="config.js"', self.html)

    def test_message_builder(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const context = {};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const built = context.EhfLevel1.buildRegistration({
  name: 'Sample Guest',
  email: 'guest@example.com',
  phone: '(905) 555-0100',
  level: '4th ($55 + HST)',
  overnight: 'Fri',
  category: 'Salad',
  dish: 'Green salad'
});
const packed = context.EhfLevel1.buildRegistration({
  name: 'N'.repeat(80),
  email: 'person@example.com',
  phone: '+1 416 555 0199',
  level: '5th+ (by donation)',
  overnight: 'Both',
  category: 'Main',
  dish: 'D'.repeat(200)
});
const bad = context.EhfLevel1.buildRegistration({
  name: 'Ada',
  email: 'ada@example.com',
  phone: '123',
  level: '1st ($444 + HST)',
  overnight: 'None',
  category: 'Side',
  dish: 'Rice'
});
if (built.error) process.exit(2);
const href = new URL(built.href);
const out = {
  subject: href.searchParams.get('subject'),
  to: href.pathname,
  body: href.searchParams.get('body'),
  packedLength: packed.href.length,
  bad: bad.error || ''
};
process.stdout.write(JSON.stringify(out));
"""
        result = subprocess.run(
            [NODE, "-e", script, str(PAGE / "register.js")],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["subject"], SUBJECT)
        self.assertEqual(data["to"], TO)
        for fact in (
            "EHF Level 1 Certification Course",
            "Sample Guest",
            "guest@example.com",
            "(905) 555-0100",
            "Caledon East",
            "4th ($55 + HST)",
            "Overnight: Fri ($100, breakfast included)",
            "Potluck: Salad - Green salad",
            "The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
            "January 16",
            "January 17",
            "A 50% deposit holds your spot.",
            "Sending this email registers you. Preparing it does not.",
        ):
            self.assertIn(fact, data["body"])
        self.assertNotIn(OLD_SUBHEAD, data["body"])
        self.assertLess(data["packedLength"], 1900)
        self.assertIn("phone", data["bad"].lower())

    def test_images_are_compact_and_have_no_exif(self):
        expected = {
            "logo.png": (1100, 495),
            "caroo.jpg": (720, 850),
            "class.webp": (1400, 1050),
        }
        for name, size in expected.items():
            path = PAGE / "img" / name
            self.assertTrue(path.is_file(), name)
            self.assertLess(path.stat().st_size, 180_000, name)
            with Image.open(path) as image:
                self.assertEqual(image.size, size, name)
                self.assertEqual(len(image.getexif() or []), 0, name)
                self.assertNotIn("exif", {key.lower() for key in image.info})


if __name__ == "__main__":
    unittest.main()
