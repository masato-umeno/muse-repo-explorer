#!/usr/bin/env python3
"""One command per step, short output. Designed so an AI agent spends as few tokens as possible.

    python3 repo_viewer.py next                  print the single next action; repeat until DONE
    python3 repo_viewer.py setup [--lang en|ja|zh-CN|ko|auto]
                                                   install ghq, gh and Mermaid if missing;
                                                   set the page's initial language;
                                                   check sign-in
    python3 repo_viewer.py login                 start GitHub device sign-in, print the code
    python3 repo_viewer.py login --wait          wait for approval, then configure git
    python3 repo_viewer.py list [--all]          repositories you can clone (compact)
    python3 repo_viewer.py clone OWNER/REPO ...  clone with ghq and install hooks
    python3 repo_viewer.py refresh [--no-pull]   pull, snapshot, build the page, list what to upload
    python3 repo_viewer.py mark-synced [--mode folder|single-file]
                                                   record that the space now shows this build
    python3 repo_viewer.py status                one-line state
    python3 repo_viewer.py build                 snapshot + page without pulling (used by hooks)

Every command is idempotent: re-running a finished step is safe and cheap.
State lives in $REPO_VIEWER_HOME (default ~/workspace/repo-viewer), outside any repository.
"""
import base64
import fcntl
import gzip
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from contextlib import redirect_stdout

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import update_snapshot  # noqa: E402

BIN = os.path.expanduser('~/.local/bin')
TEMPLATE = os.path.join(TOOLS, '..', 'page', 'index.html')
HOME = update_snapshot.home_dir()
# Binaries installed by `setup` must be usable by every subprocess.
os.environ['PATH'] = BIN + os.pathsep + os.environ.get('PATH', '')
DIST = os.path.join(HOME, 'dist')
SITE = os.path.join(DIST, 'site')
SINGLE = os.path.join(DIST, 'viewer.html')
STATE = os.path.join(HOME, '.page-state.json')
LANG_FILE = os.path.join(HOME, '.page-lang')

SAMPLE_REPO = 'masato-umeno/muse-repo-viewer'
# Bump when an existing installation must run `setup` again after updating the tool
# (for example, a new dependency or a new pinned Mermaid version).
SETUP_VERSION = '2'
SETUP_MARKER = os.path.join(HOME, '.setup-version')
STAR_NOTE = os.path.join(HOME, '.star-note-shown')
# State files of versions before the folder form (kept only to migrate existing spaces).
LEGACY_STATE = ('.page-mode', '.page-synced-heads', '.page-template-hash')
LANGS = ('en', 'ja', 'zh-CN', 'ko')

# Mermaid is downloaded at setup time (it is too large for this public repository) and verified
# against this pinned SHA-256 of dist/mermaid.min.js before it is ever embedded in a page.
MERMAID_VERSION = '11.16.1'
MERMAID_SHA256 = '18327bef70d96fb505fe7287d9f6a7362ebf07ff6576ddfaffb1a06f3e1a2954'
MERMAID_URL = f'https://registry.npmjs.org/mermaid/-/mermaid-{MERMAID_VERSION}.tgz'
MERMAID_FILE = os.path.join(HOME, 'vendor', f'mermaid-{MERMAID_VERSION}.min.js')


# ---------------------------------------------------------------- binaries

def find_bin(name):
    local = os.path.join(BIN, name)
    if os.access(local, os.X_OK):
        return local
    return shutil.which(name)


def run(cmd, **kw):
    kw.setdefault('capture_output', True)
    kw.setdefault('text', True)
    return subprocess.run(cmd, **kw)


def arch():
    m = platform.machine().lower()
    return {'x86_64': 'amd64', 'amd64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(m, m)


def latest_asset(repo, pattern):
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/latest',
                                 headers={'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rel = json.load(r)
    for a in rel.get('assets', []):
        if re.fullmatch(pattern, a['name']):
            return rel['tag_name'], a['browser_download_url']
    raise RuntimeError(f'no release asset matching {pattern} in {repo}')


def download(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def write_file(path, data, mode=0o600):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + '.tmp', 'wb') as fh:
        fh.write(data)
    os.chmod(path + '.tmp', mode)
    os.replace(path + '.tmp', path)


def install_binary(name):
    if platform.system() != 'Linux':
        raise RuntimeError(f'please install {name} yourself on {platform.system()}')
    a = arch()
    if name == 'ghq':
        tag, url = latest_asset('x-motemen/ghq', rf'ghq_linux_{a}\.zip')
        with zipfile.ZipFile(io.BytesIO(download(url))) as z:
            data = z.read(next(n for n in z.namelist() if n.endswith('/ghq')))
    else:
        tag, url = latest_asset('cli/cli', rf'gh_[\d.]+_linux_{a}\.tar\.gz')
        with tarfile.open(fileobj=io.BytesIO(download(url)), mode='r:gz') as tz:
            member = next(m for m in tz.getmembers() if m.name.endswith('/bin/gh'))
            data = tz.extractfile(member).read()
    write_file(os.path.join(BIN, name), data, 0o755)
    return tag


def install_mermaid():
    """Download the pinned Mermaid build and keep it only if its SHA-256 matches."""
    local = os.environ.get('REPO_VIEWER_MERMAID_FILE')  # offline / test source
    if local:
        data = open(local, 'rb').read()
    else:
        with tarfile.open(fileobj=io.BytesIO(download(MERMAID_URL)), mode='r:gz') as tz:
            data = tz.extractfile('package/dist/mermaid.min.js').read()
    if hashlib.sha256(data).hexdigest() != MERMAID_SHA256:
        raise RuntimeError('checksum mismatch; the file was not installed')
    write_file(MERMAID_FILE, data)


def mermaid_ok():
    try:
        with open(MERMAID_FILE, 'rb') as fh:
            return hashlib.sha256(fh.read()).hexdigest() == MERMAID_SHA256
    except OSError:
        return False


def gh(*args, **kw):
    exe = find_bin('gh')
    if not exe:
        raise SystemExit('gh not installed: run `repo_viewer.py setup` first')
    return run([exe, *args], **kw)


def signed_in_user():
    if not find_bin('gh'):
        return None
    r = gh('api', 'user', '--jq', '.login')
    return r.stdout.strip() if r.returncode == 0 else None


# ---------------------------------------------------------------- language

def normalize_lang(value):
    v = (value or '').strip().lower().replace('_', '-')
    if v.startswith('ja'):
        return 'ja'
    if v.startswith('zh'):
        return 'zh-CN'
    if v.startswith('ko'):
        return 'ko'
    if v.startswith('en'):
        return 'en'
    return ''  # unsupported or unknown: the page follows the browser language


def page_lang():
    try:
        return open(LANG_FILE).read().strip()
    except OSError:
        return ''


# ---------------------------------------------------------------- commands

def cmd_setup(args):
    os.makedirs(HOME, exist_ok=True)
    failed = False
    for name in ('ghq', 'gh'):
        if find_bin(name):
            print(f'{name}: ok')
        else:
            try:
                print(f'{name}: installed {install_binary(name)}')
            except Exception as e:
                print(f'{name}: FAILED to install ({e})')
                failed = True
    if mermaid_ok():
        print('mermaid: ok')
    else:
        try:
            install_mermaid()
            print(f'mermaid: installed {MERMAID_VERSION} (verified)')
        except Exception as e:  # optional: diagrams fall back to source
            print(f'mermaid: not installed ({e}); diagrams will be shown as source')
    # --lang sets the page's initial language (the Muse user's language); `auto` means "follow the
    # browser". Viewers can always change it in the page's settings.
    if '--lang' in args:
        i = args.index('--lang')
        lang = normalize_lang(args[i + 1] if i + 1 < len(args) else '')
        with open(LANG_FILE, 'w') as fh:
            fh.write(lang)
    lang = page_lang()
    print(f'page language: {lang or "browser setting"}')
    if not failed:
        with open(SETUP_MARKER, 'w') as fh:
            fh.write(SETUP_VERSION)
    user = signed_in_user()
    print(f'github: signed in as {user}' if user
          else 'github: not signed in -> next: repo_viewer.py login')
    return 1 if failed else 0


def cmd_login(args):
    user = signed_in_user()
    if user:
        gh('auth', 'setup-git')
        print(f'already signed in as {user}')
        return 0
    log = os.path.join(HOME, '.login.log')
    if args and args[0] == '--wait':
        deadline = time.time() + 900
        while time.time() < deadline:
            user = signed_in_user()
            if user:
                gh('auth', 'setup-git')
                print(f'signed in as {user}; git configured for HTTPS')
                return 0
            time.sleep(3)
        print('timed out waiting for approval; run `repo_viewer.py login` again')
        return 1
    os.makedirs(HOME, exist_ok=True)
    out = open(log, 'w')
    env = dict(os.environ, GH_BROWSER='true', BROWSER='true', GH_PROMPT_DISABLED='1')
    subprocess.Popen([find_bin('gh'), 'auth', 'login', '--hostname', 'github.com',
                      '--git-protocol', 'https', '--web', '--skip-ssh-key'],
                     stdin=subprocess.DEVNULL, stdout=out, stderr=out, env=env,
                     start_new_session=True)
    code = None
    for _ in range(40):
        time.sleep(0.5)
        m = re.search(r'\b([A-Z0-9]{4}-[A-Z0-9]{4})\b', open(log).read())
        if m:
            code = m.group(1)
            break
    if not code:
        tail = [ln for ln in open(log).read().splitlines() if ln.strip()][-2:]
        print('could not get a device code: ' + (' / '.join(tail) or 'no output from gh'))
        return 1
    print(f'Open https://github.com/login/device and enter: {code}')
    print('Then run: repo_viewer.py login --wait')
    return 0


def ghq_root():
    if os.environ.get('GHQ_ROOT'):
        return os.environ['GHQ_ROOT']
    exe = find_bin('ghq')
    if exe:
        r = run([exe, 'root'])
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return os.path.expanduser('~/ghq')


def cloned_ids():
    return {rid for rid, _ in update_snapshot.find_repos(ghq_root())}


def cmd_list(args):
    me = signed_in_user()
    if not me:
        print('not signed in: run `repo_viewer.py login`')
        return 1
    show_all = '--all' in args
    have = cloned_ids()
    owners = [me] + gh('api', 'user/orgs', '--jq', '.[].login').stdout.split()
    total = 0
    for owner in owners:
        r = gh('repo', 'list', owner, '--limit', '1000',
               '--json', 'nameWithOwner,isArchived,isPrivate,isFork')
        if r.returncode != 0:
            print(f'{owner}: cannot list ({r.stderr.strip()[:80]})')
            continue
        for repo in sorted(json.loads(r.stdout), key=lambda x: x['nameWithOwner'].lower()):
            if repo['isArchived'] and not show_all:
                continue
            flags = [f for f, on in (('private', repo['isPrivate']), ('fork', repo['isFork']),
                                     ('archived', repo['isArchived']),
                                     ('cloned', repo['nameWithOwner'] in have)) if on]
            print(repo['nameWithOwner'] + (f'  [{",".join(flags)}]' if flags else ''))
            total += 1
    print(f'-- {total} repositories' + ('' if show_all else ' (archived hidden; --all to show)'))
    if total == 0:
        print(f'no repositories available; the sample repository can be used: '
              f'repo_viewer.py clone {SAMPLE_REPO}')
    return 0


def install_hooks():
    r = run(['sh', os.path.join(TOOLS, 'install-hooks.sh')],
            env=dict(os.environ, GHQ_ROOT=ghq_root()))
    if r.returncode != 0:
        print((r.stdout + r.stderr).strip())
    return r.returncode


def cmd_clone(args):
    if not args:
        print('usage: repo_viewer.py clone OWNER/REPO ...')
        return 2
    exe = find_bin('ghq')
    if not exe:
        raise SystemExit('ghq not installed: run `repo_viewer.py setup` first')
    have, ok, bad = cloned_ids(), 0, 0
    for rid in args:
        if rid in have:
            ok += 1
            continue
        r = run([exe, 'get', '--silent', rid])
        if r.returncode == 0:
            ok += 1
        else:
            bad += 1
            print(f'FAILED {rid}: {(r.stderr.strip().splitlines() or ["?"])[-1][:120]}')
    install_hooks()
    print(f'cloned: {ok} ok, {bad} failed; repositories in total: {len(cloned_ids())}')
    return 1 if bad else 0


# ---------------------------------------------------------------- page build
#
# dist/site/                  "folder" form (preferred): small files, loaded on demand
#   index.html                page (language baked in)
#   data/index.json.gz        repository list and file tree, no file content
#   data/<repo-key>.json.gz   file content of one repository, loaded when it is opened
#   data/mermaid.js.gz        Mermaid, loaded only when a diagram is shown
# dist/viewer.html          "single-file" form: the same data embedded (base64 gzip)

def repo_key(repo_id):
    slug = re.sub(r'[^a-z0-9._-]+', '-', repo_id.lower().replace('/', '--')).strip('-')
    return f'{slug[:60]}-{hashlib.sha1(repo_id.encode()).hexdigest()[:6]}'


def gz(data):
    return gzip.compress(data, compresslevel=9, mtime=0)  # deterministic bytes


def page_html():
    with open(TEMPLATE, encoding='utf-8') as fh:
        tpl = fh.read()
    tag = '<html lang="en" data-lang="">'
    assert tag in tpl, 'page template is missing the <html> tag marker'
    lang = page_lang()
    return tpl.replace(tag, f'<html lang="{lang or "en"}" data-lang="{lang}">')


def build_files():
    """Return {relative path: bytes} for the folder form."""
    with open(os.path.join(HOME, 'snapshot.json'), encoding='utf-8') as fh:
        snap = json.load(fh)
    files = {'index.html': page_html().encode('utf-8')}
    index = {'generated_at': snap['generated_at'], 'repos': []}
    for r in snap['repos']:
        key = repo_key(r['id'])
        content = {f['path']: f['content'] for f in r['files'] if 'content' in f}
        files[f'data/{key}.json.gz'] = gz(json.dumps(content, ensure_ascii=False,
                                                     separators=(',', ':')).encode('utf-8'))
        index['repos'].append({
            'id': r['id'], 'key': key, 'branch': r['branch'], 'head': r['head'],
            'committed_at': r.get('committed_at', ''), 'local': r.get('local', ''),
            # [path, size, skipped-reason or 0]
            'files': [[f['path'], f['size'], f.get('skipped', 0)] for f in r['files']],
        })
    # Keep the previous timestamp when nothing changed, so an unchanged build is byte-identical
    # and `refresh` can report UP_TO_DATE.
    try:
        with gzip.open(os.path.join(SITE, 'data', 'index.json.gz'), 'rt', encoding='utf-8') as fh:
            old = json.load(fh)
        if old.get('repos') == index['repos']:
            index['generated_at'] = old['generated_at']
    except (OSError, ValueError, KeyError):
        pass
    files['data/index.json.gz'] = gz(json.dumps(index, ensure_ascii=False,
                                                separators=(',', ':')).encode('utf-8'))
    if mermaid_ok():
        with open(MERMAID_FILE, 'rb') as fh:
            files['data/mermaid.js.gz'] = gz(fh.read())
    return files


def single_file_html(files):
    html = files['index.html'].decode('utf-8')
    blobs = ''.join(
        f'<script type="application/octet-stream" data-file="{name}">'
        f'{base64.b64encode(data).decode("ascii")}</script>\n'
        for name, data in sorted(files.items()) if name.startswith('data/'))
    marker = '<!-- embedded-data -->'
    assert marker in html, 'page template is missing the embedded-data marker'
    return html.replace(marker, blobs)


def build_page():
    with open(os.path.join(HOME, '.build.lock'), 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        files = build_files()
        tmp = SITE + '.tmp'
        shutil.rmtree(tmp, ignore_errors=True)
        for name, data in files.items():
            write_file(os.path.join(tmp, name), data)
        os.makedirs(DIST, exist_ok=True)
        os.chmod(DIST, 0o700)
        shutil.rmtree(SITE, ignore_errors=True)
        os.replace(tmp, SITE)
        write_file(SINGLE, single_file_html(files).encode('utf-8'))
        for old in ('index.html', 'snapshot.json'):  # outputs of earlier versions
            if os.path.exists(os.path.join(DIST, old)):
                os.unlink(os.path.join(DIST, old))
    return files


def file_hashes():
    out = {}
    for base, _, names in os.walk(SITE):
        for n in names:
            p = os.path.join(base, n)
            with open(p, 'rb') as fh:
                out[os.path.relpath(p, SITE)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def legacy_state():
    """Map the state of an older installation, so that its existing space is updated in place.

    Older versions uploaded index.html + snapshot.json ("two-file") or viewer.html. Every file
    of the current build is reported as changed, and the old snapshot.json is reported for
    deletion.
    """
    try:
        old = open(os.path.join(HOME, '.page-mode')).read().strip()
    except OSError:
        return {}
    if old == 'single-file':
        return {'mode': 'single-file', 'files': {}}
    return {'mode': 'folder', 'files': {'snapshot.json': 'legacy', 'index.html': 'legacy'}}


def load_state():
    try:
        with open(STATE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def snapshot(pull):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = update_snapshot.main(['--quiet'] + ([] if pull else ['--no-pull']))
    return rc, buf.getvalue()


def cmd_build(args):
    rc, _ = snapshot(pull=False)
    if rc == 0:
        build_page()
    return rc


def no_repositories():
    print('NO_REPOSITORIES: clone at least one repository first.')
    print(f'If none can be chosen, the sample can be used: repo_viewer.py clone {SAMPLE_REPO}')
    return 3


def refresh_state(pull=True):
    """Pull, rebuild and compare with the space. Prints only problems and one stats line.

    Returns (status, info): status is NO_REPOSITORIES, ERROR, FIRST_TIME, UPDATE or UP_TO_DATE.
    """
    if not cloned_ids():
        return 'NO_REPOSITORIES', {}
    install_hooks()
    rc, out = snapshot(pull=pull)
    for line in out.splitlines():
        if 'pull failed' in line or line.startswith('refusing'):
            print(line)
    if rc != 0:
        return 'ERROR', {'rc': rc}
    build_page()
    with open(os.path.join(HOME, 'snapshot.json'), encoding='utf-8') as fh:
        snap = json.load(fh)
    now = file_hashes()
    total = sum(os.path.getsize(os.path.join(SITE, p)) for p in now)
    print(f'repos: {len(snap["repos"])}, files: {sum(len(r["files"]) for r in snap["repos"])}, '
          f'page data: {total / 1024 / 1024:.1f} MB' + ('' if mermaid_ok() else ', diagrams: off'))
    state = load_state() or legacy_state()
    mode, synced = state.get('mode'), state.get('files', {})
    info = {'mode': mode, 'repos': len(snap['repos']),
            'changed': sorted(p for p in now if synced.get(p) != now[p]),
            'removed': sorted(p for p in synced if p not in now)}
    if not mode:
        return 'FIRST_TIME', info
    if info['changed'] or info['removed']:
        return 'UPDATE', info
    return 'UP_TO_DATE', info


def print_upload(info):
    if info['mode'] == 'single-file':
        print(f'replace the page file in the space with: {SINGLE}')
        return
    print(f'upload to the space (paths relative to {SITE}/):')
    for p in info['changed']:
        print(f'  {p}')
    if info['removed']:
        print('delete from the space:')
        for p in info['removed']:
            print(f'  {p}')


def print_first_time():
    print('create a private space from either')
    print(f'  folder (preferred): every file under {SITE}/ (keep the data/ folder)')
    print(f'  single file:        {SINGLE}')


def cmd_refresh(args):
    status, info = refresh_state(pull='--no-pull' not in args)
    if status == 'NO_REPOSITORIES':
        return no_repositories()
    if status == 'ERROR':
        return info['rc']
    if status == 'UP_TO_DATE':
        print('UP_TO_DATE: the space already shows this build. Nothing to do.')
        return 0
    print('PAGE_UPDATE_NEEDED')
    if status == 'FIRST_TIME':
        print_first_time()
        print('then run: repo_viewer.py mark-synced --mode folder   (or --mode single-file)')
        return 0
    print_upload(info)
    print('then run: repo_viewer.py mark-synced')
    return 0


def cmd_next(args):
    """Print the single next action for the agent. Repeat until it prints DONE."""
    C = 'python3 ' + os.path.join(TOOLS, 'repo_viewer.py').replace(os.path.expanduser('~'), '~', 1)
    again = f'Then run `{C} next` again.'
    lang_note = " Speak to the user in their usual language, not in English unless that is theirs."
    try:
        setup_current = open(SETUP_MARKER).read().strip() == SETUP_VERSION
    except OSError:
        setup_current = False
    if os.path.exists(LANG_FILE) and find_bin('ghq') and find_bin('gh') and not setup_current:
        print(f'NEXT (1/5 install): the tool was updated; run `{C} setup` (the page language is kept). '
              + again)
        return 0
    if not (find_bin('ghq') and find_bin('gh')) or not os.path.exists(LANG_FILE):
        print(f'NEXT (1/5 install): run `{C} setup --lang LANG`. LANG is the language this user '
              'normally uses with you (en, ja, zh-CN or ko; auto for any other language). Judge it from '
              'your conversations with the user, not from the setup request, which is written in English. '
              + again)
        return 0
    has_repos = bool(cloned_ids())
    if not has_repos and not signed_in_user():
        print(f'NEXT (2/5 sign in): run `{C} login` and show the user the URL and the code exactly '
              f'as printed. Then run `{C} login --wait`; it returns after the user approves. '
              'If the user does not want to sign in, ask whether to use the sample repository instead; '
              f'if they agree, run `{C} clone {SAMPLE_REPO}`. ' + again + lang_note)
        return 0
    if not has_repos:
        print(f'NEXT (3/5 repositories): run `{C} list` and show the user the result. Ask which '
              'repositories to include (at least one; answers like "all private ones" are fine), then '
              f'run `{C} clone OWNER/REPO ...`. If none can be chosen, ask whether to include the sample '
              f'repository; if the user agrees, run `{C} clone {SAMPLE_REPO}`. ' + again + lang_note)
        return 0
    status, info = refresh_state()
    if status == 'ERROR':
        print('STOP: the snapshot could not be built (see the lines above). Report them to the user.')
        return info['rc']
    if status == 'FIRST_TIME':
        print('NEXT (4/5 create the space): upload the files below unchanged, by path, without '
              'opening them, to a new private Muse space named "Repository Viewer" in the '
              "user's language. Never create a public link.")
        print_first_time()
        print(f'Then run `{C} mark-synced --mode folder` (or `--mode single-file`). ' + again)
        return 0
    if status == 'UPDATE':
        print('NEXT (5/5 update the space): change only these files in the space, by path, without '
              'opening them.')
        print_upload(info)
        print(f'Then run `{C} mark-synced`. ' + again)
        return 0
    user = signed_in_user()
    print(f'DONE: the space is up to date ({info["repos"]} repositories'
          + (f', GitHub account {user}' if user else '') + ').')
    print('Tell the user in at most 3 lines, in their usual language: the account, the number of '
          'repositories, and the space. Remember for later: when the user asks to refresh the '
          f'viewer, run `git -C {os.path.dirname(TOOLS)} pull --ff-only`, then repeat '
          f'`{C} next` until it prints DONE. When the user sends a question from the viewer, it '
          'contains a `git -C ... show ...` command: run it to read exactly those lines from the local '
          'clone instead of asking for the code.')
    if not os.path.exists(STAR_NOTE):
        print('This time only, end with one short line in the same language: if the viewer is '
              f'useful, a star on GitHub is welcome (https://github.com/{SAMPLE_REPO}). Do not star '
              'the repository for the user.')
        write_file(STAR_NOTE, b'1')
    return 0


def cmd_mark_synced(args):
    state = load_state() or {k: v for k, v in legacy_state().items() if k == 'mode'}
    if '--mode' in args:
        i = args.index('--mode')
        mode = args[i + 1] if i + 1 < len(args) else ''
        if mode not in ('folder', 'single-file'):
            print('--mode must be folder or single-file')
            return 2
        state['mode'] = mode
    elif not state.get('mode'):
        print('first time: add --mode folder or --mode single-file')
        return 2
    if not os.path.isdir(SITE):
        print('nothing built yet: run refresh first')
        return 1
    if not state.get('mode'):
        state['mode'] = legacy_state().get('mode')
    state['files'] = file_hashes()
    write_file(STATE, json.dumps(state, indent=1, sort_keys=True).encode())
    for name in LEGACY_STATE:  # migrated; no longer needed
        if os.path.exists(os.path.join(HOME, name)):
            os.unlink(os.path.join(HOME, name))
    dirty = os.path.join(HOME, '.snapshot-dirty')
    if os.path.exists(dirty):
        os.unlink(dirty)
    print(f'marked as synced ({state["mode"]})')
    return 0


def cmd_status(args):
    parts = [f'ghq:{"ok" if find_bin("ghq") else "missing"}',
             f'gh:{"ok" if find_bin("gh") else "missing"}',
             f'mermaid:{"ok" if mermaid_ok() else "missing"}',
             f'lang:{page_lang() or "browser"}',
             f'user:{signed_in_user() or "-"}',
             f'clones:{len(cloned_ids())}']
    state = load_state()
    if os.path.isdir(SITE):
        same = state.get('files') == file_hashes()
        parts.append(f'space:{"up-to-date" if same and state.get("mode") else "needs-update"}')
    else:
        parts.append('build:none')
    parts.append(f'mode:{state.get("mode", "-")}')
    print(' '.join(parts))
    return 0


COMMANDS = {
    'next': cmd_next, 'setup': cmd_setup, 'login': cmd_login, 'list': cmd_list, 'clone': cmd_clone,
    'refresh': cmd_refresh, 'build': cmd_build, 'mark-synced': cmd_mark_synced,
    'status': cmd_status,
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    os.environ.setdefault('GHQ_ROOT', ghq_root())
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    return COMMANDS[argv[0]](argv[1:]) or 0


if __name__ == '__main__':
    sys.exit(main())
