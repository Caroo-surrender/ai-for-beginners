#!/usr/bin/env python3
"""Checks for the December 12, 2026 event page, email registration, and flyer."""

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
EVENT = ROOT / "december-12-2026"
CANONICAL = "https://caroo-surrender.github.io/ai-for-beginners/december-12-2026/"
SUBJECT = "RSVP AI Ninjas Mastermind Dec 12 2026"
PRICE = "$20 per person"
ACCESS = "Cost a barrier? Reach out to Caroo\u2014we can arrange another way to contribute, such as cleanup."
FOOD = "Winter soup and a fruit dish. You\u2019re welcome to bring a potluck dish."
BOTTLENECK = "Bring your biggest bottleneck. We\u2019ll work through it together with practical solutions and tools for your next step that day."
PAY = "Payment details by email after registration."
READABLE_URL = "caroo-surrender.github.io/ai-for-beginners/december-12-2026"
NODE = "/exec-daemon/node"

BANNED = [
    r"\bdonation\b",
    r"no set fee",
    r"\bfree\b",
    r"\bUSD\b",
    r"\bCAD\b",
    r"\bdollars?\b",
    r"e-transfer",
    r"etransfer",
    r"paypal",
    r"venmo",
    r"interac",
    r"\bstripe\b",
    r"\bcash\b",
    r"\bcheque\b",
    r"\bwaiver\b",
    r"\bqualif",
    r"\beligib",
    r"\bscholarship\b",
    r"\bdiscount\b",
    r"\bmenu\b",
    r"\bgluten\b",
    r"\bvegan\b",
    r"\bvegetarian\b",
    r"\ballergen",
    r"\bdietary\b",
    r"food option",
    r"La Focaccia",
    r"quanyin",
    r"Lighthouse",
    r"Gore Road",
    r"November",
    r"Nov 8",
    r"Nov 5",
    r"Oct 25",
    r"10:30",
    r"5:30",
    r"\$30",
    r"\$33",
    r"16 people",
    r"16 seats",
    r"Max 16",
    r"Advanced AI Group",
    r"AI for Beginners",
    r"\bTBD\b",
    r"sandwich",
    r"Chicken Parm",
    r"Mortadella",
]


def plain_html(html):
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def event_text():
    parts = []
    for path in [
        EVENT / "index.html",
        EVENT / "register.js",
        EVENT / "flyer" / "flyer.html",
    ]:
        parts.append(path.read_text(encoding="utf-8"))
    pdf_text = subprocess.check_output(
        ["pdftotext", "-layout", str(EVENT / "flyer" / "flyer-letter.pdf"), "-"],
        text=True,
    )
    parts.append(pdf_text)
    return "\n".join(parts), pdf_text


class DecemberEventTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, pdf_text = event_text()
        cls.pdf_text = re.sub(r"\s+", " ", pdf_text)
        cls.page = plain_html((EVENT / "index.html").read_text(encoding="utf-8"))
        cls.flyer = plain_html((EVENT / "flyer" / "flyer.html").read_text(encoding="utf-8"))
        cls.script = (EVENT / "register.js").read_text(encoding="utf-8")

    def test_historical_files_untouched(self):
        result = subprocess.run(
            ["git", "diff", "--exit-code", "main", "--", "index.html", "advanced"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        advanced = (ROOT / "advanced" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Sunday, November 8, 2026", advanced)
        self.assertIn("RSVP Advanced AI Nov 8", advanced)
        root = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("./advanced/", root)

    def test_required_facts_on_page_flyer_and_pdf(self):
        for label, text in (("page", self.page), ("flyer", self.flyer), ("pdf", self.pdf_text)):
            for fact in (
                "Saturday, December 12, 2026",
                "11 AM",
                "4 PM",
                "Toronto time",
                "Location details to be confirmed",
                "AI Ninjas Mastermind",
                "Facilitated by Caroo",
                "five-minute show-and-share",
                PRICE,
                ACCESS,
                FOOD,
                BOTTLENECK,
                PAY,
                READABLE_URL,
            ):
                self.assertIn(fact, text, f"{fact!r} missing from {label}")
        self.assertIn(CANONICAL, (EVENT / "flyer" / "flyer.html").read_text(encoding="utf-8"))
        self.assertIn(CANONICAL, (EVENT / "index.html").read_text(encoding="utf-8"))
        self.assertIn(SUBJECT, self.page)
        self.assertIn("You are registered only after you press Send", self.page)
        self.assertIn("sensitive or business-confidential", self.page)
        for leaked in (
            "no recipient or payment method is named",
            "fixed timetable",
            "reach the hosts",
            "business-confidential",
            "Not every problem can be fully resolved",
        ):
            self.assertNotIn(leaked, self.flyer)
            self.assertNotIn(leaked, self.pdf_text)

    def test_removed_wording_is_absent(self):
        for pattern in BANNED:
            self.assertIsNone(
                re.search(pattern, self.raw, flags=re.I),
                f"found banned pattern {pattern}",
            )
        for text in (self.page, self.flyer, self.script):
            lowered = text.lower()
            self.assertEqual(
                lowered.count("details to be confirmed"),
                lowered.count("location details to be confirmed"),
            )

    def test_registration_fields_and_honesty(self):
        html = (EVENT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="reg"', html)
        self.assertIn('name="name" required', html)
        self.assertIn('name="contact" required', html)
        for optional in ("party", "food", "potluck", "share", "bottleneck", "notes"):
            self.assertNotRegex(html, rf'name="{optional}"[^>]*required')
        self.assertIn("Preparing this email does not register you.", self.page)
        self.assertIn("not a commitment", self.page.lower())
        self.assertIn('href="flyer/flyer-letter.pdf"', html)
        self.assertIn(f'href="{CANONICAL}"', html)
        self.assertIn(f'rel="canonical" href="{CANONICAL}"', html)

    def test_message_builder(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const context = {};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const built = context.DecemberEvent.buildRegistration({
  name: 'Sample Guest',
  contact: 'guest@example.com',
  party: '2',
  food: 'I may bring a potluck dish',
  potluck: 'bread',
  share: 'A five-minute show-and-share',
  bottleneck: 'Getting from notes to a next step',
  notes: 'Sample only'
});
const packed = context.DecemberEvent.buildRegistration({
  name: 'N'.repeat(80),
  contact: 'c'.repeat(80),
  party: '12',
  food: 'Not sure yet',
  potluck: 'p'.repeat(80),
  share: 's'.repeat(140),
  bottleneck: 'b'.repeat(160),
  notes: 'n'.repeat(140)
});
const blank = context.DecemberEvent.buildRegistration({
  name: 'Ada',
  contact: 'ada@example.com'
});
const bad = context.DecemberEvent.buildRegistration({
  name: 'Ada',
  contact: 'ada@example.com',
  party: '0'
});
if (built.error) process.exit(2);
const href = new URL(built.href);
const body = href.searchParams.get('body');
const out = {
  subject: href.searchParams.get('subject'),
  to: href.pathname,
  body,
  packedLength: packed.href.length,
  blankFood: blank.body.includes('Not specified'),
  blankDish: blank.body.includes('None named'),
  bad: bad.error || ''
};
process.stdout.write(JSON.stringify(out));
"""
        result = subprocess.run(
            [NODE, "-e", script, str(EVENT / "register.js")],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["subject"], SUBJECT)
        self.assertEqual(data["to"], "carl.e.nissen@gmail.com")
        for fact in (PRICE, ACCESS, FOOD, BOTTLENECK, PAY, "Sample Guest", "bread", "five-minute show-and-share", "Sending this email registers you."):
            self.assertIn(fact, data["body"])
        for pattern in BANNED:
            self.assertIsNone(re.search(pattern, data["body"], flags=re.I))
        self.assertLess(data["packedLength"], 1900, "mailto URL is long enough to be dropped on phones")
        self.assertTrue(data["blankFood"])
        self.assertTrue(data["blankDish"])
        self.assertIn("whole number", data["bad"])

    def test_qr_codes_decode_to_canonical_url(self):
        self.assertEqual(decode_qr(EVENT / "flyer" / "qr.png"), CANONICAL)
        with tempfile.TemporaryDirectory() as tmp:
            svg_png = Path(tmp) / "qr-svg.png"
            rasterize_qr_svg(EVENT / "flyer" / "qr.svg", svg_png)
            self.assertEqual(decode_qr(svg_png), CANONICAL)
            pdf_png = Path(tmp) / "pdfpage"
            subprocess.check_call(
                [
                    "pdftoppm",
                    "-r",
                    "200",
                    "-png",
                    "-f",
                    "1",
                    "-singlefile",
                    str(EVENT / "flyer" / "flyer-letter.pdf"),
                    str(pdf_png),
                ],
                stdout=subprocess.DEVNULL,
            )
            self.assertEqual(decode_qr(Path(str(pdf_png) + ".png")), CANONICAL)
        self.assertEqual(decode_qr(EVENT / "flyer" / "flyer-letter.png"), CANONICAL)

    def test_pdf_is_one_letter_page_with_the_registration_link(self):
        reader = PdfReader(str(EVENT / "flyer" / "flyer-letter.pdf"))
        self.assertEqual(len(reader.pages), 1)
        box = reader.pages[0].mediabox
        self.assertAlmostEqual(float(box.width), 612, delta=2)
        self.assertAlmostEqual(float(box.height), 792, delta=2)
        uris = []
        for annot in reader.pages[0].get("/Annots") or []:
            obj = annot.get_object()
            action = obj.get("/A")
            if action is not None and action.get("/URI"):
                uris.append(str(action.get("/URI")))
            if obj.get("/URI"):
                uris.append(str(obj.get("/URI")))
        self.assertIn(CANONICAL, uris)
        self.assertFalse(any("advanced" in uri for uri in uris))


def rasterize_qr_svg(svg_path, png_path):
    """Draw segno's stroked SVG QR into a PNG without a browser."""
    text = Path(svg_path).read_text(encoding="utf-8")
    width = int(re.search(r'width="(\d+)"', text).group(1))
    height = int(re.search(r'height="(\d+)"', text).group(1))
    scale = float(re.search(r"scale\(([\d.]+)\)", text).group(1))
    stroke = re.search(r'stroke="#([0-9A-Fa-f]{6})"', text).group(1)
    color = tuple(int(stroke[i : i + 2], 16) for i in (0, 2, 4))
    path = re.search(r'stroke="#[0-9A-Fa-f]{6}" d="([^"]+)"', text).group(1)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    x = y = 0.0
    tokens = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?", path)
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd in ("M", "m"):
            dx, dy = float(tokens[i + 1]), float(tokens[i + 2])
            x, y = (dx, dy) if cmd == "M" else (x + dx, y + dy)
            i += 3
        elif cmd == "h":
            length = float(tokens[i + 1])
            x0, x1 = (x, x + length) if length >= 0 else (x + length, x)
            draw.rectangle(
                [x0 * scale, (y - 0.5) * scale, x1 * scale - 1, (y + 0.5) * scale - 1],
                fill=color,
            )
            x += length
            i += 2
        else:
            raise AssertionError(f"unexpected SVG command {cmd}")
    image.save(png_path)


def decode_qr(path):
    result = subprocess.run(
        ["zbarimg", "--quiet", "--raw", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise AssertionError(f"{path} decoded {lines!r}")
    return lines[0]


if __name__ == "__main__":
    unittest.main()
