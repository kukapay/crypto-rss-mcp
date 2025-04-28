import feedparser
import httpx
import html2text
import opml
import os
import re
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import Prompt, PromptMessage, TextContent
from typing import List

# Initialize MCP server
mcp = FastMCP("Crypto RSS Reader", dependencies=["feedparser", "httpx", "html2text", "opml"])

def load_rss_feeds_from_opml(opml_file: str) -> List[dict]:
    """Load RSS feeds from an OPML file."""
    try:
        outline = opml.parse(opml_file)
        feeds = []
        def parse_outline(items, category: str = ""):
            for item in items:
                print(item, hasattr(item, "__iter__"))
                if hasattr(item, "xmlUrl") and item.xmlUrl:
                    # Collect feed with URL, description, and optional category
                    feeds.append({
                        "url": item.xmlUrl,
                        "description": item.title or item.text or "No description available",
                        "category": category
                    })
                # Recursively process nested outlines
        def parse_outline(items, category: str = ""):
            for item in items:
                if hasattr(item, "xmlUrl") and item.xmlUrl:
                    # Collect feed with URL, description, and optional category
                    feeds.append({
                        "url": item.xmlUrl,
                        "description": item.title or item.text or "No description available",
                        "category": category
                    })
                # Recursively process nested outlines (children)
                try:
                    # Iterate over item as a container of child outlines
                    parse_outline(item, category=item.title or item.text or category)
                except TypeError:
                    # If item is not iterable, skip to next item
                    continue
                
        # Start parsing from top-level outlines
        parse_outline(outline)
        return feeds
    except FileNotFoundError:
        raise RuntimeError(f"OPML file not found: {OPML_FILE}")
    except Exception as e:
        raise RuntimeError(f"Failed to parse OPML file: {str(e)}")

async def fetch_rss_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch and parse an RSS feed from the specified URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return feedparser.parse(response.text)

# Tool: Fetch and format RSS feed content
@mcp.tool()
async def get_rss_feed(feed_url: str, ctx: Context = None) -> str:
    """
    Retrieve the content of the specified RSS feed.
    
    Parameters:
        feed_url (str): The URL of the RSS feed to fetch (e.g., 'https://cointelegraph.com/rss').
        ctx (Context, optional): MCP context for logging or progress reporting.
    
    Returns:
        str: A formatted Markdown string containing the feed title and up to 10 latest entries with titles, links, publication dates, and summaries converted from HTML to plain text.
    """
    ctx.info(f"Fetching RSS feed from {feed_url}")
    feed = await fetch_rss_feed(feed_url)
    entries = feed.entries[:10]  # Limit to the latest 10 entries
    
    # Initialize html2text converter
    h = html2text.HTML2Text()
    h.body_width = 0  # Disable line wrapping
    h.ignore_links = True  # Ignore links in summary
    h.ignore_images = True  # Ignore images in summary
    h.inline_links = False  # Ensure links are not embedded in text
    h.mark_code = False  # Disable code block markers
    h.use_automatic_links = False  # Disable automatic link references
    h.skip_internal_headers = True  # Ignores <h1>-<h6> tags
    
    result = f"# Feed: {feed.feed.title}\n\n"
    for i, entry in enumerate(entries):
        # Convert HTML summary to plain text
        summary_text = h.handle(entry.summary).strip()
        # Post-process to demote ## headers to ### in summary
        summary_text = re.sub(r'^\s*##\s+(.+)$', r'### \1', summary_text, flags=re.MULTILINE)
        result += f"## Entry {i + 1}\n"
        result += f"- **Title**: {entry.title}\n"
        result += f"- **Link**: [{entry.link}]({entry.link})\n"
        result += f"- **Published**: {entry.published}\n"
        result += f"- **Summary**: {summary_text}\n\n"
    return result

# Tool: List available RSS feeds with descriptions from OPML
@mcp.tool()
async def get_crypto_rss_list(keyword: str = None, opml_file: str = "RAW.opml") -> str:
    """
    Retrieve a list of available cryptocurrency RSS feeds from a local or remote OPML file, optionally filtered by keyword.
    
    Parameters:
        keyword (str, optional): Filter feeds where the keyword appears in the description or category (case-insensitive).
        opml_file (str, optional): Path to a local OPML file to read feeds from. If not provided, fetches from the remote OPML URL.
    
    Returns:
        str: A formatted string listing each RSS feed URL, its description, and category, parsed from the OPML file.
    """
    feeds = load_rss_feeds_from_opml(opml_file=opml_file)
    if keyword:
        keyword = keyword.lower()
        feeds = [
            feed for feed in feeds
            if keyword in feed['description'].lower() or keyword in (feed['category'] or '').lower()
        ]
    result = "Available Cryptocurrency RSS Feeds:\n\n"
    if not feeds:
        result += "No feeds found matching the keyword.\n"
    for feed in feeds:
        result += f"Category: {feed['category'] or 'Uncategorized'}\n"
        result += f"URL: {feed['url']}\n"
        result += f"Description: {feed['description']}\n\n"
    return result
    
# Prompt: Analyze RSS feed content
@mcp.prompt()
def analyze_rss_feed(url: str) -> List[PromptMessage]:
    """Create a prompt for analyzing RSS feed content."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Please analyze the latest news from this RSS feed: {url}\n"
                     f"Summarize the key points and identify any trends in the cryptocurrency market."
            )
        ),
        PromptMessage(
            role="assistant",
            content=TextContent(
                type="text",
                text="I'll fetch and analyze the latest cryptocurrency news from the provided RSS feed. "
                     "Please wait while I process the information."
            )
        )
    ]

# Main function: Run the server
def main() -> None:    
    mcp.run()
