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


# ✅ CREATE REPO (instant ready)
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


# ✅ CREATE FILE (RELIABLE METHOD)
def create_file(repo_name, path, content):

    # clean path (important)
    path = path.lstrip("/").replace("[", "").replace("]", "")

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}"

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": f"Add {path}",
        "content": encoded
    }

    r = requests.put(url, json=data, headers=headers)

    print(f"{path} → {r.status_code}")

    return r.status_code in [200, 201]


# ✅ MAIN FUNCTION (NO TREE API ANYMORE)
def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    if not create_repo(repo_name):
        return repo_name, "failed"

    time.sleep(2)  # allow repo to initialize

    success_count = 0

    for path, content in files.items():
        ok = create_file(repo_name, path, content)

        if ok:
            success_count += 1

        time.sleep(0.3)

    print(f"✅ Uploaded {success_count}/{len(files)} files")

    return repo_name, "v1"