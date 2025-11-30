# App Review Insights Analyzer 🚀

An automated pipeline to scrape Google Play Store reviews, cluster them into key themes using AI, and generate a weekly "Product Pulse" email for stakeholders.

## 🎯 Project Goal
To transform raw user feedback from the **INDmoney** app into actionable product insights. This tool automates the loop of listening to users, identifying their pain points, and reporting them to the product team.

## ✨ Key Features
1.  **Scraping**: Fetches the latest reviews (ratings 1-5) from the Google Play Store.
2.  **Clustering**: Uses **BERTopic** (with `sentence-transformers`) to group reviews into 5 distinct semantic themes.
3.  **Analysis**: Leverages **Groq (Llama 3 / GPT-OSS)** to label themes and extract key insights.
4.  **Reporting**: Generates a "Product Pulse" JSON report with executive summaries, quotes, and action items.
5.  **Automation**: Sends a weekly email summary via Gmail SMTP, orchestrated by **GitHub Actions**.

## 🛠️ Tech Stack
-   **Language**: Python 3.9+
-   **Scraping**: `google-play-scraper`
-   **ML/NLP**: `bertopic`, `sentence-transformers`, `scikit-learn`, `umap-learn`
-   **LLM**: Groq API (`openai/gpt-oss-120b`)
-   **Automation**: GitHub Actions (Cron Schedule)

## 📂 Project Structure
```
├── main.py                 # Master orchestrator script
├── scrape_reviews.py       # Scrapes reviews from Play Store
├── cluster_reviews.py      # Clusters reviews & generates insights
├── generate_pulse.py       # Creates the Product Pulse JSON report
├── send_weekly_pulse.py    # Drafts & sends the email
├── requirements.txt        # Python dependencies
├── .env                    # Local environment variables (not committed)
└── .github/workflows/      # GitHub Actions workflow for automation
```

## 🚀 Setup & Usage

### 1. Prerequisites
-   Python 3.9 or higher
-   A Groq API Key
-   A Gmail Account with an **App Password** (for sending emails)

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Manas2001Agarwal/app_review_insights_analyzer.git
cd app_review_insights_analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```bash
GROQ_API_KEY="your_groq_api_key"
GMAIL_APP_PASSWORD="your_gmail_app_password"
```

### 4. Running Manually
To run the entire pipeline (Scrape -> Cluster -> Report -> Email):
```bash
python main.py
```
You can also run individual steps:
```bash
python scrape_reviews.py
python cluster_reviews.py
python generate_pulse.py
python send_weekly_pulse.py
```

## 🤖 Automation
The project is configured to run automatically every **Monday at 9:00 AM UTC** using GitHub Actions.

**To enable this:**
1.  Go to your GitHub Repository Settings > Secrets and variables > Actions.
2.  Add the following Repository Secrets:
    -   `GROQ_API_KEY`
    -   `GMAIL_APP_PASSWORD`

The workflow is defined in `.github/workflows/weekly_pulse.yml`.

## 📊 Output Examples
-   **`reviews.json`**: Raw scraped data.
-   **`clustering_results.json`**: Detailed themes with keywords and representative reviews.
-   **`pulse_report.json`**: The final executive summary used for the email.
