import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import os

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag.get('href')
        full_url = urljoin(url, href)
        # Remove fragment identifier
        full_url, _ = urldefrag(full_url)
        if is_valid_url(full_url):
            links.append(full_url)
    return links

def get_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def crawl(base_url, visited=None):
    if visited is None:
        visited = set()

    # Remove fragment identifier from base_url
    base_url, _ = urldefrag(base_url)

    if base_url in visited:
        return

    visited.add(base_url)
    print(f"Crawling: {base_url}")

    try:
        content = get_content(base_url)
        # Create a directory for the first-level path
        first_level_path = urlparse(base_url).netloc
        # Get the path segments
        path_segments = urlparse(base_url).path.strip('/').split('/')

        # Create a unique directory for each path segment
        for i in range(len(path_segments) + 1):
            full_path = os.path.join(first_level_path, *path_segments[:i])
            if not os.path.exists(full_path):
                os.makedirs(full_path)

            # Create an output file for the current URL
            output_file = os.path.join(full_path, f"{urlparse(base_url).path.replace('/', '_') or 'index'}.txt")

            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\nURL: {base_url}\n")
                f.write(content)

        links = get_all_links(base_url)
        for link in links:
            if link.startswith(base_url):
                crawl(link, visited)
    except Exception as e:
        print(f"Error crawling {base_url}: {e}")

if __name__ == "__main__":
    base_url = input("Enter the base URL to crawl: ")

    crawl(base_url)
    print("Crawling complete.")
