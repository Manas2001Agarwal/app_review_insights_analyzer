import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL_NAME = "openai/gpt-oss-120b"
INPUT_FILE = "clustering_results.json"
OUTPUT_FILE = "pulse_report.json"

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def run():
    # 1. Load Clustering Results
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return False

    clusters = load_data(INPUT_FILE)
    
    # 2. Select Top 3 Themes by Volume
    # Ensure 'Number of Reviews' exists, default to 0 if not
    sorted_clusters = sorted(clusters, key=lambda x: x.get('Number of Reviews', 0), reverse=True)
    top_3_themes = sorted_clusters[:3]
    
    print(f"Top 3 Themes Selected: {[t['Theme Name'] for t in top_3_themes]}")

    # 3. Prepare Prompt for LLM
    themes_context = ""
    for i, theme in enumerate(top_3_themes):
        themes_context += f"\nTheme {i+1}: {theme['Theme Name']} ({theme.get('Number of Reviews', 0)} reviews)\n"
        themes_context += f"Keywords: {', '.join(theme['Keywords'][:5])}\n"
        themes_context += "Representative Reviews:\n"
        for review in theme['Representative Reviews'][:3]:
            themes_context += f"- \"{review['Review']}\" (Rating: {review['Rating']})\n"

    system_prompt = """
    You are a Product Strategy Expert. Your goal is to produce a "Product Pulse" report based on user reviews.
    
    Output MUST be a valid JSON object with this exact structure:
    {
      "title": "...",
      "overview": "...",
      "themes": [
        {"name": "...", "summary": "..."},
        ...
      ],
      "quotes": ["...", "...", "..."],
      "actions": ["...", "...", "..."]
    }
    """

    user_prompt = f"""
    Analyze the following Top 3 Themes from our app reviews and generate a Product Pulse report.

    DATA:
    {themes_context}

    REQUIREMENTS:
    1. Title: Short and punchy.
    2. Overview: One-paragraph executive summary (max 100 words).
    3. Themes: List the 3 themes provided. For each, write 1 sentence combining sentiment + key insight.
    4. Quotes: Select 3 short, impactful quotes (1-2 lines) from the data. clearly marked with the theme name in brackets e.g. "[Theme Name] Quote...".
    5. Actions: 3 specific, actionable ideas (bullets), each linked to a theme.

    CONSTRAINTS:
    - Total length: <= 400 words.
    - Tone: Executive-friendly, neutral, professional.
    - No PII (names, emails).
    - JSON OUTPUT ONLY. Do not include markdown formatting like ```json.
    """

    # 4. Call Groq API
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

    print("Generating report with Groq...")
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=2048
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up potential markdown code blocks if the model ignores the instruction
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        report_json = json.loads(content)
        
        # 5. Save Output
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report_json, f, indent=4)
            
        print(f"Report generated successfully: {OUTPUT_FILE}")
        return True
        
    except Exception as e:
        print(f"Error generating report: {e}")
        # print("Raw Content:", content if 'content' in locals() else "None") 
        return False
        return False

if __name__ == "__main__":
    run()
