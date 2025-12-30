import requests
import json

USERNAME = "mk-runner"
GITHUB_API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json"
}

def get_repos():
    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"{GITHUB_API}/users/{USERNAME}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page}
        )
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def main():
    repos = get_repos()

    total_stars = 0
    total_downloads = 0

    for repo in repos:
        total_stars += repo.get("stargazers_count", 0)

        releases_url = repo.get("releases_url", "").replace("{/id}", "")
        if releases_url:
            releases = requests.get(releases_url, headers=HEADERS).json()
            if isinstance(releases, list):
                for r in releases:
                    for asset in r.get("assets", []):
                        total_downloads += asset.get("download_count", 0)

    badge = {
        "schemaVersion": 1,
        "label": "GitHub Stats",
        "message": f"⭐ {total_stars} | ⬇️ {total_downloads}",
        "color": "blue"
    }

    with open("stats.json", "w") as f:
        json.dump(badge, f)

if __name__ == "__main__":
    main()
