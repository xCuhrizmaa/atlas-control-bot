import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def interpret_project(project_type):

    prompt = f"""
You are an expert software architect.

Convert the following project idea into a structured JSON format.

Project:
{project_type}

Return ONLY valid JSON. No explanation.

Format:
{{
  "name": "project-name",
  "frontend": [
    {{"path": "frontend/pages/index.js", "description": "homepage UI"}},
    {{"path": "frontend/components/Navbar.js", "description": "navigation bar"}}
  ],
  "backend": [
    {{"path": "backend/api/app.js", "description": "main API"}},
    {{"path": "backend/api/orders.js", "description": "orders endpoint"}}
  ],
  "database": [
    {{"path": "database/schema.sql", "description": "database schema"}}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a software architect."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content