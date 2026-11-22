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

**Language.** English, Japanese, Simplified Chinese or Korean, chosen when the page is built
(`setup --lang`). If none was chosen, the browser language is used, with English as the
fallback. The page has no language selector.

**Navigation.**

- Repositories are selected from a list grouped by owner. The branch, commit ID, commit date
  and file count are shown for the selected repository.
- The folder tree expands on demand.
- The search field has two modes, described under [Search](#search).
- The URL fragment has the form `#<repo>:<path>`, so the browser's back button returns from a
  file to the tree.
- The selected repository and the wrap setting are stored in `localStorage`. If storage is
  unavailable, defaults are used.

**Search.**

| Mode | Scope | Behavior |
| --- | --- | --- |
| Names | All repositories | Matches file paths using the index; results are immediate |
| Contents | This repository (default) | Searches the file content of the selected repository, which is usually already loaded |
| Contents | All repositories | Loads repositories one by one and shows results as they arrive |

- Content search is case-insensitive and requires at least two characters.
- Each result lists the file, the number of matches and up to three matching lines with line
  numbers. Selecting a line opens the file at that line and highlights it; Markdown files open
  in source view in this case.
- Results are limited to 200 files or 2,000 matches.
- The search runs in short slices so that the page remains responsive, and a new query cancels
  the previous one.

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
