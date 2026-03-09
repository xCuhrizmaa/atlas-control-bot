import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpret_project(project_request):

    prompt = f"""
You are a senior software architect.

User request:
{project_request}

Design a modern production architecture.

Prefer modern stacks like:
Next.js
Supabase
Stripe
Vercel

Return:

Architecture Plan
Backend
Frontend
Database
Hosting
Key Features
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
