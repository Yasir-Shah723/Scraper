# DS Assignment 4 - Medium Article Scraper & Search

A complete web application for scraping Medium articles and searching for similar articles using TF-IDF similarity.

## Features

### Part A - Scraping
- **Web Interface**: Paste multiple Medium article URLs and scrape them
- **Data Extraction**: Extracts Title, Subtitle, Full Text, Images, Links, Author Info, Claps, Reading Time, and Keywords
- **CSV Storage**: All scraped data is saved to `scrapping_results.csv`
- **Error Handling**: Gracefully handles invalid URLs and missing fields

### Part B - Search
- **Web Search Interface**: Search articles through the web UI
- **REST API**: Programmatic access via `/api/search` endpoint
- **Similarity Search**: Uses TF-IDF (Term Frequency-Inverse Document Frequency) to find similar articles
- **Smart Ranking**: Results sorted by similarity score, then by number of claps
- **Top 10 Results**: Returns the 10 most similar articles
- **Beautiful UI**: Clean, modern interface with responsive design

## Project Structure

```
/project_root
│── app.py                    # Flask application (main entry point)
│── scraper.py                # Scraping and search logic
│── templates/
│   │── index.html            # Scraping page
│   │── search.html           # Search page
│   │── results.html          # Search results display
│── static/
│   │── style.css             # Styling
│── scrapping_results.csv     # Scraped data (created automatically)
│── requirements.txt          # Python dependencies
│── README.md                 # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

Open your terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask (web framework)
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)
- pandas (data manipulation)
- scikit-learn (TF-IDF similarity)
- nltk (natural language processing)

### Step 2: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000` (or the port specified by the PORT environment variable).

### Step 3: Open in Browser

Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use

### Scraping Articles

1. Go to the **Scrape Articles** page (home page)
2. Paste one or more Medium article URLs (one per line) in the text area
   - Example:
     ```
     https://medium.com/@author/article-title
     https://medium.com/@author/another-article
     ```
3. Click **"Scrape Articles"** button
4. Wait for the scraping to complete
5. All data is automatically saved to `scrapping_results.csv`

### Searching Articles

1. Go to the **Search Articles** page
2. Enter keywords or text in the search box
   - Example: "machine learning", "Python tutorials", "data science"
3. Click **"Search Similar Articles"** button
4. View the top 10 most similar articles displayed as cards
5. Click on any article card to open it in a new tab

### REST API - Programmatic Search

The application provides a REST API endpoint for programmatic access to search functionality.

#### Endpoint: `POST /api/search`

**Request:**
- Content-Type: `application/json`
- Body:
  ```json
  {
    "query": "machine learning neural networks"
  }
  ```

**Response:**
- Content-Type: `application/json`
- Status: `200 OK` (success) or `400/404/500` (errors)
- Body (success):
  ```json
  [
    {
      "title": "Intro to Machine Learning",
      "url": "https://medium.com/@author/intro-to-ml"
    },
    {
      "title": "Deep Learning Explained",
      "url": "https://medium.com/@author/deep-learning"
    }
  ]
  ```

**Example using curl:**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning neural networks"}'
```

**Example using Python:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/search',
    json={'query': 'machine learning neural networks'}
)
results = response.json()
for article in results:
    print(f"{article['title']}: {article['url']}")
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid query field
- `404 Not Found`: No articles found in CSV
- `500 Internal Server Error`: Server error

**API Features:**
- Uses TF-IDF similarity on Title + Full Text + Keywords
- Sorts results by similarity score, then by number of claps
- Returns top 10 most similar articles
- Returns only `title` and `url` fields
- Works independently of the web UI

## Deployment on Render

[Render](https://render.com) is a cloud platform that makes deployment easy. Follow these steps:

### Step 1: Prepare Your Code

1. Make sure all files are committed to a Git repository (GitHub, GitLab, or Bitbucket)
2. Ensure `requirements.txt` is in the root directory
3. Ensure `app.py` is in the root directory

### Step 2: Create Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up for a free account (use GitHub/GitLab/Bitbucket to sign in)

### Step 3: Create New Web Service

1. Click **"New +"** button
2. Select **"Web Service"**
3. Connect your Git repository (GitHub/GitLab/Bitbucket)
4. Select the repository containing this project

### Step 4: Configure Service

Fill in the following settings:

- **Name**: `medium-scraper` (or any name you prefer)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Plan**: Select **Free** plan

### Step 5: Environment Variables (Optional)

The app automatically uses the PORT environment variable provided by Render. No additional configuration needed!

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for the build to complete (usually 2-3 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

### Step 7: Access Your App

- Open the provided URL in your browser
- Start scraping and searching articles!

## Deployment on Railway

[Railway](https://railway.app) is another excellent deployment option:

### Step 1: Create Railway Account

1. Go to [https://railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository

### Step 3: Configure

Railway will automatically detect Python and install dependencies from `requirements.txt`.

### Step 4: Set Start Command

In the project settings, set the start command:
```
python app.py
```

### Step 5: Deploy

Railway will automatically deploy. Your app will be live at a Railway-provided URL.

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, the app will automatically use the PORT environment variable or you can change it in `app.py`.

### NLTK Data Download
On first run, NLTK may download required data automatically. If it fails, run:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### CSV File Not Created
The CSV file is created automatically when you first scrape an article. Make sure the app has write permissions in the project directory.

### Scraping Fails
- Check if the URL is valid and accessible
- Some Medium articles may require authentication
- Rate limiting: Wait a few seconds between scraping multiple articles

## Technical Details

### Scraping Method
- Uses `requests` library to fetch HTML
- Parses HTML with `BeautifulSoup`
- Extracts data using CSS selectors and meta tags
- Handles missing fields gracefully

### Search Method
- Preprocesses text (lowercase, remove punctuation, tokenize)
- Uses TF-IDF vectorization with scikit-learn
- Calculates cosine similarity between query and articles
- Ranks by similarity score, then by claps

## License

This project is created for educational purposes (DS Assignment 4).

## Support

For issues or questions, check:
- Flask documentation: https://flask.palletsprojects.com/
- BeautifulSoup documentation: https://www.crummy.com/software/BeautifulSoup/
- scikit-learn documentation: https://scikit-learn.org/

---

**Happy Scraping! 🚀**

