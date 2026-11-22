# Explorer page

The explorer page is bundled as [`page/index.html`](../page/index.html). It is a single HTML file
with no external dependencies. This document describes how it is delivered and how it behaves,
for those who want to modify or port it.

## Delivery

`refresh` writes three files to `~/workspace/repo-explorer/dist/`. A Muse space is created from
one of two forms:

| Form | Files | Replaced on refresh |
| --- | --- | --- |
| Two-file (preferred) | `index.html`, `snapshot.json` | `snapshot.json` |
| Single-file | `explorer.html` | `explorer.html` |

The page first reads data embedded in `<script id="snapshot-data" type="application/json">`.
If the element is empty, it loads `snapshot.json` from the same location. In the single-file
form, every `<` in the embedded JSON is written as `<`, so file content cannot terminate
the script element.

The data format is described in [Reference](reference.md#snapshot-format).

## Behavior

**Layout.** The layout is designed for phones. On narrow screens, the tree and the file view
share one pane; on screens 900 px or wider they are shown side by side. Light and dark themes
follow the system setting.

**Languages.** English, Japanese, Simplified Chinese and Korean. The initial language follows
the browser setting, with English as the fallback, and can be changed from the header. All
strings are defined in one dictionary in the page.

**Navigation.**

- Repositories are selected from a list grouped by owner. The branch, commit ID, commit date
  and file count are shown for the selected repository.
- The folder tree expands on demand. File content is rendered only when a file is opened.
- The search field matches paths across all repositories. Selecting a result switches to its
  repository and opens the file.
- The URL fragment has the form `#<repo>:<path>`, so the browser's back button returns from a
  file to the tree.
- The selected language, repository and wrap setting are stored in `localStorage`. If storage
  is unavailable, defaults are used.

**Code view.**

- Long lines wrap by default. The Wrap button switches to horizontal scrolling.
- Line numbers remain aligned with wrapped lines and are excluded from text selection.
- Syntax highlighting is based on the file extension and is disabled for files over 80 KB.
- The Copy button copies the complete file content.
- Files without content are listed in the tree and show the reason when opened (binary, too
  large, excluded, symbolic link or submodule).

## Security

- File content is escaped before highlighting and is never inserted as markup.
- The page loads no external resources (no CDN, web fonts or analytics).
- `noindex` and `no-referrer` are set.
- The page displays private source code and must not be shared through a public link.
