import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import requests
from xml.etree import ElementTree as ET
import random
import os
import time
import subprocess
import quantstats as qs 

# Ignore all warnings
import warnings
warnings.filterwarnings("ignore")

# Function to fetch stock data
def fetch_stock_data(ticker):
    return yf.download(ticker, period="30d", interval="1d")

# Function to calculate pivot points and support/resistance levels
def calculate_pivot_points(ndata):
    high = ndata['High'].round(2)
    low = ndata['Low'].round(2)
    close = ndata['Close'].round(2)
    open_price = ndata['Open'].round(2)

    pivot_point = (high + low + close) / 3
    support1 = (2 * pivot_point) - high
    support2 = pivot_point - (high - low)
    support3 = low - 2 * (high - pivot_point)
    resistance1 = (2 * pivot_point) - low
    resistance2 = pivot_point + (high - low)
    resistance3 = high + 2 * (pivot_point - low)

    return pd.DataFrame({
        'High': high,
        'Low': low,
        'Close': close,
        'Open': open_price,
        'R3': resistance3,
        'R2': resistance2,
        'R1': resistance1,
        'Pivot_Point': pivot_point,
        'S1': support1,
        'S2': support2,
        'S3': support3,
    }).round(2)

# Function to plot pivot points
def plot_pivot_points(df, ticker):
    df_except_last_row = df.iloc[:-1]

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_except_last_row[['Close', 'R3', 'R2', 'R1', 'Pivot_Point', 'S1', 'S2', 'S3']])
    plt.title(f'{ticker} Price and Pivot Points')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=90)

    plot_filename = f"{ticker}_pivot_plot.png"
    plt.savefig(plot_filename, bbox_inches='tight')
    plt.show()
    return plot_filename


css_content = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 20px;
    }
    
    body pre {
        font-size: 24px;
    }
    .feed-container {
        margin-bottom: 20px;
    }
    .feed-item {
        border: 1px solid #ccc;
        padding: 10px;
        margin-bottom: 10px;
    }
    .feed-item h3 {
        margin: 0 0 10px 0;
    }
    .feed-item p {
        margin: 0 0 10px 0;
    }
    .text-column, .image-column {
    flex: 1;
    padding: 10px;
}
.container {
    display: flex;
    justify-content: center;
    margin: 20px;
    width: 100%;
}
.text-column {
    width: 30%;
 

}
.image-column{
    width: 60%;


}

.image-column img {
    width: 100%;

    height: auto;
    display: block;
    margin: 0 auto;
}
/* Navbar styling */
.navbar {
    width: 100%;
    background-color: #333;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    color: white;
}

.logo {
    font-size: 1.5em;
    font-weight: bold;
}

.nav-links {
    list-style: none;
    display: flex;
    margin: 0;
    padding: 0;
}

.nav-links li {
    margin-left: 20px;
}

.nav-links a {
    color: white;
    text-decoration: none;
    font-size: 1em;
}

.nav-links a:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
        align-items: center;
    }

    .text-column, .image-column {
        width: 100%;
    }
}
    """


# Function to save pivot data to HTML
def save_pivot_data_html(df, ticker, plot_filename):
    last_row = df.iloc[-2]
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{ticker} Pivot Points</title>
        <style>
         {css_content}
        </style>
    </head>
    <body>
          <div class="container">
        <div class="text-column">
            <pre>{last_row}</pre>
        </div>
        <div class="image-column">
            <img src="{plot_filename}" alt="{ticker} Pivot Plot">
        </div>
    </div>
    </body>
    </html>
    """
    file_path = os.path.join(os.getcwd(), f"{ticker}_pivot_points.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML file saved successfully: {file_path}")
    return file_path

# Function to fetch RSS feed
def fetch_rss_feed(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {url} - {e}")
        return None

# Function to parse RSS feed
def parse_rss_feed(xml_data):
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
        return items[:3]
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")
        return []
    except Exception as ex:
        print(f"Error processing RSS feed data: {ex}")
        return []

# Function to generate HTML content
def generate_html(feed_urls, css_content):
    random.shuffle(feed_urls)

    try:
        futures_symbol = "NQ=F"
        data = yf.Ticker(futures_symbol)
        futures_data = data.history(period="1y")
        
        futures_data['Return'] = futures_data['Close'].pct_change()
        
        initial_investment = 100000
        futures_data['Balance'] = initial_investment * (1 + futures_data['Return']).cumprod()
        
        futures_data['Return'].iloc[0] = 0
        futures_data['Balance'].iloc[0] = initial_investment
        
        futures_data['Balance'] = futures_data['Balance'].round(2)

        file_path = "NQ_futures_with_balance_and_return.csv"
        futures_data.to_csv(file_path)
        
        returns = futures_data['Return']
        returns.index = pd.to_datetime(returns.index)
        
        qs.reports.html(returns, output='NQ_futures_report.html')
        
    except Exception as e:
        print(f"Error generating QuantStat HTML report: {e}")
        return ""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        {css_content}
        </style>
        <title>Wolfrank's Nasdaq Trading Tools + RSS Feed</title>
    </head>
    <body>
     <nav class="navbar">
        <div class="logo">
            <img src="nqlogo.png" alt="Logo">
        </div>
      
    </nav>
        <h3> Wolfrank's Nasdaq Trading Tools + RSS Feed </h3>
        <hr>
          <div class="feed-container"> 
        <h4>This site includes returns on the index, pivot points and other statistics along with a RSS feed.</h4>
        </div>
        
        <div class="feed-container"> 
        <object type="text/html" data="NQ=F_pivot_points.html" width="100%" height="1000"></object>
        <object type="text/html" data="NQ_futures_report.html" width="100%" height="3900"></object>
 
    """

    for url in feed_urls:
        xml_data = fetch_rss_feed(url)
        if xml_data:
            feed_data = parse_rss_feed(xml_data)
            if feed_data:
                for item in feed_data:
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

# Function to save HTML content to a file
def save_html(html, filename="index.html"):
    cwd = os.getcwd()
    file_path = os.path.join(cwd, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML file saved successfully: {file_path}")
    return file_path

# Function to commit file to GitHub repository
def commit_and_push_to_github(file_path, commit_message):
    try:
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Changes committed and pushed to GitHub successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        return False

# Main job function to generate RSS feed HTML and push to GitHub
def job():
    ticker = 'NQ=F'
    ndata = fetch_stock_data(ticker)
    pivot_data = calculate_pivot_points(ndata)
    plot_filename = plot_pivot_points(pivot_data, ticker)
    pivot_html_path = save_pivot_data_html(pivot_data, ticker, plot_filename)

    rss_urls = [
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://aws.amazon.com/blogs/aws/feed",
        "https://ir.nasdaq.com/rss/news-releases.xml?items=15"
    ]

    css_content = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 20px;
    }
    .feed-container {
        margin-bottom: 20px;
        width: 90%;
    }
    .feed-item {
        border: 1px solid #ccc;
        padding: 10px;
        margin-bottom: 10px;
    }
    .feed-item h3 {
        margin: 0 0 10px 0;
    }
    .feed-item p {
        margin: 0 0 10px 0;
    }
   /* Navbar styling */
.navbar {
    width: 100%;
    background-color: #ffff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    color: white;
}

.logo img {
    height: 40px;
}

.nav-links {
    list-style: none;
    display: flex;
    margin: 0;
    padding: 0;
}

.nav-links li {
    margin-left: 20px;
}

.nav-links a {
    color: #00000;
    text-decoration: none;
    font-size: 1em;
}

.nav-links a:hover {
    text-decoration: underline;
}
    """

    html_content = generate_html(rss_urls, css_content)
    html_path = save_html(html_content)

    commit_message = f"Update RSS feed HTML on {time.strftime('%Y-%m-%d %H:%M:%S')}"
    commit_and_push_to_github(html_path, commit_message)

# Run the job function
if __name__ == "__main__":
    job()
