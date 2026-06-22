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
books.json                  source of truth (57 books)
build.py                    regenerates index.html + exports from books.json
index.html                  read-only viewer (generated)
exports/
  Book_Inventory.xlsx       spreadsheet with a status column (generated)
  book_inventory.md         plain-text table (generated)
```

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
| `cat` | broad category |
| `rel` | relevance to my research, 1–5 (5 = core: child welfare, poverty, public finance, applied micro) |
| `pages` | approx. length, standard print edition |
| `status` | `Finished` · `Started` · `Not started` |

Page counts: recent/uncommon titles verified on Amazon or publisher pages;
well-known titles are standard-edition figures.
