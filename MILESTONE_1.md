# Milestone 1: Reddit Scraper for r/PhotoshopRequest

## Features Implemented

### Core Functionality
- Reddit API integration using PRAW
- Environment variable configuration for API credentials
- Structured data storage with date-based organization
- Deduplication of downloaded images
- OpenAI API integration for translations

### Post Scraping
- Filtering posts by "Paid" flair
- Extraction of post metadata:
  - Post ID, title, author
  - Creation timestamp
  - Score and comment count
  - Post URL and selftext
  - Post flair
- Translation of content:
  - Title translation to Chinese
  - Selftext translation to Chinese
  - Preservation of URLs and technical terms in translations

### PSR-Bot Integration
- Detection and parsing of PSR-Bot comments
- Extraction of important details:
  - Request Type
  - Status
  - Deadline
  - Completion Deadline
- Prioritization of stickied PSR-Bot comments

### Image Handling
- Support for multiple image types:
  - Direct image URLs
  - Reddit gallery images
  - Preview images
  - Markdown image links
- Image deduplication using filename tracking
- Proper file extension detection
- Rate limiting (1-second delay between downloads)

### Comment Image Processing
- Dedicated comments subfolder for each post
- Extraction of images from comments
- Author-based image naming convention
- Sequential numbering for multiple images from same author
- Support for both markdown and direct image links in comments
- Development mode with comment limit (3 comments) for testing

## Directory Structure
```
data/
  YYYY-MM-DD/
    post_id/
      post_data.json
      post_image_01.jpg
      post_image_02.jpg
      comments/
        username1_image_01.jpg
        username1_image_02.jpg
        username2_image_01.jpg
        ...
```

## Data Structure
The `post_data.json` file now includes:
```json
{
  "id": "post_id",
  "title": "Original title",
  "title_zh": "Translated title in Chinese",
  "author": "username",
  "created_utc": "ISO timestamp",
  "score": 123,
  "url": "post_url",
  "selftext": "Original post text",
  "selftext_zh": "Translated post text in Chinese",
  "num_comments": 10,
  "flair": "Paid",
  "image_urls": ["url1", "url2"],
  "psr_bot_details": {
    "request_type": "type",
    "status": "status",
    "deadline": "deadline",
    "completion_deadline": "completion_deadline"
  }
}
```

## Next Steps
- Consider adding error recovery mechanisms
- Implement logging system for better debugging
- Add support for more image hosting platforms
- Consider adding a database for better data management
- Add support for batch processing of multiple subreddits
- Add support for translating comments
- Implement caching for translations to reduce API calls
- Add support for more target languages 