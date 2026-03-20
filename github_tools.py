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


# 🔥 FINAL: CREATE REPO + INITIAL COMMIT + BRANCH + ALL FILES
def create_repo_with_files(repo_name, files):

    repo_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    # ✅ FIXED (comma added)
    r = requests.post(
        "https://api.github.com/user/repos",
        json={
            "name": repo_name,
            "private": False,  # ✅ FIX
            "auto_init": True  # 🔥 REQUIRED
        },
        headers=headers
    )

    if r.status_code not in [201, 422]:
        print("Repo creation failed:", r.text)
        return

    print("Repo created ✅")

    # 🔥 IMPORTANT: give GitHub time to initialize repo + branch
    time.sleep(3)

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
        json={"tree": tree},
        headers=headers
    ).json()

    if "sha" not in tree_response:
        print("Tree creation failed:", tree_response)
        return

    new_tree_sha = tree_response["sha"]

    # 3. Create FIRST commit (no parent)
    commit_response = requests.post(
        f"{repo_url}/git/commits",
        json={
            "message": "Initial Atlas AI commit",
            "tree": new_tree_sha
        },
        headers=headers
    ).json()

    if "sha" not in commit_response:
        print("Commit failed:", commit_response)
        return

    new_commit_sha = commit_response["sha"]

    # 4. Create main branch manually
    ref_response = requests.post(
        f"{repo_url}/git/refs",
        json={
            "ref": "refs/heads/main",
            "sha": new_commit_sha
        },
        headers=headers
    ).json()

    if "ref" not in ref_response:
        print("Branch creation failed:", ref_response)
        return

    print("🔥 Repo fully built with initial commit + branch")


# ✅ MAIN FUNCTION
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    create_repo_with_files(repo_name, files)

    return repo_name, "v1"