#!/usr/bin/env python3
"""PLASMA FORGE HTTP Server — Port 3400
Routes:
  GET  /              -> index.html
  GET  /style.css     -> style.css
  GET  /script.js     -> script.js
  GET  /api/theme     -> Rust theme_engine (ou fallback Python)
  GET  /api/svg       -> Java ThemeGenerator
  POST /api/save      -> sauve JSON dans saved/
  GET  /api/health    -> status
"""
import sys, os, json, subprocess, urllib.parse, time, random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOME = Path.home()
BASE = HOME / "plasma-forge"
WWW = BASE / "www"
SRC = BASE / "src"
SAVED = BASE / "saved"
SAVED.mkdir(parents=True, exist_ok=True)
THEME_ENGINE = SRC / "theme_engine"
JAVA_CLASS_DIR = str(SRC)
PORT = int(os.environ.get("PLASMA_PORT", "3400"))

# Fallback Python : génère un thème si Rust absent
def python_theme_fallback(seed=None):
    rng = random.Random(seed if seed else int(time.time() * 1000))
    scheme_types = ["monochromatic", "complementary", "triadic", "tetradic"]
    scheme = rng.choice(scheme_types)
    base_hue = rng.uniform(0, 360)
    base_sat = rng.uniform(60, 90)
    base_light = rng.uniform(45, 65)
    bg_l = rng.uniform(6, 12)
    surface_l = bg_l + 8
    accent_h = {
        "monochromatic": base_hue,
        "complementary": (base_hue + 180) % 360,
        "triadic": (base_hue + 120) % 360,
        "tetradic": (base_hue + 90) % 360,
    }[scheme]
    accent2_h = {
        "monochromatic": base_hue,
        "complementary": base_hue,
        "triadic": (base_hue + 240) % 360,
        "tetradic": (base_hue + 270) % 360,
    }[scheme]
    palette = [
        f"hsl({base_hue:.0f}, {base_sat:.0f}%, {base_light:.0f}%)",
        f"hsl({accent_h:.0f}, {base_sat:.0f}%, {base_light+5:.0f}%)",
        f"hsl({accent2_h:.0f}, {base_sat:.0f}%, {base_light+5:.0f}%)",
        f"hsl({base_hue:.0f}, {base_sat*0.7:.0f}%, {base_light+25:.0f}%)",
        f"hsl({(base_hue+60)%360:.0f}, {base_sat:.0f}%, {base_light:.0f}%)",
    ]
    return {
        "seed": str(int(time.time() * 1000)),
        "scheme": scheme,
        "colors": {
            "bg": f"hsl({base_hue:.0f}, {base_sat*0.5:.0f}%, {bg_l:.0f}%)",
            "surface": f"hsl({base_hue:.0f}, {base_sat*0.5:.0f}%, {surface_l:.0f}%)",
            "primary": f"hsl({base_hue:.0f}, {base_sat:.0f}%, {base_light:.0f}%)",
            "accent": f"hsl({accent_h:.0f}, {base_sat:.0f}%, {base_light+10:.0f}%)",
            "accent2": f"hsl({accent2_h:.0f}, {base_sat:.0f}%, {base_light+10:.0f}%)",
            "text": f"hsl({base_hue:.0f}, 15%, 92%)",
            "muted": f"hsl({base_hue:.0f}, 15%, 65%)",
            "palette": palette,
        },
        "params": {
            "anim_duration": round(rng.uniform(6, 18), 1),
            "blob_count": rng.randint(3, 6),
            "grid_cols": rng.randint(4, 7),
            "border_radius": round(rng.uniform(4, 24), 1),
            "font_scale": round(rng.uniform(0.95, 1.05), 2),
            "letter_spacing": round(rng.uniform(-0.04, 0.04), 3),
        },
        "svg": {
            "voronoi_points": rng.randint(8, 15),
            "noise_scale": round(rng.uniform(0.5, 2.5), 2),
            "rotation": rng.randint(0, 359),
        },
        "engine": "python-fallback",
        "timestamp": int(time.time()),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        try: self.wfile.write(b)
        except BrokenPipeError: pass

    def _read_body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode() if n else ""

    def do_OPTIONS(self):
        self._send(200, "", "text/plain")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            f = WWW / "index.html"
            self._send(200, f.read_text(encoding="utf-8")) if f.exists() else self._send(404, "index.html not found", "text/plain")

        elif path == "/style.css":
            f = WWW / "style.css"
            self._send(200, f.read_text(encoding="utf-8"), "text/css; charset=utf-8") if f.exists() else self._send(404, "css not found", "text/plain")

        elif path == "/script.js":
            f = WWW / "script.js"
            self._send(200, f.read_text(encoding="utf-8"), "application/javascript; charset=utf-8") if f.exists() else self._send(404, "js not found", "text/plain")

        elif path == "/api/theme":
            seed = qs.get("seed", [None])[0]
            # Try Rust first
            if THEME_ENGINE.exists():
                try:
                    cmd = [str(THEME_ENGINE)]
                    if seed: cmd.append(str(seed))
                    r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if r.returncode == 0 and r.stdout.strip().startswith("{"):
                        data = json.loads(r.stdout)
                        data["engine"] = "rust"
                        self._send(200, json.dumps(data), "application/json")
                        return
                except Exception as e:
                    print(f"[PLASMA] Rust fallback: {e}", file=sys.stderr)
            # Fallback Python
            data = python_theme_fallback(seed)
            self._send(200, json.dumps(data), "application/json")

        elif path == "/api/svg":
            seed = qs.get("seed", [str(int(time.time() * 1000))])[0]
            points = qs.get("points", ["12"])[0]
            palette = qs.get("palette", ["#FF006E,#FB5607,#FFBE0B,#8338EC,#3A86FF"])[0]
            try:
                r = subprocess.run(
                    ["java", "-cp", JAVA_CLASS_DIR, "ThemeGenerator", str(seed), str(points), "1920", "1080", palette],
                    capture_output=True, text=True, timeout=10
                )
                if r.returncode == 0 and r.stdout.strip():
                    self._send(200, r.stdout, "image/svg+xml; charset=utf-8")
                else:
                    err = r.stderr[:300] if r.stderr else "no output"
                    self._send(500, f"<!-- Java failed: {err} -->", "image/svg+xml")
            except subprocess.TimeoutExpired:
                self._send(504, "<!-- Java timeout -->", "image/svg+xml")
            except Exception as e:
                self._send(500, f"<!-- err: {e} -->", "image/svg+xml")

        elif path == "/api/health":
            self._send(200, json.dumps({
                "status": "ok",
                "rust": THEME_ENGINE.exists(),
                "rust_version": os.popen("rustc --version 2>/dev/null").read().strip() or "absent",
                "java": (SRC / "ThemeGenerator.class").exists(),
                "java_version": os.popen("java -version 2>&1 | head -1").read().strip(),
                "port": PORT,
                "www": str(WWW),
            }), "application/json")

        elif path == "/api/saved":
            saved_list = []
            for f in SAVED.glob("theme-*.json"):
                saved_list.append({"name": f.name, "size": f.stat().st_size})
            self._send(200, json.dumps({"saved": saved_list}), "application/json")

        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/save":
            body = self._read_body()
            try:
                data = json.loads(body)
                seed = data.get("seed", "unknown").replace("/", "_")
                f = SAVED / f"theme-{seed}.json"
                f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                self._send(200, json.dumps({"saved": str(f)}), "application/json")
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}), "application/json")
        else:
            self._send(404, "Not found", "text/plain")

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[PLASMA] {self.address_string()} {fmt % args}\n")


if __name__ == "__main__":
    print(f"[PLASMA FORGE] HTTP server on :{PORT}")
    print(f"  WWW  : {WWW}")
    print(f"  Rust : {THEME_ENGINE} ({'OK' if THEME_ENGINE.exists() else 'ABSENT — fallback Python'})")
    print(f"  Java : {SRC}/ThemeGenerator.class ({'OK' if (SRC / 'ThemeGenerator.class').exists() else 'ABSENT'})")
    print(f"  Saved: {SAVED}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
