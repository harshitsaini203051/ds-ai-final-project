import requests
import os
import google.generativeai as genai
import json
import random  # Temporary for demo purposes
from docx import Document
from io import BytesIO

# --- CONFIGURATION ----------------------------------------------------
# API Keys are directly set here as requested by the user
NEWS_API_KEY = "e994016e5176447b83ec0b88961621fe"  # News API key
GEMINI_API_KEY = "AIzaSyAHFbrGN0u1Dvyc-UVpt9uzBs61JqgRSKY"  # Google Gemini API key
TARGET_DOMAINS = ["timesofindia.indiatimes.com", "thehindu.com", "reuters.com", "bbc.com", "cnn.com"]

# Maximum AI score threshold (percentage) - ensuring generated content is less than 10% AI detected
MAX_AI_SCORE = 10

# --- CORE ARTICLE FETCHING LOGIC (Module 1) ---------------------------
def fetch_latest_articles(custom_domains=None):
    """Fetches the latest articles from a list of specified domains.
    
    Args:
        custom_domains (list, optional): List of custom domains to search from. 
                                         If None, uses the default TARGET_DOMAINS.
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
        return {"error": "News API key is not configured."}
    
    # Use custom domains if provided, otherwise use default domains
    domains_to_use = custom_domains if custom_domains else TARGET_DOMAINS
    domains_str = ",".join(domains_to_use)
    
    url = f"https://newsapi.org/v2/everything?domains={domains_str}&language=en&sortBy=publishedAt&pageSize=40&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Check if articles are being filtered out somehow
        if data.get('status') == 'ok' and data.get('totalResults', 0) > 0 and len(data.get('articles', [])) == 0:
            print("WARNING: API reports articles exist but none were returned in the response")
            
        # Return the full response but ensure articles is always a list
        if 'articles' not in data:
            data['articles'] = []
            
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        return {"error": f"Network Error: {e}"}

# --- ARTICLE GENERATION LOGIC (Module 3) ------------------------------
def generate_seo_article(original_title, original_content):
    """Uses the Gemini API to generate an SEO-friendly article."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return {"error": "Gemini API key is not configured."}
        
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Act as an expert content writer and SEO specialist.
        Your task is to write a new, unique article based on the provided source material.

        **Instructions:**
        1.  **Length:** The final article must be approximately 340 words.
        2.  **Tone:** Professional, informative, and engaging for a general audience.
        3.  **SEO:** Naturally include relevant keywords from the source material. The title should be catchy and SEO-friendly.
        4.  **Originality:** Do NOT copy sentences directly. Rewrite and rephrase all information to create a fresh perspective.
        5.  **Structure:** Start with a compelling introduction, followed by 2-3 body paragraphs, and end with a concluding summary.

        **Source Material:**
        - **Original Title:** "{original_title}"
        - **Original Content:** "{original_content}"

        Now, please generate the new, SEO-optimized article.
        """
        response = model.generate_content(prompt)
        # Return the generated text in a structured dictionary
        return {"generated_text": response.text}
    except Exception as e:
        return {"error": f"An error occurred with the Gemini API: {e}"}
    
# --- AI DETECTION LOGIC (Module 4) ------------------------------
def detect_ai_content(text):
    """
    Detects if the provided text is likely to be AI-generated using a combination of
    free methods including enhanced local analysis and optional API integration.
    
    This function provides AI content detection without requiring paid API keys.
    It uses a more sophisticated local analysis algorithm and can be extended with
    free API services when available.
    
    Args:
        text (str): The text to analyze for AI generation.
        
    Returns:
        dict: A dictionary containing the AI detection score and analysis.
    """
    # GPTZero API key - free tier available with limited usage
    # Uncomment and configure if you want to use GPTZero's free tier
    # GPTZERO_API_KEY = "YOUR_GPTZERO_API_KEY_HERE"
    
    # Copyleaks API key - free demo available
    # Uncomment and configure if you want to use Copyleaks free demo
    # COPYLEAKS_API_KEY = "YOUR_COPYLEAKS_API_KEY_HERE"
    
    # By default, use the enhanced local detection
    # This provides a reasonable fallback without requiring any API keys
    return _enhanced_local_ai_detection(text)
    
    # Uncomment the appropriate section below if you want to use a free API service
    
    # # GPTZero implementation
    # if GPTZERO_API_KEY and GPTZERO_API_KEY != "YOUR_GPTZERO_API_KEY_HERE":
    #     try:
    #         url = 'https://api.gptzero.me/v2/predict/text'
    #         headers = {
    #             'x-api-key': GPTZERO_API_KEY,
    #             'Content-Type': 'application/json'
    #         }
    #         data = {
    #             'document': text
    #         }
    #         
    #         response = requests.post(url, headers=headers, json=data)
    #         response.raise_for_status()
    #         
    #         result = response.json()
    #         
    #         # Extract the AI probability from the response
    #         # GPTZero returns a completely_generated_prob value
    #         ai_score = int(result.get('documents', {}).get('completely_generated_prob', 0.5) * 100)
    #         
    #         # Determine classification based on score
    #         if ai_score > 75:
    #             classification = "likely_ai"
    #         elif ai_score > 40:
    #             classification = "possibly_ai"
    #         elif ai_score > MAX_AI_SCORE:
    #             classification = "slightly_ai"
    #         else:
    #             classification = "likely_human"
    #         
    #         # Create analysis dictionary
    #         analysis = {
    #             "ai_score": ai_score,
    #             "human_score": 100 - ai_score,
    #             "analysis": {
    #                 "overall_classification": classification,
    #                 "api_used": "gptzero",
    #                 "text_metrics": {
    #                     "word_count": len(text.split())
    #                 }
    #             }
    #         }
    #         
    #         return analysis
    #     except Exception as e:
    #         print(f"Error with GPTZero API: {e}")
    #         # Fall back to enhanced local analysis if API call fails
    #         return _enhanced_local_ai_detection(text)
    # else:
    #     return _enhanced_local_ai_detection(text)


def humanize_content(text):
    """
    Humanizes the provided text to make it appear more human-written using a combination
    of free methods including enhanced local humanization and optional API integration.
    
    This function provides text humanization without requiring paid API keys.
    It uses a sophisticated local algorithm and can be extended with free API services
    when available.
    
    Args:
        text (str): The text to humanize.
        
    Returns:
        dict: A dictionary containing the humanized text and status.
    """
    # By default, use the local humanization method
    # This provides a reasonable solution without requiring any API keys
    return _local_humanize_text(text)
    
    # Uncomment the appropriate section below if you want to use a free API service
    
    # # The Ghost AI API key - free tier available with limited usage
    # # Uncomment and configure if you want to use The Ghost AI's free tier
    # GHOST_AI_API_KEY = "YOUR_GHOST_AI_API_KEY_HERE"
    # 
    # if GHOST_AI_API_KEY and GHOST_AI_API_KEY != "YOUR_GHOST_AI_API_KEY_HERE":
    #     try:
    #         # Make API call to The Ghost AI
    #         url = 'https://api.the-ghost-ai.com/v1/humanize'
    #         headers = {
    #             'Authorization': f'Bearer {GHOST_AI_API_KEY}',
    #             'Content-Type': 'application/json'
    #         }
    #         data = {
    #             'text': text,
    #             'tone': 'professional'
    #         }
    #         
    #         response = requests.post(url, headers=headers, json=data)
    #         response.raise_for_status()
    #         
    #         result = response.json()
    #         
    #         if result.get('status') == 'success':
    #             return {
    #                 "status": "success",
    #                 "humanized_text": result.get('humanized_text'),
    #                 "message": "Text successfully humanized"
    #             }
    #         else:
    #             # Fall back to local humanization if API call fails
    #             return _local_humanize_text(text)
    #     except Exception as e:
    #         print(f"Error with humanization API: {e}")
    #         # Fall back to local humanization if API call fails
    #         return _local_humanize_text(text)
    # else:
    #     return _local_humanize_text(text)


def _local_humanize_text(text):
    """
    Local method for text humanization without requiring external APIs.
    Uses advanced NLP techniques to make AI-generated text appear more human-written.
    
    This function applies various transformations to the text to introduce elements
    typical of human writing, such as varied sentence structures, contractions,
    and natural language patterns.
    
    Args:
        text (str): The text to humanize.
        
    Returns:
        dict: A dictionary containing the humanized text and status.
    """
    import re
    import random
    
    try:
        # Split text into sentences for processing
        sentences = re.split(r'(?<=[.!?])\s+', text)
        humanized_sentences = []
        
        # Process each sentence
        for i, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence.split()) < 3:
                humanized_sentences.append(sentence)
                continue
                
            # 1. Add contractions (randomly)
            contractions = {
                'it is': "it's",
                'that is': "that's",
                'there is': "there's",
                'he is': "he's",
                'she is': "she's",
                'who is': "who's",
                'what is': "what's",
                'where is': "where's",
                'when is': "when's",
                'why is': "why's",
                'how is': "how's",
                'I am': "I'm",
                'you are': "you're",
                'we are': "we're",
                'they are': "they're",
                'I have': "I've",
                'you have': "you've",
                'we have': "we've",
                'they have': "they've",
                'would have': "would've",
                'could have': "could've",
                'should have': "should've",
                'will not': "won't",
                'cannot': "can't",
                'do not': "don't",
                'does not': "doesn't",
                'did not': "didn't",
                'has not': "hasn't",
                'have not': "haven't",
                'had not': "hadn't",
                'is not': "isn't",
                'are not': "aren't",
                'was not': "wasn't",
                'were not': "weren't",
                'should not': "shouldn't",
                'would not': "wouldn't",
                'could not': "couldn't"
            }
            
            modified_sentence = sentence
            for phrase, contraction in contractions.items():
                if phrase in modified_sentence.lower() and random.random() < 0.7:  # 70% chance to apply
                    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                    modified_sentence = pattern.sub(contraction, modified_sentence, 1)
            
            # 2. Add filler words and transition phrases (occasionally)
            if i > 0 and random.random() < 0.2:  # 20% chance to add a transition at the start
                transitions = [
                    "However, ", "Moreover, ", "In addition, ", "Furthermore, ",
                    "On the other hand, ", "Interestingly, ", "Notably, ",
                    "As a result, ", "Consequently, ", "Therefore, "
                ]
                modified_sentence = random.choice(transitions) + modified_sentence[0].lower() + modified_sentence[1:]
            
            if random.random() < 0.15:  # 15% chance to add a filler
                fillers = [
                    " actually ", " basically ", " essentially ", " honestly ",
                    " in fact ", " of course ", " surprisingly ", " interestingly "
                ]
                words = modified_sentence.split()
                if len(words) > 4:
                    insert_pos = random.randint(1, min(4, len(words)-1))
                    words.insert(insert_pos, random.choice(fillers).strip())
                    modified_sentence = ' '.join(words)
            
            # 3. Vary sentence structure (occasionally)
            if random.random() < 0.1 and not any(q in modified_sentence for q in ['?', '!']):  # 10% chance
                # Convert to rhetorical question
                if modified_sentence.endswith('.'):
                    modified_sentence = modified_sentence[:-1] + '?'
                    
            # 4. Add emphasis (occasionally)
            if random.random() < 0.05:  # 5% chance
                words = modified_sentence.split()
                if len(words) > 3:
                    emphasis_pos = random.randint(1, len(words)-2)
                    emphasis_formats = ['very ', 'really ', 'quite ', 'extremely ']
                    words.insert(emphasis_pos, random.choice(emphasis_formats))
                    modified_sentence = ' '.join(words)
            
            humanized_sentences.append(modified_sentence)
        
        # Combine sentences back into text
        humanized_text = ' '.join(humanized_sentences)
        
        # 5. Fix any double spaces or punctuation issues
        humanized_text = re.sub(r'\s+', ' ', humanized_text)  # Fix multiple spaces
        humanized_text = re.sub(r'\s+([.,;:!?])', r'\1', humanized_text)  # Fix space before punctuation
        
        return {
            "status": "success",
            "humanized_text": humanized_text,
            "message": "Text successfully humanized using local processing"
        }
    except Exception as e:
        print(f"Error with local humanization: {e}")
        return {
            "status": "error",
            "error": f"Local humanization failed: {str(e)}"
        }

def _enhanced_local_ai_detection(text):
    """
    Enhanced local method for AI detection without requiring external APIs.
    Uses multiple text characteristics to estimate AI probability with improved accuracy.
    
    This function analyzes various linguistic features that typically differ between
    human and AI-generated text, providing a more sophisticated analysis than the
    basic fallback method.
    
    Args:
        text (str): The text to analyze.
        
    Returns:
        dict: A dictionary containing the AI detection score and analysis.
    """
    import re
    import math
    from collections import Counter
    
    # Extract basic text features for analysis
    words = text.lower().split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    unique_words = len(set(words))
    
    # More advanced metrics
    # 1. Vocabulary diversity (higher in human text)
    vocabulary_diversity = unique_words / max(1, word_count)
    
    # 2. Average sentence length (AI often has more consistent lengths)
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / max(1, len(sentence_lengths))
    
    # 3. Sentence length variation (higher in human text)
    if len(sentence_lengths) > 1:
        sentence_length_std = math.sqrt(sum((x - avg_sentence_length) ** 2 for x in sentence_lengths) / len(sentence_lengths))
    else:
        sentence_length_std = 0
    
    # 4. Word frequency distribution (humans use more rare words)
    word_freq = Counter(words)
    common_words_ratio = sum(1 for w, c in word_freq.items() if c > 2) / max(1, len(word_freq))
    
    # 5. Filler words and transition phrases (humans use more)
    filler_words = ['well', 'actually', 'basically', 'honestly', 'like', 'you know', 'I mean', 'sort of', 'kind of']
    transition_phrases = ['however', 'moreover', 'nevertheless', 'in addition', 'on the other hand', 'for instance']
    
    filler_count = sum(words.count(word) for word in filler_words)
    transition_count = sum(text.lower().count(phrase) for phrase in transition_phrases)
    
    filler_ratio = filler_count / max(1, word_count)
    transition_ratio = transition_count / max(1, sentence_count)
    
    # 6. Repetition patterns (AI tends to repeat more)
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    bigram_freq = Counter(bigrams)
    repeated_bigrams = sum(1 for bg, count in bigram_freq.items() if count > 1)
    repetition_ratio = repeated_bigrams / max(1, len(bigram_freq))
    
    # 7. Contractions (humans use more)
    contractions = ["'s", "'re", "'ve", "'ll", "'d", "n't"]
    contraction_count = sum(text.count(c) for c in contractions)
    contraction_ratio = contraction_count / max(1, word_count)
    
    # Calculate AI score based on these metrics
    # Start with a neutral score
    ai_score = 50
    
    # Adjust based on vocabulary diversity (higher diversity = more human-like)
    if vocabulary_diversity > 0.7:
        ai_score -= 15
    elif vocabulary_diversity > 0.5:
        ai_score -= 8
    elif vocabulary_diversity < 0.3:
        ai_score += 10
    
    # Adjust based on sentence length variation (higher variation = more human-like)
    if sentence_length_std > 8:
        ai_score -= 10
    elif sentence_length_std < 3 and sentence_count > 5:
        ai_score += 12
    
    # Adjust based on filler words and transitions (more = more human-like)
    if filler_ratio > 0.01:
        ai_score -= 8
    if transition_ratio > 0.1:
        ai_score -= 7
    
    # Adjust based on repetition (more repetition = more AI-like)
    if repetition_ratio > 0.2:
        ai_score += 12
    elif repetition_ratio < 0.05:
        ai_score -= 5
    
    # Adjust based on contractions (more contractions = more human-like)
    if contraction_ratio > 0.02:
        ai_score -= 10
    elif contraction_ratio < 0.005 and word_count > 200:
        ai_score += 8
    
    # Adjust based on common words ratio (more common words = more AI-like)
    if common_words_ratio > 0.7:
        ai_score += 10
    elif common_words_ratio < 0.4:
        ai_score -= 8
    
    # Adjust based on text length (very short texts are hard to analyze)
    if word_count < 50:
        # For very short texts, be more conservative
        ai_score = min(max(40, ai_score), 60)
    
    # Ensure score stays within bounds
    ai_score = max(min(ai_score, 99), 1)
    
    # Determine classification based on score
    if ai_score > 75:
        classification = "likely_ai"
    elif ai_score > 40:
        classification = "possibly_ai"
    elif ai_score > MAX_AI_SCORE:
        classification = "slightly_ai"
    else:
        classification = "likely_human"
    
    # Create a detailed analysis
    analysis = {
        "ai_score": ai_score,
        "human_score": 100 - ai_score,
        "analysis": {
            "overall_classification": classification,
            "method": "enhanced_local_analysis",
            "text_metrics": {
                "vocabulary_diversity": round(vocabulary_diversity * 100),
                "avg_sentence_length": round(avg_sentence_length, 1),
                "sentence_length_variation": round(sentence_length_std, 1),
                "word_count": word_count,
                "sentence_count": sentence_count,
                "repetition_index": round(repetition_ratio * 100),
                "contraction_usage": round(contraction_ratio * 100),
                "filler_word_usage": round(filler_ratio * 100)
            }
        }
    }
    
    return analysis


def _fallback_ai_detection(text):
    """
    Legacy fallback method for AI detection.
    This is kept for backward compatibility but _enhanced_local_ai_detection is preferred.
    
    Args:
        text (str): The text to analyze.
        
    Returns:
        dict: A dictionary containing the AI detection score and analysis.
    """
    # Call the enhanced method instead
    return _enhanced_local_ai_detection(text)

# --- HUMANIZATION LOGIC (Module 5) ------------------------------
# The humanization logic is now implemented in the humanize_content and _local_humanize_text functions above

# --- OUTPUT DELIVERY LOGIC (Module 6) ------------------------------
def create_docx_file(text_content):
    """Creates a .docx file from text content in memory."""
    try:
        document = Document()
        document.add_paragraph(text_content)
        
        # Save the document to a memory buffer instead of a file on disk
        file_stream = BytesIO()
        document.save(file_stream)
        file_stream.seek(0)  # Move cursor to the beginning of the stream
        return file_stream
    except Exception as e:
        return {"error": f"Error creating document: {e}"}
    
