"""
Medium Article Scraper Module
Handles scraping of Medium articles and similarity search
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpus/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def get_headers():
    """Return headers to mimic a browser request"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

def extract_text_from_element(element):
    """Extract text content from BeautifulSoup element"""
    if element:
        return element.get_text(strip=True)
    return ''

def extract_number(text):
    """Extract number from text (e.g., '1.2K' -> 1200)"""
    if not text:
        return 0
    
    text = text.strip().upper()
    
    # Remove commas
    text = text.replace(',', '')
    
    # Handle K (thousands) and M (millions)
    if 'K' in text:
        number = float(text.replace('K', '')) * 1000
    elif 'M' in text:
        number = float(text.replace('M', '')) * 1000000
    else:
        try:
            number = float(text)
        except:
            number = 0
    
    return int(number)

def scrape_medium_article(url):
    """
    Scrape a Medium article and extract all required fields
    
    Returns:
        dict: Dictionary containing article data or None if scraping fails
    """
    try:
        # Validate URL
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Make request
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Title
        title = ''
        title_elem = soup.find('h1')
        if not title_elem:
            title_elem = soup.find('meta', property='og:title')
            if title_elem:
                title = title_elem.get('content', '')
        else:
            title = extract_text_from_element(title_elem)
        
        # Extract Subtitle
        subtitle = ''
        subtitle_elem = soup.find('h2')
        if not subtitle_elem:
            subtitle_elem = soup.find('meta', property='og:description')
            if subtitle_elem:
                subtitle = subtitle_elem.get('content', '')
        else:
            subtitle = extract_text_from_element(subtitle_elem)
        
        # Extract Full Text
        full_text = ''
        # Try multiple selectors for article content
        content_selectors = [
            'article',
            '[data-testid="post-content"]',
            '.postArticle-content',
            '.articleBody',
            'main article',
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Get all paragraph text
                paragraphs = content_elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                full_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                if full_text:
                    break
        
        # If still no text, try getting all p tags
        if not full_text:
            paragraphs = soup.find_all('p')
            full_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # Extract Images
        images = soup.find_all('img')
        image_urls = []
        for img in images:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src and src.startswith('http'):
                image_urls.append(src)
        
        num_images = len(image_urls)
        image_urls_str = '; '.join(image_urls[:50])  # Limit to 50 URLs
        
        # Extract External Links
        links = soup.find_all('a', href=True)
        external_links = []
        for link in links:
            href = link.get('href', '')
            if href.startswith('http') and 'medium.com' not in href.lower():
                external_links.append(href)
        
        num_external_links = len(set(external_links))  # Remove duplicates
        
        # Extract Author Name
        author_name = ''
        author_elem = soup.find('meta', property='article:author')
        if author_elem:
            author_name = author_elem.get('content', '')
        
        if not author_name:
            author_elem = soup.find('a', {'data-action': 'show-user-card'})
            if author_elem:
                author_name = extract_text_from_element(author_elem)
        
        if not author_name:
            author_elem = soup.find('a', href=re.compile(r'/@'))
            if author_elem:
                author_name = extract_text_from_element(author_elem)
        
        # Extract Author Profile URL
        author_profile_url = ''
        author_link = soup.find('a', href=re.compile(r'/@'))
        if author_link:
            href = author_link.get('href', '')
            if href.startswith('/'):
                author_profile_url = 'https://medium.com' + href
            elif href.startswith('http'):
                author_profile_url = href
        
        # Extract Number of Claps
        claps = 0
        clap_elem = soup.find('button', {'data-testid': 'clap-button'})
        if clap_elem:
            clap_text = extract_text_from_element(clap_elem)
            claps = extract_number(clap_text)
        
        # Try alternative clap selectors
        if claps == 0:
            clap_selectors = [
                '[data-testid="clap-count"]',
                '.clap-count',
                'button[aria-label*="clap"]',
            ]
            for selector in clap_selectors:
                clap_elem = soup.select_one(selector)
                if clap_elem:
                    clap_text = extract_text_from_element(clap_elem)
                    claps = extract_number(clap_text)
                    if claps > 0:
                        break
        
        # Extract Reading Time
        reading_time = ''
        reading_elem = soup.find('span', string=re.compile(r'\d+\s*min'))
        if reading_elem:
            reading_time = extract_text_from_element(reading_elem)
        
        if not reading_time:
            reading_elem = soup.find('span', string=re.compile(r'\d+\s*minute'))
            if reading_elem:
                reading_time = extract_text_from_element(reading_elem)
        
        # Extract Keywords (from meta tags)
        keywords = []
        keyword_elem = soup.find('meta', {'name': 'keywords'})
        if keyword_elem:
            keywords_str = keyword_elem.get('content', '')
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        
        # If no keywords from meta, try extracting from tags
        if not keywords:
            tag_elems = soup.find_all('a', href=re.compile(r'/tag/'))
            keywords = [extract_text_from_element(tag) for tag in tag_elems[:10]]
            keywords = [k for k in keywords if k]
        
        keywords_str = ', '.join(keywords[:20])  # Limit to 20 keywords
        
        # Return dictionary with all extracted data
        return {
            'Title': title or 'N/A',
            'Subtitle': subtitle or 'N/A',
            'Full Text': full_text or 'N/A',
            'Number of Images': num_images,
            'Image URLs': image_urls_str or 'N/A',
            'Number of External Links': num_external_links,
            'Author Name': author_name or 'N/A',
            'Author Profile URL': author_profile_url or 'N/A',
            'Number of Claps': claps,
            'Reading Time': reading_time or 'N/A',
            'Keywords': keywords_str or 'N/A',
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def preprocess_text(text):
    """Preprocess text for TF-IDF: lowercase, remove punctuation, tokenize"""
    if pd.isna(text) or not text:
        return ''
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
    
    return ' '.join(tokens)

def search_similar_articles(query, csv_file, top_n=10):
    """
    Search for similar articles using TF-IDF cosine similarity
    
    Args:
        query: Search query string
        csv_file: Path to CSV file with scraped articles
        top_n: Number of top results to return
    
    Returns:
        list: List of dictionaries with article info and similarity scores
    """
    try:
        # Read CSV fresh
        df = pd.read_csv(csv_file)
        
        if df.empty:
            return []
        
        # Store original index before any filtering
        df['original_index'] = df.index
        
        # Fill NaN values with empty strings FIRST
        df['Title'] = df['Title'].fillna('').astype(str)
        df['Subtitle'] = df['Subtitle'].fillna('').astype(str)
        df['Full Text'] = df['Full Text'].fillna('').astype(str)
        df['Keywords'] = df['Keywords'].fillna('').astype(str)
        
        # Filter out rows with empty or invalid data
        # Ensure we have at least Title or Full Text
        df = df[
            (df['Title'].str.strip() != '') & 
            (df['Title'] != 'N/A') &
            (df['Full Text'].str.strip() != '') & 
            (df['Full Text'] != 'N/A')
        ]
        
        if df.empty:
            return []
        
        # Combine title, subtitle, keywords, and full text for each article
        # Prioritize title and keywords for better matching
        df['combined_text'] = (
            df['Title'].astype(str) + ' ' + 
            df['Title'].astype(str) + ' ' +  # Double weight title
            df['Keywords'].astype(str) + ' ' +
            df['Keywords'].astype(str) + ' ' +  # Double weight keywords
            df['Subtitle'].astype(str) + ' ' + 
            df['Full Text'].astype(str)
        )
        
        # Remove empty strings
        df = df[df['combined_text'].str.strip() != '']
        
        if df.empty:
            return []
        
        # Preprocess texts
        df['processed_text'] = df['combined_text'].apply(preprocess_text)
        
        # Remove rows with empty processed text
        df = df[df['processed_text'].str.strip() != '']
        
        if df.empty:
            return []
        
        # Preprocess query
        processed_query = preprocess_text(query)
        
        if not processed_query or processed_query.strip() == '':
            return []
        
        # Create TF-IDF vectorizer
        # Use min_df=0 to handle small datasets
        vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=0)
        
        # Get all processed texts
        all_texts = list(df['processed_text'].astype(str))
        
        # Ensure we have valid texts
        if not all_texts or len(all_texts) == 0:
            return []
        
        # Fit vectorizer on documents
        try:
            doc_vectors = vectorizer.fit_transform(all_texts)
        except ValueError as e:
            print(f"Vectorizer error: {str(e)}")
            return []
        
        # Transform query
        try:
            query_vector = vectorizer.transform([processed_query])
        except Exception as e:
            print(f"Query transform error: {str(e)}")
            return []
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, doc_vectors)[0]
        
        # Add similarity scores to dataframe
        df = df.copy()
        df['similarity'] = similarities
        
        # Don't filter zero similarity - show all results sorted by similarity
        # This ensures we always return results if data exists
        
        # Sort by similarity (descending), then by claps (descending)
        df_sorted = df.sort_values(
            by=['similarity', 'Number of Claps'], 
            ascending=[False, False]
        )
        
        # Get top N results (even if similarity is low)
        top_results = df_sorted.head(top_n)
        
        # Format results
        results = []
        for idx, row in top_results.iterrows():
            # Get original index (row number from CSV)
            article_id = int(row['original_index']) if 'original_index' in row else int(idx)
            results.append({
                'article_id': article_id,  # Original index from CSV
                'title': str(row.get('Title', 'N/A')),
                'url': str(row.get('URL', '')),
                'similarity': round(float(row['similarity']) * 100, 2),  # Convert to percentage
                'claps': int(row.get('Number of Claps', 0)) if pd.notna(row.get('Number of Claps')) else 0,
                'author': str(row.get('Author Name', 'N/A')),
                'reading_time': str(row.get('Reading Time', 'N/A')),
            })
        
        return results
    
    except Exception as e:
        import traceback
        print(f"Error in search: {str(e)}")
        print(traceback.format_exc())
        return []

