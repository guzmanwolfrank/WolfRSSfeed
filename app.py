import requests
import xml.etree.ElementTree as ET
from flask import Flask, send_file

# Function to fetch RSS feed
def fetch_rss_feed(url):
    response = requests.get(url)
    return response.text

# Function to parse RSS feed
def parse_rss_feed(xml_data):
    root = ET.fromstring(xml_data)
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text
        pub_date = item.find('pubDate').text
        items.append({
            'title': title,
            'link': link,
            'description': description,
            'pub_date': pub_date
        })
    return items

# Function to generate HTML file
def generate_html(items, css_file='style.css'):
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
        </div>
        """
    html_content += """
        </div>
    </body>
    </html>
    """
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
"""

# Save CSS content to file
with open('static/style.css', 'w') as file:
    file.write(css_content)

# Flask app to serve the HTML
app = Flask(__name__)

@app.route('/')
def home():
    return send_file('templates/index.html')

if __name__ == '__main__':
    rss_url = 'https://example.com/rss'  # Replace with actual RSS feed URL
    xml_data = fetch_rss_feed(rss_url)
    items = parse_rss_feed(xml_data)
    generate_html(items)
    app.run(debug=True)
