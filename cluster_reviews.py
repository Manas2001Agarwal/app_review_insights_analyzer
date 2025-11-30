import json
import os
import pandas as pd
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired, OpenAI
from sklearn.cluster import KMeans
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL_NAME = "openai/gpt-oss-120b"

def load_reviews(filepath):
    with open(filepath, 'r') as f:
        reviews = json.load(f)
    return reviews

def cluster_reviews():
    # 1. Load Data
    reviews = load_reviews('reviews.json')
    review_texts = [r['text_review'] for r in reviews]
    print(f"Loaded {len(reviews)} reviews.")

    # 2. Generate Embeddings (Local)
    print("Generating embeddings using local SentenceTransformer...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedding_model.encode(review_texts, show_progress_bar=True)
    
    # 3. Define Sub-models
    
    # UMAP: Reduce to 5 dimensions, keep neighbors low for small data
    umap_model = UMAP(n_neighbors=5, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    
    # Clustering: KMeans to force 5 topics
    kmeans_model = KMeans(n_clusters=5, random_state=42)
    
    # Vectorizer: Clean up terms
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2))
    
    # Representation: KeyBERT + Groq LLM
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )
    
    prompt = """
    I have a topic that contains the following documents: 
    [DOCUMENTS]
    The topic is described by the following keywords: [KEYWORDS]

    Based on the above information, give a short, concise label (max 5 words) for this topic.
    """
    
    representation_model = {
        "KeyBERT": KeyBERTInspired(top_n_words=10),
        "Groq": OpenAI(client, model=GROQ_MODEL_NAME, chat=True, prompt=prompt)
    }

    # 4. Initialize BERTopic
    topic_model = BERTopic(
        embedding_model=embedding_model, # Pass the model itself or embeddings
        umap_model=umap_model,
        hdbscan_model=kmeans_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        verbose=True
    )

    # 5. Fit Model
    print("Fitting BERTopic model...")
    topics, probs = topic_model.fit_transform(review_texts, embeddings)

    # 6. Output Results
    print("\nTop 5 Topics:")
    freq = topic_model.get_topic_info()
    print(freq.head(10))
    
    results_data = []

    # Print detailed info
    for topic_id in range(5): 
        print(f"\n--- Topic {topic_id} ---")
        topic_info = topic_model.get_topic(topic_id)
        
        # Get count for this topic
        # freq is a dataframe with columns Topic, Count, Name, ...
        # We filter where Topic == topic_id
        topic_count = int(freq[freq['Topic'] == topic_id]['Count'].values[0])
        
        theme_name = "Unknown Theme"
        keywords = []
        
        if topic_info:
            keywords = [word for word, score in topic_info]
            print(f"Keywords: {keywords}")
            
            # Get label from Groq
            try:
                # topic_aspects_ returns a list of labels for the topic
                if "Groq" in topic_model.topic_aspects_:
                    labels = topic_model.topic_aspects_["Groq"][topic_id]
                    # It might be a list of lists or just a list depending on how many labels requested
                    # Usually it's [label]
                    if isinstance(labels, list) and len(labels) > 0:
                        theme_name = labels[0]
                        # If it's a tuple/list inside
                        if isinstance(theme_name, (list, tuple)):
                             theme_name = theme_name[0]
                    else:
                        theme_name = str(labels)
                else:
                    print("Groq labels not found in topic_aspects_")
                
                print(f"Groq Label: {theme_name}")
            except Exception as e:
                print(f"Could not retrieve Groq label: {e}")
            
            # Fallback if theme_name is still "Unknown Theme" or empty
            if not theme_name or theme_name == "Unknown Theme" or theme_name.strip() == "":
                theme_name = ", ".join(keywords[:3]).title()
                print(f"Fallback Label: {theme_name}")
            
            # Get representative docs with metadata
            print("Representative Reviews:")
            rep_docs_text = topic_model.get_representative_docs(topic_id)
            rep_reviews_data = []
            
            # Find metadata for these texts
            # Note: This simple matching assumes unique texts or takes the first match
            for doc_text in rep_docs_text:
                print(f"- {doc_text}")
                for review in reviews:
                    if review['text_review'] == doc_text:
                        rep_reviews_data.append({
                            "User Name": review['user_name'],
                            "Date": review['date'],
                            "Rating": review['rating'],
                            "Review": review['text_review']
                        })
                        break # Found the match
            
            results_data.append({
                "Theme Name": theme_name,
                "Number of Reviews": topic_count,
                "Keywords": keywords,
                "Representative Reviews": rep_reviews_data
            })

    # Export to JSON
    output_json = 'clustering_results.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=4, ensure_ascii=False)
    print(f"\nDetailed results saved to {output_json}")

if __name__ == "__main__":
    cluster_reviews()
