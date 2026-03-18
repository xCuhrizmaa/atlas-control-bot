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
    """
    Convert project request into safe repo name
    Example:
    'cookie ordering app with payments'
    -> atlas-cookie-ordering-app
    """

    cleaned = project_type.lower()

    # remove filler words
    cleaned = cleaned.replace("with payments", "")
    cleaned = cleaned.replace("app", "")
    cleaned = cleaned.replace("application", "")

    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned).strip("-")

    return f"atlas-{cleaned}"


def create_repo(repo_name):

    url = "https://api.github.com/user/repos"

    data = {
        "name": repo_name,
        "private": False
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code == 201:
        print("Repo created")
    elif r.status_code == 422:
        print("Repo already exists")
    else:
        print("Repo creation error:", r.text)


def create_file(repo_name, path, content):

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}"

    data = {
        "message": f"Adding {path}",
        "content": base64.b64encode(content.encode()).decode()  # ✅ FIXED
    }

    response = requests.put(url, json=data, headers=headers)

    # ✅ FULL DEBUG OUTPUT
    print("\n====================")
    print(f"FILE: {path}")
    print(f"STATUS: {response.status_code}")
    print(f"RESPONSE: {response.text}")
    print("====================\n")


def create_or_update_repo(project_type, files):

    repo_name = f"{slugify_project(project_type)}-{int(time.time())}"

    create_repo(repo_name)

    time.sleep(3)  # ✅ WAIT for GitHub repo to be ready

    version = "v1"

    for path, content in files.items():
        create_file(repo_name, path, content)

    return repo_name, version
