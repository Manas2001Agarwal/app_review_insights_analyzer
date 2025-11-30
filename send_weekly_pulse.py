import json
import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GMAIL_USER = "manasmrt10@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
if GMAIL_APP_PASSWORD:
    GMAIL_APP_PASSWORD = GMAIL_APP_PASSWORD.strip()
RECIPIENT_EMAIL = "manasagarwal2512@gmail.com"
GROQ_MODEL_NAME = "openai/gpt-oss-120b"
INPUT_FILE = "pulse_report.json"
LOG_FILE = "email_log.txt"
PRODUCT_NAME = "INDmoney"

def load_report(filepath):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def draft_email_body(report_json):
    print("Drafting email with Groq...")
    
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

    system_prompt = """
    You are drafting an internal weekly email sharing the latest product pulse.
    
    Audience:
    - Product & Growth: want to see what to fix or double down on.
    - Support: wants to know what to acknowledge and celebrate.
    - Leadership: wants a quick pulse, key risks, and wins.
    
    Tasks:
    - Write an email body only (no subject line).
    - Structure:
      1) 2–3 line intro explaining the time window and the product/program.
      2) Embed the weekly pulse note in a clean, scannable format (Title, Overview, Top 3 themes, Quotes, Actions).
      3) End with a short closing line and invite replies.
    
    Constraints:
    - Professional, neutral tone with a hint of warmth.
    - No names, emails, or IDs. Anonymize if needed.
    - Keep the whole email under 350 words.
    - Output plain text only (no HTML).
    """

    user_prompt = f"""
    Input (weekly note JSON):
    {json.dumps(report_json, indent=2)}
    
    Draft the email body.
    """

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error drafting email: {e}")
        return None

def send_email(subject, body):
    if not GMAIL_APP_PASSWORD:
        print("Error: GMAIL_APP_PASSWORD not set in environment.")
        return False

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    print(f"Sending email to {RECIPIENT_EMAIL}...")
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def log_status(status, subject):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] Status: {status} | Subject: {subject} | Recipient: {RECIPIENT_EMAIL}\n")

def run():
    # 1. Load Report
    report = load_report(INPUT_FILE)
    if not report:
        return False

    # 2. Draft Email
    email_body = draft_email_body(report)
    if not email_body:
        return False
    
    # 3. Generate Subject Line
    # Calculating approx week range (last 7 days)
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=7)
    subject = f"Weekly Product Pulse – {PRODUCT_NAME} ({week_start.strftime('%b %d')}–{today.strftime('%b %d')})"
    
    print(f"\n--- Generated Subject ---\n{subject}")
    print(f"\n--- Generated Body ---\n{email_body}\n")

    # 4. Send Email
    success = send_email(subject, email_body)

    # 5. Log Status
    log_status("SUCCESS" if success else "FAILED", subject)
    return success

if __name__ == "__main__":
    run()
