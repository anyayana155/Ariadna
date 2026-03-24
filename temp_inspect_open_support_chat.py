from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXTS = {".py", ".html", ".txt"}

print("=== references ===")
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix not in EXTS:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for lineno, line in enumerate(text.splitlines(), 1):
        if "open_support_chat" in line:
            print(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")

print("=== key files ===")
for rel in [
    "config/urls.py",
    "apps/places/views.py",
    "apps/places/urls.py",
    "apps/core/urls.py",
    "templates/places/detail.html",
    "templates/base.html",
]:
    path = ROOT / rel
    print(f"--- {rel} ---")
    if not path.exists():
        print("MISSING")
        continue
    print(path.read_text(encoding="utf-8"))
