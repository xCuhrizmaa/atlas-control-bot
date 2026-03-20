import os
import requests
import re
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def slugify_project(project_type):
    cleaned = project_type.lower()

    cleaned = cleaned.replace("with payments", "")
    cleaned = cleaned.replace("app", "")
    cleaned = cleaned.replace("application", "")

    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned).strip("-")

    return f"atlas-{cleaned}"


# 🔥 FINAL: CREATE REPO + COMMIT ALL FILES AT ONCE
def create_repo_with_files(repo_name, files):

    # 1. Create repo
    url = "https://api.github.com/user/repos"

    data = {
        "name": repo_name,
        "private": False,
        "auto_init": True
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code not in [201, 422]:
        print("Repo creation failed:", r.text)
        return

    print("Repo created ✅")

    time.sleep(2)

    repo_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    # 2. Get default branch
    repo_data = requests.get(repo_url, headers=headers).json()
    default_branch = repo_data["default_branch"]

    # 3. Get latest commit
    ref_data = requests.get(f"{repo_url}/git/ref/heads/{default_branch}", headers=headers).json()
    latest_commit_sha = ref_data["object"]["sha"]

    # 4. Get base tree
    commit_data = requests.get(f"{repo_url}/git/commits/{latest_commit_sha}", headers=headers).json()
    base_tree_sha = commit_data["tree"]["sha"]

    # 5. Build tree (ALL FILES)
    tree = []

    for path, content in files.items():
        clean_path = path.replace("[", "").replace("]", "")

        tree.append({
            "path": clean_path,
            "mode": "100644",
            "type": "blob",
            "content": content
        })

    tree_response = requests.post(
        f"{repo_url}/git/trees",
        json={"base_tree": base_tree_sha, "tree": tree},
        headers=headers
    ).json()

    new_tree_sha = tree_response["sha"]

    # 6. Create commit
    commit_response = requests.post(
        f"{repo_url}/git/commits",
        json={
            "message": "Atlas AI project build",
            "tree": new_tree_sha,
            "parents": [latest_commit_sha]
        },
        headers=headers
    ).json()

    new_commit_sha = commit_response["sha"]

    # 7. Update branch
    requests.patch(
        f"{repo_url}/git/refs/heads/{default_branch}",
        json={"sha": new_commit_sha},
        headers=headers
    )

    print("🔥 ALL FILES SUCCESSFULLY PUSHED")


# ✅ MAIN FUNCTION
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    create_repo_with_files(repo_name, files)

    return repo_name, "v1"