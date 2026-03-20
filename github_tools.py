import os
import requests
import re
import time
import base64

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",  # ✅ IMPORTANT (Bearer for fine-grained)
    "Accept": "application/vnd.github+json"
}


def slugify_project(project_type):
    cleaned = project_type.lower()
    cleaned = cleaned.replace("with payments", "")
    cleaned = cleaned.replace("app", "")
    cleaned = cleaned.replace("application", "")
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned).strip("-")
    return f"atlas-{cleaned}"


# 🔥 STEP 1: CREATE REPO
def create_repo(repo_name):

    r = requests.post(
        "https://api.github.com/user/repos",
        json={
            "name": repo_name,
            "private": False
        },
        headers=headers
    )

    if r.status_code not in [201, 422]:
        print("Repo creation failed:", r.text)
        return False

    print("Repo created ✅")
    return True


# 🔥 STEP 2: FORCE INITIAL COMMIT
def create_initial_commit(repo_name):

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/git/blobs"

    # 1. Create blob (README)
    blob = requests.post(
        url,
        json={
            "content": "# Atlas Project\n\nInitialized",
            "encoding": "utf-8"
        },
        headers=headers
    ).json()

    blob_sha = blob["sha"]

    # 2. Create tree
    tree = requests.post(
        f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/git/trees",
        json={
            "tree": [
                {
                    "path": "README.md",
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                }
            ]
        },
        headers=headers
    ).json()

    tree_sha = tree["sha"]

    # 3. Create commit
    commit = requests.post(
        f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/git/commits",
        json={
            "message": "Initial commit",
            "tree": tree_sha
        },
        headers=headers
    ).json()

    commit_sha = commit["sha"]

    # 4. Create branch
    ref = requests.post(
        f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/git/refs",
        json={
            "ref": "refs/heads/main",
            "sha": commit_sha
        },
        headers=headers
    )

    if ref.status_code not in [201, 422]:
        print("Initial commit failed:", ref.text)
        return False

    print("Initial commit created ✅")
    return True


# 🔥 STEP 3: NORMAL FILE UPLOAD (NOW IT WORKS)
def create_file(repo_name, path, content):

    path = path.lstrip("/").replace("[", "").replace("]", "")

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}"

    encoded = base64.b64encode(content.encode()).decode()

    r = requests.put(
        url,
        json={
            "message": f"Add {path}",
            "content": encoded,
            "branch": "main"
        },
        headers=headers
    )

    print(f"{path} → {r.status_code}")
    return r.status_code in [200, 201]


# 🔥 MAIN
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    if not create_repo(repo_name):
        return repo_name, "failed"

    time.sleep(1)

    if not create_initial_commit(repo_name):
        return repo_name, "failed"

    success = 0

    for path, content in files.items():
        if create_file(repo_name, path, content):
            success += 1
        time.sleep(0.2)

    print(f"✅ Uploaded {success}/{len(files)} files")

    return repo_name, "v1"