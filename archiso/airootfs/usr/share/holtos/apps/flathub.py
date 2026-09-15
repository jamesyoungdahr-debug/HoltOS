"""Flathub web API client for HoltOS Apps: collections, categories, search, app details, permission warnings and cached media. Standard library only, so it runs in worker threads. Every response is cached on disk; when the network is down the last cached copy is used."""

import hashlib
from html.parser import HTMLParser
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request


BASE = "https://flathub.org/api/v2"
CACHE_ROOT = os.path.join(os.path.expanduser("~"), ".cache", "holtos-apps")
API_CACHE = os.path.join(CACHE_ROOT, "api")
MEDIA_CACHE = os.path.join(CACHE_ROOT, "media")
MEDIA_HOSTS = ("dl.flathub.org", "flathub.org")
USER_AGENT = "HoltOS-Apps/1.0"
APP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,254}$")
COLLECTIONS = ("popular", "trending", "recently-updated", "recently-added", "verified")
CATEGORIES = [
    ("AudioVideo", "Audio & Video"),
    ("Game", "Games"),
    ("Network", "Internet"),
    ("Graphics", "Graphics & Photography"),
    ("Office", "Productivity"),
    ("Development", "Developer Tools"),
    ("Education", "Education"),
    ("Science", "Science"),
    ("System", "System"),
    ("Utility", "Utilities"),
]


class FlathubError(Exception):
    """Raised when Flathub cannot be reached and nothing is cached, or on bad input."""


def _get_json(path, ttl=3600, body=None):
    key = hashlib.sha1((path + "|" + json.dumps(body, sort_keys=True)).encode()).hexdigest()
    cache_file = os.path.join(API_CACHE, f"{key}.json")

    if os.path.isfile(cache_file):
        mtime = os.path.getmtime(cache_file)
        if time.time() - mtime < ttl:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

    url = BASE + path
    headers = {"User-Agent": USER_AGENT}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
    except (urllib.error.URLError, OSError, ValueError) as e:
        if os.path.isfile(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        raise FlathubError(f"Flathub could not be reached: {e}") from e

    tmp = cache_file + ".tmp"
    os.makedirs(API_CACHE, exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(json.loads(raw), f)
    os.replace(tmp, cache_file)
    return json.loads(raw)


def _app_from_hit(hit):
    """Convert a Flathub search/collection hit dict to our app summary."""
    return {
        "id": hit.get("app_id") or "",
        "name": hit.get("name") or hit.get("app_id") or "",
        "summary": hit.get("summary") or "",
        "icon": hit.get("icon") or "",
        "developer": hit.get("developer_name") or "",
        "verified": bool(hit.get("verification_verified")),
        "license": hit.get("project_license") or "",
        "free": bool(hit.get("is_free_license")),
    }


def collection(name, page=1, per_page=24):
    """Return a list of app dicts from a named Flathub collection."""
    if name not in COLLECTIONS:
        raise FlathubError(f"Unknown collection: {name}")
    data = _get_json(f"/collection/{name}?page={int(page)}&per_page={int(per_page)}")
    return [_app_from_hit(h) for h in data.get("hits", []) if h.get("app_id")]


def category(name, page=1, per_page=48):
    """Return a list of app dicts from a Flathub category."""
    valid_keys = [c[0] for c in CATEGORIES]
    if name not in valid_keys:
        raise FlathubError(f"Unknown category: {name}")
    data = _get_json(f"/collection/category/{name}?page={int(page)}&per_page={int(per_page)}")
    return [_app_from_hit(h) for h in data.get("hits", []) if h.get("app_id")]


def search(query):
    """Search Flathub and return a list of app dicts."""
    q = query.strip()[:100]
    if not q:
        return []
    data = _get_json("/search", ttl=600, body={"query": q})
    return [_app_from_hit(h) for h in data.get("hits", []) if h.get("app_id")]


class _TextParser(HTMLParser):
    """Collect plain text from HTML markup."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "li", "ul", "ol", "br"):
            self._parts.append("\n")
        if tag == "li":
            self._parts.append("• ")

    def handle_endtag(self, tag):
        if tag in ("p", "ul", "ol"):
            self._parts.append("\n")

    def handle_data(self, data):
        # Line breaks inside the markup are only source formatting; the tags
        # above decide where real line breaks go.
        self._parts.append(data.replace("\n", " "))

    def text(self):
        """Return cleaned plain text."""
        raw = "".join(self._parts)
        lines = []
        for line in raw.split("\n"):
            line = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(line)
        collapsed = "\n".join(lines)
        collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
        return collapsed.strip()


def _plain(markup):
    """Convert HTML markup to plain text."""
    if not markup:
        return ""
    p = _TextParser(convert_charrefs=True)
    p.feed(markup)
    return p.text()


def _screenshot_url(shot, target=752):
    """Pick the best screenshot URL closest to *target* width."""
    sizes = shot.get("sizes") or []
    if not sizes:
        return ""
    best = None
    best_diff = None
    for s in sizes:
        try:
            w = int(s["width"])
        except (KeyError, ValueError, TypeError):
            continue
        diff = abs(w - target)
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best = s.get("src") or ""
    return best


def _date(stamp):
    """Convert a Unix timestamp to YYYY-MM-DD, or '' on failure."""
    try:
        return time.strftime("%Y-%m-%d", time.gmtime(int(stamp)))
    except (TypeError, ValueError, OSError):
        return ""


def details(app_id):
    """Return full detail dict for an app by its ID."""
    if not APP_ID.match(app_id or ""):
        raise FlathubError("bad app id")
    quoted = urllib.parse.quote(app_id, safe=".-_")
    store = _get_json(f"/appstream/{quoted}")
    try:
        summary = _get_json(f"/summary/{quoted}")
    except FlathubError:
        summary = {}

    meta = summary.get("metadata") or {}
    urls = store.get("urls") or {}

    releases = []
    for r in (store.get("releases") or [])[:5]:
        releases.append({
            "version": r.get("version") or "",
            "date": _date(r.get("timestamp")),
            "notes": _plain(r.get("description") or ""),
        })

    return {
        "id": app_id,
        "name": store.get("name") or app_id,
        "summary": store.get("summary") or "",
        "description": _plain(store.get("description") or ""),
        "developer": store.get("developer_name") or "",
        "license": store.get("project_license") or "",
        "free": bool(store.get("is_free_license")),
        "icon": store.get("icon") or "",
        "screenshots": [u for u in (_screenshot_url(s) for s in (store.get("screenshots") or [])[:8]) if u],
        "homepage": urls.get("homepage") or "",
        "bugtracker": urls.get("bugtracker") or "",
        "donation": urls.get("donation") or "",
        "download_size": int(summary.get("download_size") or 0),
        "installed_size": int(summary.get("installed_size") or 0),
        "runtime": meta.get("runtime") or "",
        "runtime_eol": bool(meta.get("runtimeIsEol")),
        "permissions": meta.get("permissions") or {},
        "releases": releases,
        "eol": bool(store.get("is_eol")),
    }


def permission_warnings(perms):
    """Return a list of short plain-English permission warning strings."""
    warnings = []

    fs = perms.get("filesystems") or []
    for entry in fs:
        base, _, mode = entry.partition(":")
        ro = mode == "ro"
        if base in ("host",):
            if ro:
                warnings.append("Can read all your files")
            else:
                warnings.append("Can read and change all your files and system folders")
        elif base in ("host-os", "host-etc"):
            if ro:
                warnings.append("Can see system folders")
            else:
                warnings.append("Can read and change all your files and system folders")
        elif base in ("home", "~"):
            if ro:
                warnings.append("Can read your home folder")
            else:
                warnings.append("Can read and change everything in your home folder")
        elif base.startswith("xdg-download"):
            warnings.append("Can use your Downloads folder")
        elif base == "xdg-videos":
            warnings.append("Can use your Videos folder")
        elif base == "xdg-music":
            warnings.append("Can use your Music folder")
        elif base == "xdg-pictures":
            warnings.append("Can use your Pictures folder")
        elif base == "xdg-documents":
            warnings.append("Can use your Documents folder")

    devices = perms.get("devices") or []
    if "all" in devices:
        warnings.append("Can use all devices, such as webcams, microphones and controllers")

    shared = perms.get("shared") or []
    if "network" in shared:
        warnings.append("Uses the internet")

    sockets = perms.get("sockets") or []
    if "system-bus" in sockets:
        warnings.append("Full access to system services")
    if "session-bus" in sockets:
        warnings.append("Full access to your desktop session")
    if "x11" in sockets and "wayland" not in sockets:
        warnings.append("Uses the older X11 display, which isolates apps less")
    if "ssh-auth" in sockets:
        warnings.append("Can use your SSH keys")

    talk = (perms.get("session-bus") or {}).get("talk") or []
    if "org.freedesktop.Flatpak" in talk:
        warnings.append("Can run programs outside its sandbox")
    for name in talk:
        if name.startswith("org.freedesktop.secrets") or name.startswith("org.kde.kwalletd"):
            warnings.append("Can use your saved passwords (keyring)")
            break

    seen = set()
    deduped = []
    for w in warnings:
        if w not in seen:
            seen.add(w)
            deduped.append(w)
    return deduped


def fetch_media(url):
    """Download and cache a media file from an allowed host, returning the local path or None."""
    parsed = urllib.parse.urlparse(url or "")
    if parsed.scheme != "https" or parsed.hostname not in MEDIA_HOSTS:
        return None

    ext = os.path.splitext(parsed.path)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        ext = ".img"

    path = os.path.join(MEDIA_CACHE, hashlib.sha1(url.encode()).hexdigest() + ext)
    if os.path.isfile(path):
        return path

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            return None
    except (urllib.error.URLError, OSError, ValueError):
        return None

    tmp = path + ".tmp"
    os.makedirs(MEDIA_CACHE, exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(raw)
    os.replace(tmp, path)
    return path


def human_size(count):
    """Return a human-readable size string like '52.7 MB', or '' for 0/None."""
    if not count:
        return ""
    count = int(count)
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f} GB"
    elif count >= 1_000_000:
        return f"{count / 1_000_000:.1f} MB"
    elif count >= 1_000:
        return f"{count // 1_000} KB"
    else:
        return f"{count} B"


if __name__ == "__main__":
    print(collection("popular", per_page=3))
    d = details("org.videolan.VLC")
    print(d["name"], human_size(d["download_size"]), permission_warnings(d["permissions"]), d["screenshots"][:1])
