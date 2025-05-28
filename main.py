import os
import praw
from dotenv import load_dotenv
import json
from datetime import datetime
import pathlib
import requests
from urllib.parse import urlparse, unquote
import mimetypes
import time
import re
import hashlib
from io import BytesIO
import openai
import argparse

"""
Reddit Scraper for r/PhotoshopRequest

This script scrapes posts from r/PhotoshopRequest subreddit, focusing on paid requests.
It downloads post images, comment images, and translates post content to Chinese.

Features:
- Scrapes posts with "Paid" flair
- Downloads post images and comment images
- Extracts PSR-Bot details (request type, status, deadlines)
- Translates post title and content to Chinese
- Organizes data in date-based directory structure
- Supports development mode for testing

Requirements:
- Python 3.7+
- Required packages: praw, python-dotenv, requests, openai
- Reddit API credentials (client_id, client_secret, user_agent)
- OpenAI API key

Environment Variables (.env file):
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key

Usage:
    python main.py [--output OUTPUT_DIR] [--dev-mode]

Arguments:
    --output, -o    Output directory path (default: data/)
    --dev-mode, -d  Run in development mode (limit to 3 comments)

Output Structure:
    output_dir/
        YYYY-MM-DD/
            post_id/
                post_data.json
                post_image_01.jpg
                comments/
                    username1_image_01.jpg
                    ...

Author: Steve Fan
Date: 2025-05-27
Version: 1.0
"""

# Load environment variables
load_dotenv()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Reddit Scraper for r/PhotoshopRequest')
    parser.add_argument(
        '--output', 
        '-o',
        type=str,
        default='data',
        help='Output directory path (default: data)'
    )
    parser.add_argument(
        '--dev-mode',
        '-d',
        type=bool,
        default=True,
        help='Run in development mode (limit to 3 comments)'
    )
    return parser.parse_args()

def setup_reddit_client():
    """Initialize and return a Reddit client instance."""
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'MyRedditScraper v1.0')
    )

def setup_openai_client():
    """Initialize and return an OpenAI client instance."""
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    return client

def is_image_url(url):
    """Check if the URL points to an image."""
    if not url:
        return False
    
    # Common image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    
    # Check if it's a Reddit image URL
    if parsed_url.netloc in ['i.redd.it', 'preview.redd.it']:
        return True
    
    # Check file extension
    if any(path.endswith(ext) for ext in image_extensions):
        return True
    
    # Check content type if it's a direct URL
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('content-type', '').lower()
        return content_type.startswith('image/')
    except:
        return False

def get_image_hash(image_data):
    """Calculate SHA-256 hash of image data."""
    return hashlib.sha256(image_data).hexdigest()

def get_filename_from_url(url):
    """Extract filename from URL."""
    parsed_url = urlparse(url)
    path = parsed_url.path
    # URL decode the path
    decoded_path = unquote(path)
    # Get the filename
    filename = os.path.basename(decoded_path)
    # Remove any query parameters
    filename = filename.split('?')[0]
    return filename

def download_image(url, save_path, post_id, image_index, existing_filenames=None):
    """Download an image from URL and save it to the specified path with a unique name."""
    try:
        # Check if we've already downloaded this filename
        filename = get_filename_from_url(url)
        if existing_filenames is not None and filename in existing_filenames:
            print(f"Skipping duplicate filename: {filename}")
            return None, existing_filenames

        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get the content type and determine file extension
        content_type = response.headers.get('content-type', '')
        ext = mimetypes.guess_extension(content_type) or '.jpg'
        
        # Read image data
        image_data = response.content
        
        # Create a unique filename using post ID and image index
        filename = f"{post_id}_image_{image_index:02d}{ext}"
        file_path = os.path.join(save_path, filename)
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Update existing filenames if provided
        if existing_filenames is not None:
            existing_filenames.add(get_filename_from_url(url))
        
        return file_path, existing_filenames
    except Exception as e:
        print(f"Error downloading image from {url}: {str(e)}")
        return None, existing_filenames

def parse_psr_bot_details(comment_body):
    """Parse PSR-Bot MOD comment details."""
    details = {
        'request_type': None,
        'status': None,
        'deadline': None,
        'completion_deadline': None
    }
    
    # Parse request type
    request_type_match = re.search(r'Request Type:\s*(\w+)', comment_body, re.IGNORECASE)
    if request_type_match:
        details['request_type'] = request_type_match.group(1).strip()
    
    # Parse status
    status_match = re.search(r'Status:\s*(\w+)', comment_body, re.IGNORECASE)
    if status_match:
        details['status'] = status_match.group(1).strip()
    
    # Parse deadline
    deadline_match = re.search(r'Deadline:\s*([^\n]+)', comment_body, re.IGNORECASE)
    if deadline_match:
        details['deadline'] = deadline_match.group(1).strip()
    
    # Parse completion deadline
    completion_deadline_match = re.search(r'Completion Deadline:\s*([^\n]+)', comment_body, re.IGNORECASE)
    if completion_deadline_match:
        details['completion_deadline'] = completion_deadline_match.group(1).strip()
    
    return details

def get_post_images(post):
    """Get all image URLs from a post."""
    image_urls = []
    
    # Check post URL
    if is_image_url(post.url):
        image_urls.append(post.url)
    
    # Check if post has a gallery
    if hasattr(post, 'gallery_data'):
        for item in post.gallery_data['items']:
            media_id = item['media_id']
            if media_id in post.media_metadata:
                image_url = post.media_metadata[media_id]['s']['u']
                image_urls.append(image_url)
    
    # Check if post has a preview
    if hasattr(post, 'preview') and 'images' in post.preview:
        for image in post.preview['images']:
            if 'source' in image and 'url' in image['source']:
                image_url = image['source']['url']
                # Convert preview URLs to direct image URLs
                image_url = image_url.replace('&amp;', '&')
                image_urls.append(image_url)
    
    # Check selftext for markdown image links
    if post.selftext:
        # Look for markdown image links
        image_links = re.findall(r'!\[.*?\]\((.*?)\)', post.selftext)
        image_urls.extend(image_links)
        
        # Look for direct URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, post.selftext)
        for url in urls:
            if is_image_url(url):
                image_urls.append(url)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(image_urls))

def translate_text(text):
    """Translate text to Chinese using OpenAI API."""
    if not text:
        print("No text provided for translation")
        return None
    
    try:
        print(f"Attempting to translate text: {text[:100]}...")  # Print first 100 chars for debugging
        
        client = setup_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following text to Chinese. Keep any URLs, usernames, and technical terms unchanged."},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        translation = response.choices[0].message.content.strip()
        print(f"Translation successful: {translation[:100]}...")  # Print first 100 chars of translation
        return translation
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        print(f"Error type: {type(e)}")
        return None

def get_post_details(post):
    """Get detailed information about a post including PSR-Bot details and translations."""
    # Get PSR-Bot comment
    post.comments.replace_more(limit=0)
    psr_bot_comment = None
    
    # First try to find stickied comment
    for comment in post.comments:
        if comment.stickied and comment.author and comment.author.name == 'psr-bot':
            psr_bot_comment = comment
            break
    
    # If no stickied comment found, look for any PSR-Bot comment
    if not psr_bot_comment:
        for comment in post.comments:
            if comment.author and comment.author.name == 'psr-bot':
                psr_bot_comment = comment
                break
    
    # Parse PSR-Bot details
    psr_bot_details = None
    if psr_bot_comment:
        psr_bot_details = parse_psr_bot_details(psr_bot_comment.body)
        print(f"Found PSR-Bot comment for post {post.id}")
        if psr_bot_details['completion_deadline']:
            print(f"Completion Deadline: {psr_bot_details['completion_deadline']}")
    else:
        print(f"No PSR-Bot comment found for post {post.id}")
    
    # Get all image URLs
    image_urls = get_post_images(post)
    
    # Translate title and selftext
    print(f"\nTranslating content for post {post.id}")
    print("Original title:", post.title)
    translated_title = translate_text(post.title)
    print("Translated title:", translated_title)
    
    print("\nOriginal selftext:", post.selftext[:100] + "..." if post.selftext else "No selftext")
    translated_selftext = translate_text(post.selftext)
    print("Translated selftext:", translated_selftext[:100] + "..." if translated_selftext else "No translation")
    
    return {
        'id': post.id,
        'title': post.title,
        'title_zh': translated_title,
        'author': str(post.author),
        'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
        'score': post.score,
        'url': post.url,
        'selftext': post.selftext,
        'selftext_zh': translated_selftext,
        'num_comments': post.num_comments,
        'flair': post.link_flair_text,
        'image_urls': image_urls,
        'psr_bot_details': psr_bot_details
    }

def scrape_subreddit(subreddit_name='PhotoshopRequest', limit=5):
    """Scrape posts from the specified subreddit."""
    reddit = setup_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    
    posts = []
    # Use search with flair filter to get only Paid posts
    for post in subreddit.search('flair:"Paid"', limit=limit, sort='new'):
        post_details = get_post_details(post)
        posts.append(post_details)
    
    return posts

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist."""
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

def get_comment_images(comment):
    """Get all image URLs from a comment."""
    image_urls = []
    
    # Check comment body for markdown image links
    if comment.body:
        # Look for markdown image links
        image_links = re.findall(r'!\[.*?\]\((.*?)\)', comment.body)
        image_urls.extend(image_links)
        
        # Look for direct URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, comment.body)
        for url in urls:
            if is_image_url(url):
                image_urls.append(url)
    
    return list(dict.fromkeys(image_urls))

def download_comment_image(url, save_path, author_name, image_index):
    """Download an image from a comment and save it with author's username."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get the content type and determine file extension
        content_type = response.headers.get('content-type', '')
        ext = mimetypes.guess_extension(content_type) or '.jpg'
        
        # Create filename using author name and sequence number
        filename = f"{author_name}_image_{image_index:02d}{ext}"
        file_path = os.path.join(save_path, filename)
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return file_path
    except Exception as e:
        print(f"Error downloading comment image from {url}: {str(e)}")
        return None

def format_post_as_text(post_data):
    """Format post data as a readable text file."""
    text = []
    text.append(f"ID: {post_data['id']}")
    text.append(f"Author: {post_data['author']}")
    text.append(f"Title: {post_data['title']}")
    text.append(f"Title (Chinese): {post_data['title_zh']}")
    text.append(f"Created UTC: {post_data['created_utc']}")
    text.append(f"Number of Comments: {post_data['num_comments']}")
    text.append("\nOriginal Text:")
    text.append(post_data['selftext'] if post_data['selftext'] else "No text content")
    text.append("\nTranslated Text:")
    text.append(post_data['selftext_zh'] if post_data['selftext_zh'] else "No translation available")
    
    if post_data['psr_bot_details']:
        text.append("\nPSR-Bot Details:")
        for key, value in post_data['psr_bot_details'].items():
            if value:  # Only include non-None values
                text.append(f"{key.replace('_', ' ').title()}: {value}")
    
    return "\n".join(text)

def save_post_data(post_data, post_dir, dev_mode=False):
    """Save post data and download associated images."""
    # Save post data as JSON
    post_file = os.path.join(post_dir, 'post_data.json')
    with open(post_file, 'w', encoding='utf-8') as f:
        json.dump(post_data, f, indent=4, ensure_ascii=False)
    
    # Save post data as TXT
    post_txt_file = os.path.join(post_dir, 'post_data.txt')
    with open(post_txt_file, 'w', encoding='utf-8') as f:
        f.write(format_post_as_text(post_data))
    
    # Set to store image filenames for this post
    existing_filenames = set()
    
    # Download all post images
    image_index = 1
    for image_url in post_data['image_urls']:
        if image_url:
            print(f"Processing post image {image_index} from {image_url}")
            file_path, existing_filenames = download_image(image_url, post_dir, post_data['id'], image_index, existing_filenames)
            if file_path:  # Only increment index if image was saved
                image_index += 1
            time.sleep(1)  # Be nice to the server
    
    # Create comments directory
    comments_dir = os.path.join(post_dir, 'comments')
    ensure_directory_exists(comments_dir)
    
    # Get the post object to access comments
    reddit = setup_reddit_client()
    post = reddit.submission(id=post_data['id'])
    post.comments.replace_more(limit=0)  # Load all comments
    
    # Process each comment
    comment_count = 0
    for comment in post.comments.list():
        if comment.author:  # Skip deleted/removed comments
            author_name = str(comment.author)
            comment_images = get_comment_images(comment)
            
            if comment_images:
                print(f"Found {len(comment_images)} images in comment by {author_name}")
                # Download each image from the comment
                for idx, image_url in enumerate(comment_images, 1):
                    print(f"Processing comment image {idx} from {author_name}")
                    file_path = download_comment_image(image_url, comments_dir, author_name, idx)
                    if file_path:
                        print(f"Saved comment image to {file_path}")
                    time.sleep(1)  # Be nice to the server
                
                comment_count += 1
                if dev_mode and comment_count >= 3:
                    print("Development mode: Reached maximum comment limit (3)")
                    break

def save_posts(posts, output_dir, dev_mode=False):
    """Save all posts in the structured folder hierarchy."""
    saved_posts = []
    for post in posts:
        # Check PSR-Bot status
        if post['psr_bot_details'] and post['psr_bot_details'].get('status') == 'Solved':
            print(f"Skipping post {post['id']} - PSR-Bot status is 'Solved'")
            continue
            
        # Create base data directory
        ensure_directory_exists(output_dir)
        
        # Get post date and create date directory
        post_date = datetime.fromisoformat(post['created_utc']).strftime('%Y-%m-%d')
        date_dir = os.path.join(output_dir, post_date)
        ensure_directory_exists(date_dir)
        
        # Create post directory
        post_dir = os.path.join(date_dir, post['id'])
        ensure_directory_exists(post_dir)
        
        # Save post data and download images
        save_post_data(post, post_dir, dev_mode)
        saved_posts.append(post_dir)
    
    return saved_posts

def main():
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Initialize OpenAI client
        openai_client = setup_openai_client()
        if not openai_client:
            print("Failed to initialize OpenAI client. Please check your API key.")
            return
            
        print("OpenAI client initialized successfully")
        print(f"Output directory: {args.output}")
        print(f"Development mode: {'Enabled' if args.dev_mode else 'Disabled'}")
        
        # Scrape the subreddit
        posts = scrape_subreddit()
        
        if not posts:
            print("No posts found")
            return
        
        # Save the posts in structured folders
        saved_dirs = save_posts(posts, args.output, args.dev_mode)
        print(f"Successfully scraped {len(posts)} posts")
        print("Posts saved in the following directories:")
        for directory in saved_dirs:
            print(f"- {directory}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
