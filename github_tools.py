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


# 🔥 FINAL: CREATE REPO + BUILD ON INITIAL COMMIT
def create_repo_with_files(repo_name, files):

    repo_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    # 1. Create repo
    r = requests.post(
        "https://api.github.com/user/repos",
        json={
            "name": repo_name,
            "private": False,
            "auto_init": True
        },
        headers=headers
    )

    if r.status_code not in [201, 422]:
        print("Repo creation failed:", r.text)
        return

    print("Repo created ✅")

    # 🔥 WAIT FOR INITIAL COMMIT
    default_branch = "main"
    latest_commit_sha = None

    for _ in range(10):
        ref_response = requests.get(
            f"{repo_url}/git/ref/heads/{default_branch}",
            headers=headers
        )

        if ref_response.status_code == 200:
            latest_commit_sha = ref_response.json()["object"]["sha"]
            print("Initial commit found ✅")
            break

        print("Waiting for initial commit...")
        time.sleep(1)

    if not latest_commit_sha:
        print("Failed to find initial commit")
        return

    # 🔥 GET BASE TREE SHA
    commit_data = requests.get(
        f"{repo_url}/git/commits/{latest_commit_sha}",
        headers=headers
    ).json()

    base_tree_sha = commit_data["tree"]["sha"]

    # 2. Build tree (ALL FILES)
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
        json={
            "base_tree": base_tree_sha,  # 🔥 KEY FIX
            "tree": tree
        },
        headers=headers
    ).json()

    if "sha" not in tree_response:
        print("Tree creation failed:", tree_response)
        return

    new_tree_sha = tree_response["sha"]

    # 3. Create commit (on top of initial commit)
    commit_response = requests.post(
        f"{repo_url}/git/commits",
        json={
            "message": "Atlas AI project build",
            "tree": new_tree_sha,
            "parents": [latest_commit_sha]  # 🔥 KEY FIX
        },
        headers=headers
    ).json()

    if "sha" not in commit_response:
        print("Commit failed:", commit_response)
        return

    new_commit_sha = commit_response["sha"]

    # 4. Update branch
    update_response = requests.patch(
        f"{repo_url}/git/refs/heads/{default_branch}",
        json={"sha": new_commit_sha},
        headers=headers
    )

    if update_response.status_code != 200:
        print("Branch update failed:", update_response.text)
        return

    print("🔥 ALL FILES SUCCESSFULLY PUSHED")


# ✅ MAIN FUNCTION
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    create_repo_with_files(repo_name, files)

    return repo_name, "v1"