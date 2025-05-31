# Rscraper: A simple subreddit scraper
  Steve Fan @2025-05-27

# What is this?
  I need to download some posts and images of comments from r/PhotoRequest and create this simple tool
  Later I generalized it for any other subreddit. This tool uses Reddit's API, and as of 2023, Reddit's API  has limits.
  Check out their terms. 

  This tool downloads the latest posts and images of comments, save the post in json format and text format, the title and selftext are sent to OpenAI for translation. The translation is saved in json and text file. Comment images are saved in
  comments folder.

  You need to use your own Reddit API keys and your own Open API keys. Set them in .env file.


# Usage:
**Reddit Scraper for subreddits**

## Options

- `-h`, `--help`  
  Show this help message and exit.

- `-o OUTPUT`, `--output OUTPUT`  
  Output directory path (default: `data`).

- `-d DEV_MODE`, `--dev-mode`  
  Run in development mode (limit to 3 comments), skip this flag for prod mode.

- `-r SUBREDDIT`, `--subreddit SUBREDDIT`  
  Subreddit to scrape (default: `PhotoshopRequest`).

- `-f {Paid,Free,All}`, `--flair {Paid,Free,All}`  
  Filter posts by flair (`Paid`, `Free`, or `All`). Default: `Paid`.

- `-t {Chinese,Spanish,French,German,Japanese,Korean,Russian}`, `--target-lang {Chinese,Spanish,French,German,Japanese,Korean,Russian}`  
  Target language for translation (default: `Chinese`).

- `-c COUNT`, `--count COUNT`  
  Number of posts to download (default: `5`).

# Get started
1. download and install uv
2. in project folder, run `uv pip install -r requirements.txt`
3. run command: `uv run main.py -d False -r PhotoRequest -f Paid -o ./data -t Japanese -c 10`

~ sfan