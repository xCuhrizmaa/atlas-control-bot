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

    print("CREATE REPO:", r.status_code)

    if r.status_code not in [201, 422]:
        print("❌ Repo creation failed:", r.text)
        return False

    print("Repo created ✅")
    return True


# 🔥 CREATE FILE (THIS DOES EVERYTHING)
def create_file(repo_name, path, content):

    path = path.lstrip("/").replace("[", "").replace("]", "")

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}"

    encoded = base64.b64encode(content.encode()).decode()

    r = requests.put(
        url,
        json={
            "message": f"Add {path}",
            "content": encoded
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

    # 🔥 NO WAIT NEEDED
    # 🔥 NO INITIAL COMMIT NEEDED

    success = 0

    for i, (path, content) in enumerate(files.items()):

        ok = create_file(repo_name, path, content)

        if ok:
            success += 1
        else:
            print("❌ Failed on:", path)
            break

        time.sleep(0.3)

    print(f"✅ Uploaded {success}/{len(files)} files")

    return repo_name, "v1" if success > 0 else "failed"