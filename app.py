import requests
import xml.etree.ElementTree as ET
from flask import Flask, send_file
import os

# Function to fetch RSS feed
def fetch_rss_feed(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None

# Function to parse RSS feed
def parse_rss_feed(xml_data):
    if not xml_data:
        print("No XML data to parse.")
        return []
    try:
        root = ET.fromstring(xml_data)
        items = []
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else 'No title'
            link = item.find('link').text if item.find('link') is not None else '#'
            description = item.find('description').text if item.find('description') is not None else 'No description'
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No date'
            media = item.find('{http://search.yahoo.com/mrss/}content')
            media_url = media.attrib['url'] if media is not None else ''
            items.append({
                'title': title,
                'link': link,
                'description': description,
                'pub_date': pub_date,
                'media_url': media_url
            })
        return items
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")
        return []

# Function to generate HTML file
def generate_html(items, css_file='static/style.css'):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{css_file}">
        <title>Custom RSS Feed</title>
    </head>
    <body>
        <h1>Custom RSS Feed</h1>
        <div class="rss-feed">
    """
    for item in items:
        html_content += f"""
        <div class="rss-item">
            <h2><a href="{item['link']}">{item['title']}</a></h2>
            <p>{item['description']}</p>
            <span>{item['pub_date']}</span>
            <div class="media">
                {'<img src="' + item['media_url'] + '" alt="Media content">' if item['media_url'] else ''}
            </div>
        </div>
        """
    html_content += """
        </div>
    </body>
    </html>
    """
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w') as file:
        file.write(html_content)

# Sample CSS content
css_content = """
body {
    font-family: Arial, sans-serif;
}

h1 {
    text-align: center;
}

.rss-feed {
    width: 80%;
    margin: 0 auto;
}

.rss-item {
    border-bottom: 1px solid #ccc;
    padding: 10px 0;
}

.rss-item h2 a {
    text-decoration: none;
    color: #333;
}

.rss-item p {
    font-size: 14px;
    color: #666;
}

.rss-item span {
    font-size: 12px;
    color: #999;
}

.media img {
    max-width: 100%;
    height: auto;
}
"""

# Save CSS content to file
os.makedirs('static', exist_ok=True)
with open('static/style.css', 'w') as file:
    file.write(css_content)

# Flask app to serve the HTML
app = Flask(__name__)

@app.route('/')
def home():
    return send_file('templates/index.html')

if __name__ == '__main__':
    rss_url = 'https://www.yahoo.com/news/rss'  # Yahoo News - Top Stories RSS feed URL
    xml_data = fetch_rss_feed(rss_url)
    items = parse_rss_feed(xml_data)
    generate_html(items)
    app.run(debug=True)
