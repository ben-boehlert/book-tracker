# Book Tracker

**Live:** https://ben-boehlert.github.io/book-tracker/ (public GitHub Pages site)

A simple, version-controlled tracker for my personal library — what I own, how
relevant each book is to my research, how long it is, and where I am in it.

## How it works

- **`books.json` is the single source of truth.** One object per book.
- **I don't hand-edit.** To change something (mark a book finished, add a title,
  fix a page count), I ask Claude in plain English; Claude edits `books.json`,
  reruns the build, and commits the change. Git history is the reading log.
- **`index.html` is a read-only viewer** — sortable, searchable, filterable.
  Open it in any browser (no server needed; data is embedded). It is generated,
  so don't edit it by hand.

## Layout

```
books.json                  source of truth
build.py                    regenerates index.html + exports from books.json
lookup_pages.py             look up a book's page count from APIs (not the browser)
index.html                  read-only viewer (generated)
exports/
  Book_Inventory.xlsx       spreadsheet with a status column (generated)
  book_inventory.md         plain-text table (generated)
```

## Use from a Claude.ai Project

`claude_project.md` holds instructions to paste into a Claude.ai Project so a regular
chat can pull this data from GitHub and help you query/decide what to read. The Project
(GitHub connector) is read-only; edits are drafted there and applied via a Claude Code
session, which commits and pushes.

## Looking up page counts

Instead of opening the browser to a retailer, query the APIs:

```bash
python3 lookup_pages.py "The Power to Destroy" "Graetz"   # one book
python3 lookup_pages.py --audit                            # compare books.json vs APIs
```

- **Open Library** is the keyless default — instant, but coverage is patchy and counts
  are edition-variable (can be off by tens of pages from the in-print edition).
- **Google Books** has better coverage but its keyless endpoint is rate-limited, so it
  only kicks in when an API key is set. Create a free key at
  <https://console.cloud.google.com/> (enable "Books API" → Credentials → API key), then:
  ```bash
  export GOOGLE_BOOKS_API_KEY=xxxx        # in ~/.zshrc, OR
  echo 'GOOGLE_BOOKS_API_KEY=xxxx' > .env # gitignored, stays local
  ```
  The key is read from the environment / `.env` only and is never committed.

API counts are edition-approximate. When an exact figure matters, browser-verify on the
publisher or Amazon page.

## Rebuild after editing books.json

```bash
python3 build.py
```

## Fields in `books.json`

| field | meaning |
|-------|---------|
| `n` | stable id / shelf order |
| `title`, `author` | book |
| `shelf` | which photographed shelf (1–3) |
| `cat` | broad subject category |
| `relevance` | research bucket: `Immediately relevant` · `Will be relevant` · `Maybe relevant` · `For fun` |
| `pages` | approx. length, standard print edition |
| `status` | `Finished` · `Started` · `Not started` |

Page counts: recent/uncommon titles verified on Amazon or publisher pages;
well-known titles are standard-edition figures.
