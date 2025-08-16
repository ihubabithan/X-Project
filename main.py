from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re

def parse_tweet_time(date_span, now):
    tweet_time_str = date_span.get("title", "")
    tweet_time = None
    try:
        tweet_time = datetime.strptime(tweet_time_str, "%b %d, %Y · %I:%M %p UTC")
        return tweet_time
    except Exception:
        rel_time = date_span.get_text(strip=True)
        match = re.match(r"(\d+)([mh])", rel_time)
        if match:
            val, unit = match.groups()
            if unit == "m":
                tweet_time = now - timedelta(minutes=int(val))
            elif unit == "h":
                tweet_time = now - timedelta(hours=int(val))
            return tweet_time
    return None


def get_last_24h_tweets(username, nitter_instance="https://nitter.net", max_pages=3, min_delay=5):
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    tweets = []
    now = datetime.utcnow()
    cutoff = now - timedelta(days=1)

    url = f"{nitter_instance}/{username}"
    page = 0
    cursor = None

    try:
        while page < max_pages:
            fetch_url = f"{url}?cursor={cursor}" if cursor else url
            print(f"Fetching page: {fetch_url}")
            driver.get(fetch_url)
            time.sleep(5)  # Wait for JS content to load

            soup = BeautifulSoup(driver.page_source, "html.parser")
            tweet_items = soup.select("div.timeline-item")
            print(f"Found {len(tweet_items)} tweets on this page.")

            found_any = False
            for tweet_div in tweet_items:
                content = tweet_div.select_one(".tweet-content")
                date_span = tweet_div.select_one(".tweet-date a")
                if not (content and date_span):
                    continue
                text = content.get_text(strip=True)
                tweet_time = parse_tweet_time(date_span, now)
                if not tweet_time:
                    continue

                if tweet_time >= cutoff:
                    found_any = True
                    link = tweet_div.select_one("a.tweet-link").get("href")
                    full_link = f"{nitter_instance}{link}"
                    tweets.append({
                        "time": tweet_time.strftime('%Y-%m-%d %H:%M'),
                        "text": text,
                        "url": full_link
                    })

            # Pagination (get next cursor)
            cursor_tag = soup.select_one(".show-more a")
            cursor = cursor_tag["href"].split("cursor=")[-1] if cursor_tag else None
            if not found_any or not cursor:
                break

            page += 1
            time.sleep(min_delay)  # Delay before next page
    finally:
        driver.quit()

    return tweets


if __name__ == "__main__":
    username = "kyalashish"  # Change username as needed
    tweets = get_last_24h_tweets(username)
    print(f"Tweets in last 24h: {len(tweets)}")
    for t in tweets:
        print(f"{t['time']} - {t['text']}\nLink: {t['url']}\n")
