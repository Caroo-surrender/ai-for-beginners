#!/usr/bin/env python3
"""Build the December 12 QR code, printable PDF, and PNG flyer.

Uses segno for the QR code and headless Chrome for the HTML flyer.
No paid image service. Re-run from the repo root:

    python3 scripts/render_december_event.py
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
FLYER = ROOT / "december-12-2026" / "flyer"
PAGE = ROOT / "december-12-2026" / "index.html"
URL = "https://caroo-surrender.github.io/ai-for-beginners/december-12-2026/"
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
            ready = await cdp.call(
                "Runtime.evaluate",
                {
                    "expression": "(() => { const img = document.querySelector('.qr img'); return img && img.complete && img.naturalWidth > 0; })()",
                    "returnByValue": True,
                },
            )
            if not ready.get("result", {}).get("value"):
                raise RuntimeError("Flyer QR image did not load")
            await shoot(cdp, 816, 1056, 2, FLYER / "flyer-letter.png")
            await print_pdf(cdp, FLYER / "flyer-letter.pdf")

            await open_page(cdp, PAGE.resolve().as_uri())
            await shoot(cdp, 390, 844, 2, review_dir / "registration-mobile.png", full=True)
            await shoot(cdp, 1280, 900, 1, review_dir / "registration-desktop.png", full=True)
            await shoot(cdp, 320, 700, 2, review_dir / "registration-320.png", full=True)

            filled = await cdp.call(
                "Runtime.evaluate",
                {
                    "expression": """
(() => {
  const form = document.getElementById('reg');
  form.name.value = 'Sample Guest';
  form.contact.value = 'guest@example.com';
  form.party.value = '1';
  form.food.value = 'I may bring a potluck dish';
  form.potluck.value = 'bread';
  form.share.value = 'five-minute show-and-share';
  form.bottleneck.value = 'next step from notes';
  form.notes.value = 'cost is a barrier';
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
            await shoot(cdp, 390, 844, 2, review_dir / "registration-confirm.png", full=True)
        finally:
            reader.cancel()


def main():
    if not CHROME:
        raise SystemExit("google-chrome is required")
    review = Path(tempfile.mkdtemp(prefix="dec12-review-"))
    make_qr()
    profile = tempfile.mkdtemp(prefix="chrome-dec12-")
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
