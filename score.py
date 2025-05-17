import pandas as pd
import openai
import os
from dotenv import load_dotenv
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(row):
    email = row.get("Email", "")
    website = row.get("Link", "")
    phone = row.get("Phone", "")
    name = row.get("Name", "")

    email_present = email and email != "N/A"
    custom_domain = email_present and not any(g in email.lower() for g in ["gmail", "yahoo", "hotmail", "aol"])
    phone_present = phone and phone != "N/A"
    website_present = website and website != "N/A"

    return f"""
You're a lead scoring agent for a cold outreach tool.

Apply the following scoring system. Start at 0. Maximum score is 100.

Scoring rules:
- +25 if email is present
- +20 if email uses a custom domain (not Gmail, Yahoo, Hotmail, AOL)
- +15 if phone number is present
- +20 if website is present and not empty
- +10 if business name is professional
- -10 if no phone number
- -10 if no website

Here is the lead:

- Name: {name}
- Website: {website}
- Email: {email}
- Phone: {phone}

Respond only with:
SCORE: <numeric score>
REASON: <1–2 sentences explaining your logic>
"""


def get_score(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ GPT error:", e)
        return "SCORE: 0 | REASON: Failed to score"

def enrich_scores(input_file, output_file):
    df = pd.read_csv(input_file)

    if "LeadScore" not in df.columns:
        df["LeadScore"] = ""
        df["ScoreReason"] = ""

    for i, row in df.iterrows():
        if df.at[i, "LeadScore"] != "":
            continue

        prompt = build_prompt(row)
        result = get_score(prompt)
        print(f"→ {row['Name']}: {result}")

        try:
            score_part, reason_part = result.split("|")
            score = int(score_part.strip().replace("SCORE:", "").strip())
            reason = reason_part.strip().replace("REASON:", "").strip()
        except:
            score = 0
            reason = "Parsing error"

        df.at[i, "LeadScore"] = score
        df.at[i, "ScoreReason"] = reason

        time.sleep(1.2)  # polite delay

    df.to_csv(output_file, index=False)
    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    enrich_scores("output/results.csv", "output/results_scored.csv")
