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

BADGE_DIR = "badges"
os.makedirs(BADGE_DIR, exist_ok=True)
COLORS = {
    "stars": "#2f80ed",      # academic blue
    "forks": "#6f42c1",      # deep purple
    "commits": "#0f766e",    # deep teal
    "downloads": "#475569"  # neutral gray
}

def get_all_repos():
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

def get_commit_count(repo_name):
    """
    Count commits on default branch using GitHub pagination header.
    """
    url = f"{GITHUB_API}/repos/{USERNAME}/{repo_name}/commits"
    r = requests.get(url, headers=HEADERS, params={"per_page": 1})
    r.raise_for_status()

    link = r.headers.get("Link")
    if not link:
        return len(r.json()) if isinstance(r.json(), list) else 0

    match = re.search(r'page=(\d+)>; rel="last"', link)
    return int(match.group(1)) if match else 0

def write_badge(name, label, value, color):
    badge = {
        "schemaVersion": 1,
        "label": label,
        "message": str(value),
        "color": color
    }
    path = os.path.join(BADGE_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)

def main():
    os.makedirs(BADGE_DIR, exist_ok=True)

    repos = get_all_repos()

    total_stars = 0
    total_forks = 0
    total_commits = 0
    total_downloads = 0

    for repo in repos:
        name = repo["name"]

        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)

        # commits (default branch only)
        total_commits += get_commit_count(name)

        # release downloads
        releases_url = repo.get("releases_url", "").replace("{/id}", "")
        if releases_url:
            releases = requests.get(releases_url, headers=HEADERS).json()
            if isinstance(releases, list):
                for r in releases:
                    for asset in r.get("assets", []):
                        total_downloads += asset.get("download_count", 0)

    # write badges
    write_badge("stars", "Stars", total_stars, COLORS["stars"])
    write_badge("forks", "Forks", total_forks, COLORS["forks"])
    write_badge("commits", "Commits", total_commits, COLORS["commits"])
    write_badge("downloads", "Downloads", total_downloads, COLORS["downloads"])

if __name__ == "__main__":
    main()
