import pandas as pd
import openai
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

DEFAULT_TONE = "casual"
DEFAULT_VARIANT_COUNT = 3
DEFAULT_OFFER = "We help local businesses get 5–15 qualified applicants in 14 days with zero hiring fees."
EXAMPLES_FILE = "cold_email_examples.txt"


def load_examples():
    with open(EXAMPLES_FILE, "r") as f:
        return f.read()


def build_sequence_prompt(lead, offer, tone, examples):
    return f"""
You are a cold email strategist.

Below is a 7-email campaign used successfully by another business:

{examples}

Now, generate a custom version of that sequence for this business:

- Name: {lead['Name']}
- Website: {lead['Link']}
- Email: {lead['Email']}
- Lead Score: {lead['LeadScore']}
- Offer: {offer}
- Tone: {tone}

Use the same themes, timing, and structure. Match the style of the examples but personalize to this business.
Respond ONLY in this JSON format:
[
  {{ "day": 1, "subject": "...", "body": "..." }},
  {{ "day": 3, "subject": "...", "body": "..." }},
  ...
]
"""


def generate_email_sequence(lead, offer=DEFAULT_OFFER, tone=DEFAULT_TONE, examples=""):
    try:
        prompt = build_sequence_prompt(lead, offer, tone, examples)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"❌ GPT error on {lead['Name']}:", e)
        return []


def generate_sequences(input_file, output_file, offer=DEFAULT_OFFER, tone=DEFAULT_TONE):
    df = pd.read_csv(input_file)
    examples = load_examples()

    for i, row in df.iterrows():
        if df.at[i, "Email_1_Subject"] if "Email_1_Subject" in df.columns else False:
            continue  # Skip if already populated

        print(f"📝 Generating sequence for: {row['Name']}")
        sequence = generate_email_sequence(row, offer=offer, tone=tone, examples=examples)

        for email in sequence:
            day = email.get("day")
            if day:
                df.at[i, f"Email_D{day}_Subject"] = email.get("subject", "")
                df.at[i, f"Email_D{day}_Body"] = email.get("body", "")

        time.sleep(1.5)  # polite spacing

    df.to_csv(output_file, index=False)
    print(f"✅ Sequences saved to {output_file}")


if __name__ == "__main__":
    generate_sequences(
        input_file="output/results_scored.csv",
        output_file="output/results_with_sequences.csv",
        offer=DEFAULT_OFFER,
        tone=DEFAULT_TONE
    )
