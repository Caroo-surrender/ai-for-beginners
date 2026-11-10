#!/usr/bin/env python3
"""Build the December 4 house-party QR code, printable PDF, and PNG flyer.

Uses segno for the QR code and headless Chrome for the HTML flyer.
No paid image service. Re-run from the repo root:

    python3 scripts/render_december_4.py
"""

import asyncio
import base64
import json
import shutil
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

import segno
import websockets

ROOT = Path(__file__).resolve().parents[1]
FLYER = ROOT / "december-4-2026" / "flyer"
PAGE = ROOT / "december-4-2026" / "index.html"
URL = "https://caroo-surrender.github.io/ai-for-beginners/december-4-2026/"
CHROME = shutil.which("google-chrome") or shutil.which("google-chrome-stable")


def make_qr():
    qr = segno.make(URL, error="h", boost_error=False)
    qr.save(FLYER / "qr.svg", scale=8, border=4, dark="#241c16", light="#ffffff")
    qr.save(FLYER / "qr.png", scale=16, border=4, dark="#241c16", light="#ffffff")


class Cdp:
    def __init__(self, ws):
        self.ws = ws
        self.n = 0
        self.pending = {}
        self.events = asyncio.Queue()

    async def reader(self):
        async for raw in self.ws:
            msg = json.loads(raw)
            if "id" in msg:
                fut = self.pending.pop(msg["id"])
                fut.set_result(msg)
            else:
                await self.events.put(msg)

    async def call(self, method, params=None, timeout=30):
        self.n += 1
        fut = asyncio.get_running_loop().create_future()
        self.pending[self.n] = fut
        await self.ws.send(json.dumps({"id": self.n, "method": method, "params": params or {}}))
        msg = await asyncio.wait_for(fut, timeout)
        if "error" in msg:
            raise RuntimeError(msg["error"])
        return msg.get("result") or {}

    async def wait_event(self, name, timeout=30):
        while True:
            msg = await asyncio.wait_for(self.events.get(), timeout)
            if msg.get("method") == name:
                return msg


async def open_page(cdp, uri):
    await cdp.call("Page.enable")
    await cdp.call("Runtime.enable")
    await cdp.call("Page.navigate", {"url": uri})
    await cdp.wait_event("Page.loadEventFired")
    await cdp.call(
        "Runtime.evaluate",
        {"expression": "document.fonts.ready.then(() => 'ok')", "awaitPromise": True},
    )


async def shoot(cdp, width, height, scale, path, full=False):
    await cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": scale,
            "mobile": width < 500,
        },
    )
    if full:
        metrics = await cdp.call("Page.getLayoutMetrics")
        css = metrics["cssContentSize"]
        height = max(height, int(css["height"]) + 1)
        await cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": scale,
                "mobile": width < 500,
            },
        )
    result = await cdp.call(
        "Page.captureScreenshot",
        {
            "format": "png",
            "captureBeyondViewport": False,
            "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1},
        },
    )
    path.write_bytes(base64.b64decode(result["data"]))


async def print_pdf(cdp, path):
    await cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": 816, "height": 1056, "deviceScaleFactor": 1, "mobile": False},
    )
    result = await cdp.call(
        "Page.printToPDF",
        {
            "paperWidth": 8.5,
            "paperHeight": 11,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
            "printBackground": True,
            "preferCSSPageSize": True,
            "displayHeaderFooter": False,
        },
    )
    path.write_bytes(base64.b64decode(result["data"]))


async def render_all(ws_url, review_dir):
    async with websockets.connect(ws_url, max_size=40_000_000) as ws:
        cdp = Cdp(ws)
        reader = asyncio.create_task(cdp.reader())
        try:
            await open_page(cdp, (FLYER / "flyer.html").resolve().as_uri())
            fit = await cdp.call(
                "Runtime.evaluate",
                {
                    "expression": """
(() => {
  const imgs = [...document.images];
  const pages = [...document.querySelectorAll('.sheet')].map(sheet => {
    const sr = sheet.getBoundingClientRect();
    const url = sheet.querySelector('.url').getBoundingClientRect();
    const qr = sheet.querySelector('.qr img').getBoundingClientRect();
    return {
      h: sr.height,
      urlInside: url.bottom <= sr.bottom + 2 && url.top >= sr.top - 1,
      qrWidth: qr.width
    };
  });
  return {
    imgs: imgs.map(img => ({src: img.currentSrc.split('/').pop(), ok: img.complete && img.naturalWidth > 0})),
    pages
  };
})()
""",
                    "returnByValue": True,
                },
            )
            info = fit["result"]["value"]
            (review_dir / "flyer-fit.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
            if not all(item["ok"] for item in info["imgs"]):
                raise RuntimeError(f"Flyer image failed to load: {info['imgs']}")
            for page in info.get("pages") or []:
                if not page["urlInside"]:
                    raise RuntimeError(f"Flyer URL is clipped: {info}")
                if page["qrWidth"] < 120:
                    raise RuntimeError(f"QR is too small: {info}")
            await print_pdf(cdp, FLYER / "flyer-letter.pdf")
            subprocess.check_call(
                ["pdftoppm", "-r", "170", "-png", str(FLYER / "flyer-letter.pdf"), str(review_dir / "page")]
            )
            first = review_dir / "page-1.png"
            second = review_dir / "page-2.png"
            if not first.exists() or not second.exists():
                raise RuntimeError("Expected a 2-page flyer PDF")
            (FLYER / "flyer-letter.png").write_bytes(first.read_bytes())
            (FLYER / "flyer-letter-page2.png").write_bytes(second.read_bytes())

            await open_page(cdp, PAGE.resolve().as_uri())
            await shoot(cdp, 390, 844, 2, review_dir / "page-mobile.png", full=True)
            await shoot(cdp, 1280, 900, 1, review_dir / "page-desktop.png", full=True)
            await shoot(cdp, 320, 700, 2, review_dir / "page-320.png", full=True)
            filled = await cdp.call(
                "Runtime.evaluate",
                {
                    "expression": """
(() => {
  const form = document.getElementById('reg');
  form.name.value = 'Sample Guest';
  form.email.value = 'guest@example.com';
  form.guests.value = '2';
  form.dish.value = 'Vegetables';
  form.sleep.value = 'Yes, sleeping over';
  form.staying.value = '2';
  form.mastermind.value = 'Yes';
  form.requestSubmit();
  const link = document.getElementById('mail-open');
  return {
    hidden: document.getElementById('confirm').hidden,
    subject: document.getElementById('confirm-subject').textContent,
    to: document.getElementById('confirm-to').textContent,
    href: link.getAttribute('href'),
    body: document.getElementById('confirm-body').textContent,
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth
  };
})()
""",
                    "returnByValue": True,
                },
            )
            (review_dir / "confirmation.json").write_text(
                json.dumps(filled["result"]["value"], indent=2), encoding="utf-8"
            )
            await shoot(cdp, 390, 844, 2, review_dir / "page-confirm.png", full=True)
        finally:
            reader.cancel()


def main():
    if not CHROME:
        raise SystemExit("google-chrome is required")
    review = Path(tempfile.mkdtemp(prefix="dec4-review-"))
    make_qr()
    profile = tempfile.mkdtemp(prefix="chrome-dec4-")
    proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--hide-scrollbars",
            "--remote-debugging-port=0",
            "--remote-allow-origins=*",
            f"--user-data-dir={profile}",
            "--no-first-run",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        port_file = Path(profile) / "DevToolsActivePort"
        deadline = time.time() + 20
        while not port_file.exists():
            if proc.poll() is not None:
                raise RuntimeError(f"Chrome exited {proc.returncode}")
            if time.time() > deadline:
                raise RuntimeError("Chrome did not open a DevTools port")
            time.sleep(0.1)
        port = port_file.read_text(encoding="utf-8").splitlines()[0].strip()
        flyer_uri = (FLYER / "flyer.html").resolve().as_uri()
        opener = urllib.request.Request(
            f"http://127.0.0.1:{port}/json/new?{urllib.parse.quote(flyer_uri, safe='')}",
            data=b"",
            method="PUT",
        )
        with urllib.request.urlopen(opener) as response:
            target = json.load(response)
        asyncio.run(render_all(target["webSocketDebuggerUrl"], review))
        print(f"REVIEW {review}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
