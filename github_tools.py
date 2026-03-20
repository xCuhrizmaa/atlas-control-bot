import os
import requests
import re
import time
import base64

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
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


# ✅ CREATE REPO
def create_repo(repo_name):

    r = requests.post(
        "https://api.github.com/user/repos",
        json={
            "name": repo_name,
            "private": False
        },
        headers=headers
    )

    print("CREATE REPO RESPONSE:", r.status_code, r.text)

    if r.status_code not in [201, 422]:
        print("❌ Repo creation failed")
        return False

    print("Repo created ✅")
    return True


# 🔥 FORCE INITIAL COMMIT (STABLE)
def create_initial_commit(repo_name):

    base = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    # -----------------------
    # 1. CREATE BLOB
    # -----------------------
    blob_res = requests.post(
        f"{base}/git/blobs",
        json={
            "content": "# Atlas Project\n\nInitialized",
            "encoding": "utf-8"
        },
        headers=headers
    )

    blob = blob_res.json()
    print("BLOB:", blob)

    if "sha" not in blob:
        print("❌ Blob failed")
        return False

    blob_sha = blob["sha"]

    # -----------------------
    # 2. CREATE TREE
    # -----------------------
    tree_res = requests.post(
        f"{base}/git/trees",
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
    )

    tree = tree_res.json()
    print("TREE:", tree)

    if "sha" not in tree:
        print("❌ Tree failed")
        return False

    tree_sha = tree["sha"]

    # -----------------------
    # 3. CREATE COMMIT
    # -----------------------
    commit_res = requests.post(
        f"{base}/git/commits",
        json={
            "message": "Initial commit",
            "tree": tree_sha
        },
        headers=headers
    )

    commit = commit_res.json()
    print("COMMIT:", commit)

    if "sha" not in commit:
        print("❌ Commit failed")
        return False

    commit_sha = commit["sha"]

    # -----------------------
    # 4. CREATE BRANCH
    # -----------------------
    ref_res = requests.post(
        f"{base}/git/refs",
        json={
            "ref": "refs/heads/main",
            "sha": commit_sha
        },
        headers=headers
    )

    print("REF:", ref_res.status_code, ref_res.text)

    if ref_res.status_code not in [200, 201]:
        print("❌ Branch creation failed")
        return False

    print("Initial commit created ✅")
    return True


# ✅ CREATE FILE
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

    print(f"{path} → {r.status_code} | {r.text}")

    return r.status_code in [200, 201]


# 🚀 MAIN
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    if not create_repo(repo_name):
        return repo_name, "failed"

    time.sleep(1)

    if not create_initial_commit(repo_name):
        print("❌ Initial commit failed — stopping")
        return repo_name, "failed"

    success = 0

    for path, content in files.items():
        if create_file(repo_name, path, content):
            success += 1
        time.sleep(0.2)

    print(f"✅ Uploaded {success}/{len(files)} files")

    return repo_name, "v1"