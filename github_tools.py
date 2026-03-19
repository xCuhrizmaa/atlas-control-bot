import os
import requests
import re
import time
import base64
from urllib.parse import quote

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


# 🔥 FIXED: FORCE BRANCH CREATION
def create_repo(repo_name):

    url = "https://api.github.com/user/repos"

    data = {
        "name": repo_name,
        "private": False,
        "auto_init": True,        # ✅ creates README + main branch instantly
        "default_branch": "main"  # ✅ ensures correct branch
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code == 201:
        print("Repo created")
    elif r.status_code == 422:
        print("Repo already exists")
    else:
        print("Repo creation error:", r.text)


def create_file(repo_name, path, content):

    # ✅ flatten + sanitize (this works reliably)
    path = path.lstrip("/").replace("/", "_").replace("[", "").replace("]", "")

    safe_path = quote(path)

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{safe_path}"

    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": f"Adding {path}",
        "content": encoded_content,
        "branch": "main"
    }

    response = requests.put(url, json=data, headers=headers)

    print("\n====================")
    print(f"FILE: {path}")
    print(f"STATUS: {response.status_code}")
    print(f"RESPONSE: {response.text}")
    print("====================\n")


def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    create_repo(repo_name)

    time.sleep(2)  # slightly shorter now that auto_init is used

    version = "v1"

    sorted_files = dict(sorted(files.items(), key=lambda x: x[0].count("/")))

    # ❌ REMOVED manual README (GitHub already created it)

    for path, content in sorted_files.items():
        create_file(repo_name, path, content)
        time.sleep(0.5)

    return repo_name, version