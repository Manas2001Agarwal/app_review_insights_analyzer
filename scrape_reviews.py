import json
import re
from datetime import datetime, timedelta
from google_play_scraper import Sort, reviews
from langdetect import detect, LangDetectException
import pandas as pd
# Configuration
APP_ID = 'in.indwealth'
TARGET_RATINGS = [1, 2, 3, 4, 5]
TARGET_COUNT_PER_RATING = 60
WEEKS_BACK = 20
MIN_WORD_COUNT = 10
def clean_text(text):
    """
    Removes emojis and special characters, keeping only alphanumeric and basic punctuation.
    """
    # Remove emojis and other non-ascii chars (approximate) or use regex for specific cleanup
    # Keeping alphanumeric, spaces, and basic punctuation (.,!?)
    cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False
def run():
    all_reviews = []
    
    # Calculate date threshold
    cutoff_date = datetime.now() - timedelta(weeks=WEEKS_BACK)
    print(f"Filtering reviews after: {cutoff_date.date()}")
    for rating in TARGET_RATINGS:
        print(f"Fetching reviews for rating: {rating}...")
        
        collected_reviews = []
        continuation_token = None
        
        # Fetch more than needed to account for filtering
        # We'll fetch in batches until we have enough qualified reviews
        while len(collected_reviews) < TARGET_COUNT_PER_RATING:
            try:
                result, continuation_token = reviews(
                    APP_ID,
                    lang='en', # Request English reviews from Google, but we'll double check
                    country='in',
                    sort=Sort.NEWEST,
                    count=200, # Fetch a batch
                    filter_score_with=rating,
                    continuation_token=continuation_token
                )
            except Exception as e:
                print(f"Error fetching reviews: {e}")
                return False
            if not result:
                break
            for review in result:
                # 6. Ignore replies from INDMoney team (the library output doesn't include replies by default in the main text, 
                # but 'replyContent' field exists if there is a reply. We just ignore it as requested.)
                
                review_date = review['at']
                content = review['content']
                
                # 4. Date Filter
                if review_date < cutoff_date:
                    # Since we sort by NEWEST, if we hit a date older than cutoff, we can stop for this rating?
                    # Not necessarily, sometimes sort isn't perfect, but usually yes. 
                    # However, to be safe, we just skip. If we find many old ones, we might stop.
                    continue
                # 3. Word Count Filter
                if len(content.split()) < MIN_WORD_COUNT:
                    continue
                # 2. Language Filter (Double check)
                if not is_english(content):
                    continue
                
                # 5. Clean Text
                cleaned_content = clean_text(content)
                
                # Add to list
                collected_reviews.append({
                    "user_name": review['userName'],
                    "rating": review['score'],
                    "text_review": cleaned_content,
                    "date": review_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                if len(collected_reviews) >= TARGET_COUNT_PER_RATING:
                    break
            
            # If we went through a whole batch and the last one was too old, we can probably stop
            if result and result[-1]['at'] < cutoff_date:
                print("Reached past date limit.")
                break
                
            if not continuation_token:
                break
        
        print(f"Collected {len(collected_reviews)} reviews for rating {rating}")
        all_reviews.extend(collected_reviews)
    # Export to JSON
    output_file = 'reviews.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=4, ensure_ascii=False)
    
    print(f"Total reviews saved: {len(all_reviews)}")
    print(f"Saved to {output_file}")
    return True
if __name__ == "__main__":
    run()