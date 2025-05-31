Rscraper: A Simple Subreddit Scraper & Translator

Created by Steve Fan, 2025-05-27

⸻

📚 Project Overview

Rscraper is a lightweight Python tool designed to scrape posts and comment images from any subreddit.

Originally built for r/PhotoRequest, the tool has since been generalized and supports:
	•	Downloading recent subreddit posts
	•	Saving posts in JSON and text format
	•	Translating post titles and selftexts via OpenAI API
	•	Saving translations alongside original data
	•	Downloading comment images

⸻

⚠️ Important Notes
	•	This tool uses Reddit’s API, which as of 2023 has usage limitations — please review their API Terms of Service.
	•	You must provide your own Reddit API keys and OpenAI API key — these are stored securely in a .env file.

⸻

✨ Features

✅ Scrape posts from any subreddit
✅ Download comment images
✅ Save posts in both .json and .txt formats
✅ Translate titles and selftexts with OpenAI
✅ Save translations in both .json and .txt formats
✅ Flexible CLI options for filtering and targeting
✅ Simple setup with uv dependency management

⸻

🔧 Usage

Command-line Options

Option	Description
-h, --help	Show help message and exit
-o OUTPUT, --output OUTPUT	Output directory (default: data)
-d DEV_MODE, --dev-mode	Run in development mode (limit to 3 comments); omit for production
-r SUBREDDIT, --subreddit SUBREDDIT	Subreddit to scrape (default: PhotoshopRequest)
-f {Paid,Free,All}, --flair {Paid,Free,All}	Filter posts by flair (Paid, Free, or All); default: Paid
-t {Chinese,Spanish,French,German,Japanese,Korean,Russian}, --target-lang	Target language for translation (default: Chinese)
-c COUNT, --count COUNT	Number of posts to download (default: 5)


⸻

🚀 Getting Started

1️⃣ Prerequisites
	•	Python 3.8+
	•	uv — fast package installer (alternative to pip)

2️⃣ Installation

Clone the repo:

git clone https://github.com/your-username/rscraper.git
cd rscraper

Install dependencies:

uv pip install -r requirements.txt

3️⃣ Configure API Keys

Create a .env file in the project root:

REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key


⸻

🏃 Example Usage

Basic example:

uv run main.py -d False -r PhotoRequest -f Paid -o ./data -t Japanese -c 10

Help screen:

uv run main.py --help


⸻

📂 Output Structure

/data
    /comments
        comment_image_1.jpg
        comment_image_2.png
    post_12345.json
    post_12345.txt
    post_12345_translated.json
    post_12345_translated.txt


⸻

📝 License

This project is released under the MIT License.

⸻

🤝 Contributing

Contributions welcome! Feel free to open:
	•	Issues
	•	Pull requests
	•	Suggestions

⸻

🙏 Acknowledgements
	•	PRAW — Python Reddit API Wrapper
	•	OpenAI API
	•	uv

⸻

Happy scraping! 🚀
~ Steve Fan (sfan)

⸻

If you’d like, I can also:
✅ Auto-generate a LICENSE file
✅ Add a .gitignore
✅ Generate a requirements.txt
✅ Suggest badges (PyPI version, license, stars, etc.)

Want me to generate those too? Just say “yes”! 🚀✨