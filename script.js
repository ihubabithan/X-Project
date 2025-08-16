const express = require('express');
const puppeteer = require('puppeteer');

const app = express();

app.get('/tweets/:username', async (req, res) => {
  const username = req.params.username;
  const url = `https://nitter.net/${username}`;

  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    );
    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.waitForSelector('.timeline-item');

    // Extract tweets
    const tweets = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.timeline-item'))
        .map(tweet => {
          const text = tweet.querySelector('.tweet-content')?.innerText || '';
          const date = tweet.querySelector('.tweet-date a')?.getAttribute('title') || '';
          return { text, date };
        });
    });

    await browser.close();
    res.json({ username, tweets });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch tweets.', details: err.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
