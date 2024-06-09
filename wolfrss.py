import requests
from xml.etree import ElementTree as ET
import random
import os
import time
import subprocess


def fetch_rss_feed(url):
    """Fetches RSS feed content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {url} - {e}")
        return None

def parse_rss_feed(xml_data):
    """Parses RSS feed data and extracts relevant information."""
    if not xml_data:
        return []

    try:
        root = ET.fromstring(xml_data)
        items = []
        for index, item in enumerate(root.findall('.//item')):
            if index >= 3:
                break
            title = item.find('title').text if item.find('title') is not None else 'No title'
            link = item.find('link').text if item.find('link') is not None else '#'
            description = item.find('description').text if item.find('description') is not None else 'No description'
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No date'
            media_content = item.find('{http://search.yahoo.com/mrss/}content')
            media_url = media_content.attrib['url'] if media_content is not None and 'url' in media_content.attrib else ''
            items.append({
                'title': title,
                'link': link,
                'description': description,
                'pub_date': pub_date,
                'media_url': media_url
            })
        return items[:3]  # Limit to 3 items per feed
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")
        return []
    except Exception as ex:
        print(f"Error processing RSS feed data: {ex}")
        return []

def generate_html(feed_urls, css_content):
    """Generates HTML content with embedded CSS and feed item details."""
    random.shuffle(feed_urls)  # Shuffle feed URLs for random order

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        {css_content}
        </style>
        <title>Wolfrank's Custom RSS Feed Aggregator</title>
    </head>
    <body>
        <h1>Wolfrank's Custom RSS Feed Aggregator</h1>
        <div class="feed-container">
    """

    for url in feed_urls:
        xml_data = fetch_rss_feed(url)
        if xml_data:
            feed_data = parse_rss_feed(xml_data)
            if feed_data:
                for item in feed_data:
                    # Ensure links open in a new tab by adding target="_blank"
                    html_content += f"""
                    <div class="feed-item">
                        <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
                        <p>{item['description']}</p>
                        <span>{item['pub_date']}</span>
                        {'<br><img src="' + item['media_url'] + '" alt="Media content">' if item['media_url'] else ''}
                    </div>
                    """
            else:
                html_content += f"\n<p>No valid items found in RSS feed: {url}</p>"
        else:
            html_content += f"\n<p>Error fetching RSS feed: {url}</p>"

    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

def save_html(html, filename="custom_rss_feed.html"):
    """Saves the generated HTML content to a file."""
    cwd = os.getcwd()
    file_path = os.path.join(cwd, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML file saved successfully: {file_path}")
    return file_path

def commit_and_push_to_github(file_path, commit_message):
    """Commits the file to the local git repository and pushes it to GitHub."""
    try:
        # Add the file to staging
        subprocess.run(["git", "add", file_path], check=True)
        # Commit the file
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        # Push the changes to the main branch
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Changes committed and pushed to GitHub successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        return False

def job():
    """Job to generate RSS feed HTML and push to GitHub."""
    feed_urls = [
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://aws.amazon.com/blogs/aws/feed",
        "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss"
    ]
    
    css_content = """
    body {
        font-family: Arial, sans-serif;
    }

    h1 {
        text-align: center;
    }

    .feed-container {
        width: 80%;
        margin: 0 auto;
    }

    .feed-item {
        border-bottom: 1px solid #ccc;
        padding: 10px 0;
    }

    .feed-item h3 a {
        text-decoration: none;
        color: #000;
    }
    """

    html = generate_html(feed_urls, css_content)
    filename = "index.html"
    file_path = save_html(html, filename)
    commit_message = f"Update RSS feed - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    success = commit_and_push_to_github(file_path, commit_message)
    if success:
        print(f"File published successfully to GitHub: {file_path}")
    else:
        print(f"Failed to publish file to GitHub: {file_path}")



# Run the job once
job()
