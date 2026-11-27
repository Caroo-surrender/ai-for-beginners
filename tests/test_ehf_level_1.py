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
SUBJECT = "Register EHF Level 1 January 2027"
TO = "carl.e.nissen@gmail.com"
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
            "January 2027, date to be confirmed",
            "The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
            "$444",
            "CAD",
            "Last time at this price",
            "1st time",
            "2nd time",
            "50% off ($222)",
            "3rd time",
            "$111",
            "4th time",
            "$55",
            "5th time and beyond",
            "by donation",
            "12 maximum, any combination of 12 total paying people.",
            "Complete the Quan Yin Virtual Classes (online) first.",
            "Potluck lunch: please bring a dish to share.",
            "Sleeping arrangements",
            "Overnight stays available at The Light House: $100 per night, breakfast included. Let us know in the form if you'd like to stay.",
            "Online payment is being set up. We'll confirm your spot and send payment details after you register.",
            "EHF Holistic Services Canada Inc.",
            "More information about the EHF program",
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
        self.assertNotIn("caroo.jpg", self.html)
        self.assertIn('src="img/class.webp"', self.html)
        without_site_urls = re.sub(r"https://caroo-surrender\.github\.io\S*", " ", self.html, flags=re.I)
        self.assertIsNone(re.search(r"caroo|karoo", without_site_urls, flags=re.I))
        self.assertIn('href="https://ehfpath.com"', self.html)
        script_without_urls = re.sub(r"https://caroo-surrender\.github\.io\S*", " ", self.script, flags=re.I)
        self.assertIsNone(re.search(r"caroo|karoo", script_without_urls, flags=re.I))
        self.assertNotIn("Facilitator:", self.script)
        self.assertIsNone(re.search(r"January\s+(?:[1-9]|[12]\d|3[01])\b", self.html))
        self.assertNotIn("location to be confirmed", self.html)
        self.assertNotIn("location to be confirmed", self.script)
        self.assertNotIn("Details coming soon", self.html)
        self.assertNotIn("Limited to 12", self.html)
        self.assertNotIn("10 spots for new students", self.html)
        self.assertNotIn("2 teachers", self.html)
        self.assertNotIn("paying spots", self.html)
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
        self.assertIn('name="city"', self.html)
        self.assertIn('name="questions"', self.html)
        self.assertIn('name="overnight" value="No" required', self.html)
        self.assertIn('name="overnight" value="1 night"', self.html)
        self.assertIn('name="overnight" value="2 nights"', self.html)
        self.assertIn("Overnight stay?", self.page)
        for value in (
            "First time ($444)",
            "2nd ($222, 50% off)",
            "3rd ($111)",
            "4th ($55)",
            "5th+ (by donation)",
        ):
            self.assertIn(f'value="{value}"', self.html)
        self.assertIn("First time", self.page)
        for label in ("2nd", "3rd", "4th", "5th+"):
            self.assertIn(label, self.page)
        self.assertNotRegex(self.html, r'name="questions"[^>]*required')

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
  city: 'Caledon East',
  attendance: '4th ($55)',
  overnight: '1 night',
  questions: 'Is there parking?'
});
const packed = context.EhfLevel1.buildRegistration({
  name: 'N'.repeat(80),
  email: 'person@example.com',
  phone: '+1 416 555 0199',
  city: 'C'.repeat(80),
  attendance: '5th+ (by donation)',
  overnight: '2 nights',
  questions: 'Q'.repeat(400)
});
const bad = context.EhfLevel1.buildRegistration({
  name: 'Ada',
  email: 'ada@example.com',
  phone: '123',
  city: 'Toronto',
  attendance: 'First time ($444)',
  overnight: 'No'
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
            "4th ($55)",
            "Overnight stay: 1 night",
            "The Light House, 15606 The Gore Rd, Caledon East, ON L7C 3E5",
            "Is there parking?",
            "January 2027, date to be confirmed",
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
