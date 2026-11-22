# Explorer page

The explorer page is bundled as [`page/index.html`](../page/index.html). It is a single HTML file
with no external dependencies. This document describes how it is delivered and how it behaves,
for those who want to modify or port it.

## Delivery

`refresh` builds the page in two forms. A Muse space is created from one of them.

| Form | Files | Uploaded on refresh |
| --- | --- | --- |
| Folder (preferred) | Everything under `dist/site/` | The index and the content files of changed repositories |
| Single-file | `dist/explorer.html` | The whole file |

Layout of the folder form:

| Path | Contents | Loaded |
| --- | --- | --- |
| `index.html` | The page, with the language built in | On open |
| `data/index.json.gz` | Repository list and file tree, without file content | On open |
| `data/<repository>.json.gz` | File content of one repository | When the repository is first shown |
| `data/mermaid.js.gz` | Mermaid (present only if installed by `setup`) | When a diagram is first displayed |

In the single-file form, the same data files are embedded in the page as base64 and decoded only
when needed. The format of the snapshot from which these files are built is described in
[Reference](reference.md#snapshot-format).

## Loading strategy

- Only the index is read at start-up, so the time to the first screen does not depend on the
  amount of code in the included repositories.
- When a repository is selected, its content file is prefetched in the background. Opening a
  file is normally immediate.
- Content of the four most recently used repositories is kept in memory.
- Data is gzip-compressed and decompressed with the browser's `DecompressionStream`. If a server
  has already removed the compression, the data is used as it is.

With 41 repositories and 12,000 files over a simulated 20 Mbit/s connection, the file tree
appeared after 0.25 seconds, compared with 16 seconds when all content was loaded at start-up.

## Behavior

**Layout.** The layout is designed for phones. On narrow screens, the tree and the file view
share one pane; on screens 900 px or wider they are shown side by side. Light and dark themes
follow the system setting.

**Language.** English, Japanese, Simplified Chinese or Korean. The language is chosen in this
order: the viewer's choice in the settings (remembered), the initial language set by Muse at
setup (`setup --lang`, the language the user normally uses with Muse), and the browser language.
English is the fallback.

**Settings.** The gear button opens the settings: language and whether long lines wrap.

**Navigation.**

- Repositories are selected from a list grouped by owner. The branch, commit ID, commit date
  and file count are shown for the selected repository.
- The folder tree expands on demand.
- The search field searches file names or file contents (see **Search** below).
- The URL fragment has the form `#<repo>:<path>`, so the browser's back button returns from a
  file to the tree.
- The selected repository and the wrap setting are stored in `localStorage`. If storage is
  unavailable, defaults are used.

**Search.**

The search field has two modes, **Names** (file paths) and **Contents** (text inside files), and
a scope button shared by both:

| Scope | Behavior |
| --- | --- |
| This repository (default) | Searches the selected repository; results follow when another repository is selected |
| All repositories | Searches every repository; content search loads them one by one and shows results as they arrive |
| Picked repositories | Repositories chosen with check boxes in the scope panel, grouped by owner |

- Checking every repository is the same as "All repositories"; clearing every check box returns to
  "This repository". The scope is remembered.
- Name search uses the index only, so its results are immediate in any scope.
- Content search is case-insensitive and requires at least two characters.
- Each result lists the file, the number of matches and up to three matching lines with line
  numbers. Selecting a line opens the file at that line and highlights it; Markdown files open
  in source view in this case.
- Results are limited to 200 files or 2,000 matches.
- The search runs in short slices so that the page remains responsive, and a new query cancels
  the previous one.

**Header.** The button at the right of the title row collapses the repository selector, search
field and scope panel to a single line that shows the selected repository. The state is
remembered.

**Asking Muse.**

- Tap a line number to select that line; tap another line number to select the range between
  them. A bar at the bottom shows the selection.
- **Ask Muse** (in the file bar or the selection bar) opens a sheet with an optional question and
  the line range, pre-filled from the selection. The range can also be typed, which works from the
  Markdown preview as well. The lines in the range are shown in the sheet so that they can be
  checked before sending. Without a range, the question refers to the whole file (the fields
  show the first and last line numbers as a guide).
- **Copy to clipboard** copies the message; paste it into the Muse chat to ask. The page cannot post
  into the chat by itself. Where the system share sheet is available, **Share…** offers the same
  text to other apps.
- The message identifies the repository, file, line range, branch and commit, and includes a
  command that reads exactly those lines from Muse's local clone, for example:

  ```text
  Code: your-org/your-repo src/app.py L18-L21 (main @ abc1234)
  Read locally: git -C ~/ghq/github.com/your-org/your-repo show abc1234:src/app.py | sed -n '18,21p'
  ```

- The code itself is never included: Muse reads it from its local clone, which keeps the
  conversation short and saves tokens.
- With a selection, **Copy** in the file bar copies only the selected lines.

**Code view.**

- Long lines wrap by default. The Wrap button switches to horizontal scrolling.
- Line numbers remain aligned with wrapped lines and are excluded from text selection.
- Syntax highlighting is based on the file extension and is disabled for files over 80 KB.
- The Copy button copies the complete file content.
- Files without content are listed in the tree and show the reason when opened (binary, too
  large, excluded, symbolic link or submodule).

**Markdown preview.** Files ending in `.md` or `.markdown` open as formatted documents; the
Preview button switches to the source. Supported: headings with anchors, emphasis, inline code,
fenced code with highlighting, lists including task lists, tables with alignment, block quotes,
horizontal rules, links and front matter. Links to other files in the repository open them in
the explorer, and `#anchor` links scroll within the document. Raw HTML is not rendered: tags are
removed and their text is kept, and `<script>` and `<style>` elements are removed entirely.
Images are shown as their alternative text, because the page loads no external resources.

**Mermaid.** Fenced code blocks with the language `mermaid`, and files ending in `.mmd` or
`.mermaid`, are rendered as diagrams. If Mermaid is not installed or a diagram cannot be
rendered, the source is shown with a notice.

## Security

- File content is escaped before display. Markdown is converted from escaped text, and only links
  with `http`, `https` or `mailto` schemes become external links.
- Mermaid runs with `securityLevel: 'strict'`, which sanitizes the generated SVG.
- The page loads no external resources (no CDN, web fonts or analytics). `noindex` and
  `no-referrer` are set.
- The page displays private source code and must not be shared through a public link.
