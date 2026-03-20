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


# ✅ CREATE REPO (auto creates main branch + README)
def create_repo(repo_name):

    url = "https://api.github.com/user/repos"

    data = {
        "name": repo_name,
        "private": False,
        "auto_init": True
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code == 201:
        print("Repo created")
    elif r.status_code == 422:
        print("Repo already exists")
    else:
        print("Repo creation error:", r.text)


# ✅ WAIT UNTIL REPO IS FULLY READY
def wait_for_repo(repo_name):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    for _ in range(10):
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            print("Repo is ready ✅")
            return

        print("Waiting for repo...")
        time.sleep(1)


# ✅ CREATE FILE (🔥 FINAL STABLE VERSION)
def create_file(repo_name, path, content):

    # 🔥 FINAL FIX: flatten folders + remove brackets
    path = (
        path.lstrip("/")
        .replace("/", "_")
        .replace("[", "")
        .replace("]", "")
    )

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}"

    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": f"Adding {path}",
        "content": encoded_content
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

    wait_for_repo(repo_name)

    # 🔥 EXTRA SAFETY DELAY
    time.sleep(2)

    version = "v1"

    sorted_files = dict(sorted(files.items(), key=lambda x: x[0].count("/")))

    for path, content in sorted_files.items():
        create_file(repo_name, path, content)
        time.sleep(0.5)

    return repo_name, version