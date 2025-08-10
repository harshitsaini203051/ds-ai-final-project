from flask import Blueprint, render_template, request, jsonify, send_file
from services import fetch_latest_articles, generate_seo_article, detect_ai_content, humanize_content, create_docx_file, MAX_AI_SCORE
import io
import json

main_bp = Blueprint('main', __name__)

# --- API Route for Fetching Articles ---
@main_bp.route("/api/get-articles")
def get_articles():
    articles_data = fetch_latest_articles()
    return jsonify(articles_data)

# --- API Route for Fetching Articles from Custom Websites ---
@main_bp.route("/api/search-articles", methods=['POST'])
def search_articles():
    data = request.get_json()
    websites = data.get('websites', [])
    
    if not websites:
        return jsonify({"error": "No websites provided"}), 400
    
    # Convert comma-separated string to list if needed
    if isinstance(websites, str):
        websites = [site.strip() for site in websites.split(',')]
    
    # Validate websites format
    valid_websites = []
    for site in websites:
        # Basic validation - ensure it's a domain name
        if '.' in site and not site.startswith('http'):
            valid_websites.append(site)
        elif site.startswith('http'):
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                domain = urlparse(site).netloc
                if domain:
                    valid_websites.append(domain)
            except:
                pass
    
    if not valid_websites:
        return jsonify({"error": "No valid websites provided. Please provide domain names like 'example.com'"}), 400
    
    articles_data = fetch_latest_articles(valid_websites)
    return jsonify(articles_data)

# --- NEW API Route for Generating an Article ---
@main_bp.route("/api/generate-article", methods=['POST'])
def generate_article_route():
    # Get the article data sent from the frontend
    data = request.get_json()
    title = data.get('title')
    content = data.get('description')

    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    # Call the generation service
    generated_data = generate_seo_article(title, content)
    return jsonify(generated_data)

# --- Frontend Page Route ---
@main_bp.route("/api/detect-ai", methods=['POST'])
def detect_ai_route():
    # Get the generated text sent from the frontend
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "Missing text content"}), 400
    
    # Call the AI detection service
    detection_result = detect_ai_content(text)
    return jsonify(detection_result)

@main_bp.route("/api/humanize-article", methods=['POST'])
def humanize_article_route():
    # Get the text to humanize from the frontend
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "Missing text content"}), 400
    
    # Call the humanization service
    result = humanize_content(text)
    
    if result.get('status') == 'success':
        # Get AI detection score for the humanized text
        humanized_text = result['humanized_text']
        detection_result = detect_ai_content(humanized_text)
        
        return jsonify({
            'status': 'success',
            'humanized_text': humanized_text,
            'ai_score': detection_result.get('ai_score', 0),
            'message': f"Content successfully humanized! AI detection score: {detection_result.get('ai_score', 0)}%"
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error', 'Failed to humanize text')
        }), 400
    
    return jsonify(result)

@main_bp.route("/api/get-article-text", methods=['POST'])
def get_article_text():
    # Get the content to display in text editor
    data = request.get_json()
    content = data.get('text')
    
    if not content:
        return jsonify({"error": "Missing text content"}), 400
    
    # Return the text content directly as JSON
    return jsonify({
        'text': content,
        'success': True
    })

@main_bp.route("/api/download-docx", methods=['POST'])
def download_docx():
    # Get the content to convert to DOCX
    data = request.get_json()
    content = data.get('text')
    filename = data.get('filename', 'article.docx')
    
    if not content:
        return jsonify({"error": "Missing text content"}), 400
    
    # Create the DOCX file in memory
    docx_file = create_docx_file(content)
    
    # Check if there was an error
    if isinstance(docx_file, dict) and 'error' in docx_file:
        return jsonify(docx_file), 400
    
    # Return the file for download
    return send_file(
        docx_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

@main_bp.route("/")
def home():
    return render_template('dash.html')

