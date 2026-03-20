import os
import requests
import re
import time
import base64

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


# ✅ CREATE REPO
def create_repo(repo_name):

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
        return False

    print("Repo created ✅")
    return True


# 🔥 NEW: WAIT UNTIL REPO IS FULLY READY (CRITICAL FIX)
def wait_for_ready(repo_name):

    repo_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    for _ in range(20):
        repo_data = requests.get(repo_url, headers=headers).json()

        # wait for default branch
        default_branch = repo_data.get("default_branch")

        if default_branch:
            ref = requests.get(
                f"{repo_url}/git/ref/heads/{default_branch}",
                headers=headers
            )

            if ref.status_code == 200:
                print("Repo fully ready ✅")
                return True

        print("Waiting for GitHub to initialize...")
        time.sleep(1)

    return False


# ✅ CREATE FILE
def create_file(repo_name, path, content):

    # flatten + clean path
    path = (
        path.lstrip("/")
        .replace("/", "_")
        .replace("[", "")
        .replace("]", "")
    )

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}"

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": f"Add {path}",
        "content": encoded
    }

    r = requests.put(url, json=data, headers=headers)

    print(f"{path} → {r.status_code}")

    return r.status_code in [200, 201]


# ✅ MAIN FUNCTION
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    if not create_repo(repo_name):
        return repo_name, "failed"

    # 🔥 CRITICAL FIX (replaces blind sleep)
    if not wait_for_ready(repo_name):
        print("❌ Repo never became ready")
        return repo_name, "failed"

    success_count = 0

    for path, content in files.items():
        ok = create_file(repo_name, path, content)

        if ok:
            success_count += 1

        time.sleep(0.3)

    print(f"✅ Uploaded {success_count}/{len(files)} files")

    return repo_name, "v1"