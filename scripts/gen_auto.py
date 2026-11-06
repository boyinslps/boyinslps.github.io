#!/usr/bin/env python3
"""掃描 GitHub 帳號下有開 Pages 的 repo，產生 auto.json 給總覽頁讀取。

- 排除：總覽頁自己、非公開、沒開 Pages、帶有 topic「no-index」的 repo。
- repo 根目錄若有 site.json（[{"t":"標題","d":"說明","u":"子路徑/"}, ...]），
  就把裡面列的子頁面一併收進來；沒有的話只收 repo 首頁。
- 已經放在 index.html 固定清單的網址，由 index.html 在瀏覽時自動略過。

made by 資訊老師黃博胤
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

OWNER = os.environ.get("OWNER", "boyinslps")
SELF = f"{OWNER}.github.io"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
GENERIC_DESC = re.compile(r"^(?:-|\?+.*|由 EZPage 建立的網站.*)$")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gen-auto"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def list_repos():
    repos, page = [], 1
    while True:
        batch = json.loads(get(
            f"https://api.github.com/users/{OWNER}/repos?per_page=100&page={page}"))
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def title_and_desc(repo):
    desc = (repo.get("description") or "").strip()
    if not desc or GENERIC_DESC.match(desc):
        return repo["name"], ""
    m = re.match(r"^(.{1,30}?)[:：](.*)$", desc)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return (desc, "") if len(desc) <= 30 else (repo["name"], desc)


def site_json(repo):
    url = (f"https://raw.githubusercontent.com/{OWNER}/{repo['name']}/"
           f"{repo['default_branch']}/site.json")
    try:
        pages = json.loads(get(url))
    except (urllib.error.URLError, ValueError):
        return None
    out = []
    for p in pages if isinstance(pages, list) else []:
        if isinstance(p, dict) and p.get("t") and p.get("u") is not None:
            out.append({"t": str(p["t"]), "d": str(p.get("d", "")),
                        "u": f"{repo['name']}/{str(p['u']).lstrip('/')}"})
    return out or None


def main():
    result = []
    for repo in sorted(list_repos(), key=lambda r: r["pushed_at"], reverse=True):
        if (repo["name"] == SELF or repo["private"] or not repo["has_pages"]
                or "no-index" in repo.get("topics", [])):
            continue
        title, desc = title_and_desc(repo)
        pages = site_json(repo)
        result.append({
            "repo": repo["name"],
            "title": title,
            "desc": desc,
            "explicit": pages is not None,
            "pages": pages or [{"t": title, "d": desc, "u": f"{repo['name']}/"}],
        })
    json.dump(result, sys.stdout if "--stdout" in sys.argv else open("auto.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(result)} repos", file=sys.stderr)


if __name__ == "__main__":
    main()
