#!/usr/bin/env python3
"""Look up a book's page count from APIs instead of the browser.

Sources, in order of preference:
  1. Google Books  — best coverage, but the keyless endpoint is heavily rate-limited,
     so it is only used when an API key is available (see below).
  2. Open Library  — free, no key, but coverage is patchy and counts are edition-variable.

API counts are edition-approximate; browser-verify on the publisher/Amazon page when
an exact in-print figure matters.

Usage:
  python3 lookup_pages.py "Title" ["Author last name"]   # one book -> JSON + best guess
  python3 lookup_pages.py --audit                         # compare books.json vs the APIs

Google Books API key (optional but recommended for reliable lookups):
  Create a free key at https://console.cloud.google.com/ -> enable "Books API" ->
  Credentials -> Create credentials -> API key. Then make it available either way:
    export GOOGLE_BOOKS_API_KEY=xxxx          # e.g. in ~/.zshrc
  or put it in a gitignored .env next to this file:
    GOOGLE_BOOKS_API_KEY=xxxx
The key is read from the environment / .env only; it is never written to the repo.
"""
import os, sys, json, ssl, subprocess, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))


def _api_key():
    k = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if k:
        return k.strip()
    envf = os.path.join(ROOT, ".env")
    if os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            line = line.strip()
            if line.startswith("GOOGLE_BOOKS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


GB_KEY = _api_key()


def _get(url):
    """Fetch a URL, preferring urllib but falling back to curl when the Python
    install lacks a CA bundle (common in sandboxes / python.org builds)."""
    try:
        with urllib.request.urlopen(url, timeout=20, context=ssl.create_default_context()) as r:
            return r.read().decode()
    except Exception:
        try:
            return subprocess.run(["curl", "-s", "--max-time", "20", url],
                                  capture_output=True, text=True).stdout
        except Exception:
            return ""


def _json(url):
    try:
        return json.loads(_get(url))
    except Exception:
        return {}


def google_books(title, author=None):
    if not GB_KEY:
        return None  # keyless endpoint is rate-limited; require a key
    q = f"intitle:{title}" + (f" inauthor:{author}" if author else "")
    url = "https://www.googleapis.com/books/v1/volumes?" + urllib.parse.urlencode(
        {"q": q, "maxResults": 5, "country": "US", "key": GB_KEY})
    d = _json(url)
    if d.get("error"):
        return None
    for it in d.get("items", []):
        vi = it.get("volumeInfo", {})
        if vi.get("pageCount") and vi.get("printType", "BOOK") == "BOOK":
            return {"pages": vi["pageCount"], "title": vi.get("title"), "source": "Google Books"}
    return None


def open_library(title, author=None):
    params = {"title": title, "fields": "title,number_of_pages_median", "limit": 3}
    if author:
        params["author"] = author
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode(params)
    for doc in _json(url).get("docs", []):
        if doc.get("number_of_pages_median"):
            return {"pages": doc["number_of_pages_median"], "title": doc.get("title"), "source": "Open Library"}
    return None


def lookup(title, author=None):
    g = google_books(title, author)
    o = open_library(title, author)
    best = g or o
    return {"query": {"title": title, "author": author},
            "google_books": g, "open_library": o,
            "pages": best["pages"] if best else None,
            "source": best["source"] if best else None}


def _lastname(author):
    return author.split("&")[0].split(",")[0].strip().split()[-1] if author else None


def _audit():
    books = json.load(open(os.path.join(ROOT, "books.json"), encoding="utf-8"))
    print(f"{'#':>3}  {'Title':<34}{'json':>5}{'api':>6}  source")
    diffs = 0
    for b in books:
        r = lookup(b["title"], _lastname(b["author"]))
        api = r["pages"]
        ok = api and abs(api - b["pages"]) <= 8
        if not ok:
            diffs += 1
        flag = "" if ok else "  <-- differs/missing"
        print(f"{b['n']:>3}  {b['title'][:33]:<34}{b['pages']:>5}{str(api or '-'):>6}  {(r['source'] or '-')}{flag}")
    print(f"\n{diffs} of {len(books)} differ by >8 pages or were not found (edition variance is normal).")


if __name__ == "__main__":
    args = sys.argv[1:]
    print(f"[key: {'Google Books enabled' if GB_KEY else 'no key — Open Library only'}]", file=sys.stderr)
    if args and args[0] == "--audit":
        _audit()
    elif args:
        r = lookup(args[0], args[1] if len(args) > 1 else None)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        if r["pages"]:
            print(f"\nbest guess: {r['pages']} pages (via {r['source']}) — edition-approximate")
        else:
            print("\nnot found — browser-verify this one")
    else:
        print(__doc__)
