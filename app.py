"""
Flask Web Application for Medium Article Scraping and Search
DS Assignment 4 - Full Website + Deployment Ready
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import pandas as pd
from scraper import scrape_medium_article, search_similar_articles
import csv

app = Flask(__name__)

# CSV file path
CSV_FILE = 'scrapping_results.csv'

# Global DataFrame to store articles in memory
articles_df = None

def load_articles():
    """Load articles from CSV into global DataFrame"""
    global articles_df
    if os.path.exists(CSV_FILE):
        try:
            articles_df = pd.read_csv(CSV_FILE)
            # Reset index to use as ID
            articles_df.reset_index(drop=True, inplace=True)
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            articles_df = pd.DataFrame()
    else:
        articles_df = pd.DataFrame()

# Initialize CSV file with headers if it doesn't exist
def init_csv():
    """Create CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        headers = [
            'Title', 'Subtitle', 'Full Text', 'Number of Images', 
            'Image URLs', 'Number of External Links', 'Author Name', 
            'Author Profile URL', 'Number of Claps', 'Reading Time', 
            'Keywords', 'URL'
        ]
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

@app.route('/')
def index():
    """Home page - Scraping interface"""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Handle article scraping request"""
    try:
        # Get URLs from form
        urls_text = request.form.get('urls', '')
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            return jsonify({'success': False, 'message': 'Please provide at least one URL'}), 400
        
        results = []
        errors = []
        
        # Scrape each URL
        for url in urls:
            try:
                article_data = scrape_medium_article(url)
                if article_data:
                    # Add URL to data
                    article_data['URL'] = url
                    results.append(article_data)
                else:
                    errors.append(f"Failed to scrape: {url}")
            except Exception as e:
                errors.append(f"Error scraping {url}: {str(e)}")
        
        # Save to CSV
        if results:
            df = pd.DataFrame(results)
            # Ensure all columns exist
            columns = [
                'Title', 'Subtitle', 'Full Text', 'Number of Images', 
                'Image URLs', 'Number of External Links', 'Author Name', 
                'Author Profile URL', 'Number of Claps', 'Reading Time', 
                'Keywords', 'URL'
            ]
            
            # Reorder columns and fill missing ones
            for col in columns:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[columns]
            
            # Append to CSV
            if os.path.exists(CSV_FILE):
                df.to_csv(CSV_FILE, mode='a', header=False, index=False, encoding='utf-8')
            else:
                df.to_csv(CSV_FILE, mode='w', header=True, index=False, encoding='utf-8')
            
            # Reload articles into memory
            load_articles()
            
            # Prepare scraped articles for display (stay on same page)
            global articles_df
            scraped_articles = []
            if articles_df is not None and not articles_df.empty:
                # Get the newly scraped articles (last N articles)
                for i in range(len(results)):
                    idx = len(articles_df) - len(results) + i
                    if idx >= 0:
                        article_row = articles_df.iloc[idx]
                        
                        # Safely convert fields to strings
                        def safe_str(value):
                            if pd.isna(value) or value is None:
                                return ''
                            return str(value)
                        
                        # Truncate text to 200-300 characters
                        full_text = safe_str(article_row.get('Full Text', ''))
                        if len(full_text) > 300:
                            truncated_text = full_text[:300] + '...'
                        else:
                            truncated_text = full_text
                        
                        # Process keywords
                        keywords_str = safe_str(article_row.get('Keywords', ''))
                        keywords_list = []
                        if keywords_str and keywords_str != 'N/A' and keywords_str.strip():
                            keywords_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
                        
                        # Process image URLs
                        image_urls_str = safe_str(article_row.get('Image URLs', ''))
                        image_urls_list = []
                        if image_urls_str and image_urls_str != 'N/A' and image_urls_str.strip():
                            image_urls_list = [url.strip() for url in image_urls_str.split(';') if url.strip()]
                        
                        scraped_articles.append({
                            'id': idx,
                            'title': safe_str(article_row.get('Title', 'N/A')),
                            'subtitle': safe_str(article_row.get('Subtitle', 'N/A')),
                            'text': truncated_text,
                            'num_images': int(article_row.get('Number of Images', 0)) if pd.notna(article_row.get('Number of Images')) else 0,
                            'image_urls': image_urls_list,
                            'num_external_links': int(article_row.get('Number of External Links', 0)) if pd.notna(article_row.get('Number of External Links')) else 0,
                            'author': safe_str(article_row.get('Author Name', 'N/A')),
                            'author_url': safe_str(article_row.get('Author Profile URL', '')),
                            'claps': int(article_row.get('Number of Claps', 0)) if pd.notna(article_row.get('Number of Claps')) else 0,
                            'reading_time': safe_str(article_row.get('Reading Time', 'N/A')),
                            'keywords': keywords_list,
                            'url': safe_str(article_row.get('URL', '')),
                        })
            
            return jsonify({
                'success': True,
                'scraped': len(results),
                'errors': errors,
                'message': f'Successfully scraped {len(results)} article(s)',
                'articles': scraped_articles
            })
        
        # If no results, return error
        return jsonify({
            'success': False,
            'errors': errors,
            'message': 'No articles were successfully scraped'
        }), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/search')
def search_page():
    """Search page"""
    return render_template('search.html')

@app.route('/articles')
def articles_list():
    """Display all scraped articles"""
    global articles_df
    load_articles()
    
    if articles_df is None or articles_df.empty:
        return render_template('articles.html', articles=[], message='No articles found. Please scrape some articles first.')
    
    # Convert DataFrame to list of dicts with index as ID
    articles = []
    for idx, row in articles_df.iterrows():
        articles.append({
            'id': idx,
            'title': row.get('Title', 'N/A'),
            'subtitle': row.get('Subtitle', 'N/A'),
            'author': row.get('Author Name', 'N/A'),
            'claps': row.get('Number of Claps', 0),
            'reading_time': row.get('Reading Time', 'N/A'),
            'url': row.get('URL', ''),
        })
    
    return render_template('articles.html', articles=articles, message=f'Found {len(articles)} article(s)')

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Display full article content"""
    global articles_df
    load_articles()
    
    if articles_df is None or articles_df.empty:
        return redirect(url_for('articles_list'))
    
    if article_id < 0 or article_id >= len(articles_df):
        return redirect(url_for('articles_list'))
    
    article = articles_df.iloc[article_id].to_dict()
    
    # Safely convert all fields to strings and handle NaN
    def safe_str(value):
        if pd.isna(value) or value is None:
            return ''
        return str(value)
    
    # Process all article fields safely
    article['Title'] = safe_str(article.get('Title', ''))
    article['Subtitle'] = safe_str(article.get('Subtitle', ''))
    article['Full Text'] = safe_str(article.get('Full Text', ''))
    article['Author Name'] = safe_str(article.get('Author Name', ''))
    article['Author Profile URL'] = safe_str(article.get('Author Profile URL', ''))
    article['Reading Time'] = safe_str(article.get('Reading Time', ''))
    article['URL'] = safe_str(article.get('URL', ''))
    
    # Process Keywords as a list (never call .split() in template)
    keywords_str = safe_str(article.get('Keywords', ''))
    if keywords_str and keywords_str != 'N/A' and keywords_str.strip():
        # Split by comma and clean
        keywords_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
    else:
        keywords_list = []
    article['keywords_list'] = keywords_list
    
    # Process Image URLs as a list
    image_urls_str = safe_str(article.get('Image URLs', ''))
    if image_urls_str and image_urls_str != 'N/A' and image_urls_str.strip():
        image_urls_list = [url.strip() for url in image_urls_str.split(';') if url.strip()]
    else:
        image_urls_list = []
    article['image_urls_list'] = image_urls_list
    
    # Ensure numeric fields are safe
    article['Number of Images'] = int(article.get('Number of Images', 0)) if pd.notna(article.get('Number of Images')) else 0
    article['Number of External Links'] = int(article.get('Number of External Links', 0)) if pd.notna(article.get('Number of External Links')) else 0
    article['Number of Claps'] = int(article.get('Number of Claps', 0)) if pd.notna(article.get('Number of Claps')) else 0
    
    return render_template('article_detail.html', article=article, article_id=article_id)

@app.route('/api/search', methods=['POST'])
def api_search():
    """REST API endpoint for searching articles"""
    try:
        # Check if request is JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        # Get JSON data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing required field: query'}), 400
        
        query = str(data['query']).strip()
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Check if CSV exists
        if not os.path.exists(CSV_FILE):
            return jsonify({'error': 'No articles found. Please scrape some articles first.'}), 404
        
        # Reload articles before searching
        load_articles()
        
        global articles_df
        if articles_df is None or articles_df.empty:
            return jsonify({'error': 'No articles found. Please scrape some articles first.'}), 404
        
        # Perform search using TF-IDF similarity
        similar_articles = search_similar_articles(query, CSV_FILE, top_n=10)
        
        # If search returns empty but we have data, try a simpler search
        if not similar_articles and not articles_df.empty:
            # Fallback: simple keyword matching
            query_lower = query.lower()
            fallback_results = []
            for idx, row in articles_df.iterrows():
                title = str(row.get('Title', '')).lower()
                keywords = str(row.get('Keywords', '')).lower()
                text = str(row.get('Full Text', '')).lower()
                
                if query_lower in title or query_lower in keywords or query_lower in text:
                    fallback_results.append({
                        'article_id': idx,
                        'title': str(row.get('Title', 'N/A')),
                        'url': str(row.get('URL', '')),
                    })
            
            if fallback_results:
                similar_articles = fallback_results[:10]
        
        # Format response: only title and url
        results = []
        for article in similar_articles:
            results.append({
                'title': article.get('title', 'N/A'),
                'url': article.get('url', '')
            })
        
        return jsonify(results), 200
    
    except Exception as e:
        import traceback
        error_msg = f'Error: {str(e)}\n{traceback.format_exc()}'
        print(error_msg)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/search_results', methods=['POST'])
def search_results():
    """Handle search request and return results"""
    try:
        query = request.form.get('query', '').strip()
        
        if not query:
            return render_template('results.html', 
                                 query='', 
                                 results=[], 
                                 message='Please enter a search query')
        
        # Reload articles before searching
        load_articles()
        
        # Check if CSV exists and has data
        if not os.path.exists(CSV_FILE):
            return render_template('results.html', 
                                 query=query, 
                                 results=[], 
                                 message='No articles found. Please scrape some articles first.')
        
        global articles_df
        if articles_df is None or articles_df.empty:
            return render_template('results.html', 
                                 query=query, 
                                 results=[], 
                                 message='No articles found. Please scrape some articles first.')
        
        # Perform search - reload CSV fresh for search
        similar_articles = search_similar_articles(query, CSV_FILE, top_n=10)
        
        # If search returns empty but we have data, try a simpler search
        if not similar_articles and not articles_df.empty:
            # Fallback: simple keyword matching
            query_lower = query.lower()
            fallback_results = []
            for idx, row in articles_df.iterrows():
                title = str(row.get('Title', '')).lower()
                keywords = str(row.get('Keywords', '')).lower()
                text = str(row.get('Full Text', '')).lower()
                
                if query_lower in title or query_lower in keywords or query_lower in text:
                    fallback_results.append({
                        'article_id': idx,
                        'title': str(row.get('Title', 'N/A')),
                        'url': str(row.get('URL', '')),
                        'similarity': 50.0,  # Default similarity for fallback
                        'claps': int(row.get('Number of Claps', 0)) if pd.notna(row.get('Number of Claps')) else 0,
                        'author': str(row.get('Author Name', 'N/A')),
                        'reading_time': str(row.get('Reading Time', 'N/A')),
                    })
            
            if fallback_results:
                similar_articles = fallback_results[:10]
        
        if not similar_articles:
            return render_template('results.html', 
                                 query=query, 
                                 results=[], 
                                 message='No similar articles found. Try different keywords.')
        
        return render_template('results.html', 
                             query=query, 
                             results=similar_articles,
                             message=f'Found {len(similar_articles)} similar articles')
    
    except Exception as e:
        import traceback
        error_msg = f'Error: {str(e)}\n{traceback.format_exc()}'
        print(error_msg)
        return render_template('results.html', 
                             query=query if 'query' in locals() else '', 
                             results=[], 
                             message=f'Search error: {str(e)}')

if __name__ == '__main__':
    # Initialize CSV on startup
    init_csv()
    
    # Load articles into memory
    load_articles()
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Disable debug mode in production (set DEBUG=False in environment for production)
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

