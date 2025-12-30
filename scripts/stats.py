import requests
import json
import os
import re

USERNAME = "mk-runner"
GITHUB_API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}"
}

def get_repos():
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"{GITHUB_API}/users/{USERNAME}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page}
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_commit_count(repo):
    url = f"{GITHUB_API}/repos/{USERNAME}/{repo}/commits"
    r = requests.get(url, headers=HEADERS, params={"per_page": 1})
    r.raise_for_status()

    link = r.headers.get("Link")
    if not link:
        return len(r.json()) if isinstance(r.json(), list) else 0

    match = re.search(r'page=(\d+)>; rel="last"', link)
    return int(match.group(1)) if match else 0

def main():
    repos = get_repos()

    total_stars = 0
    total_forks = 0
    total_commits = 0
    total_downloads = 0

    for repo in repos:
        name = repo["name"]

        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)

        # commits (default branch)
        total_commits += get_commit_count(name)

        # release downloads
        releases_url = repo.get("releases_url", "").replace("{/id}", "")
        if releases_url:
            releases = requests.get(releases_url, headers=HEADERS).json()
            if isinstance(releases, list):
                for r in releases:
                    for asset in r.get("assets", []):
                        total_downloads += asset.get("download_count", 0)

    badge = {
        "schemaVersion": 1,
        "label": "GitHub Total",
        "message": (
            f"⭐ {total_stars}  "
            f"🍴 {total_forks}  "
            f"🧮 {total_commits}  "
            f"⬇️ {total_downloads}"
        ),
        "color": "blue"
    }

    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
