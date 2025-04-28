# Crypto RSS MCP

An MCP server that aggregates real-time cryptocurrency news from multiple RSS feeds, helping AI agents make informed decisions in a fast-paced market.

![GitHub License](https://img.shields.io/github/license/kukapay/crypto-trending-mcp)
![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)


## Features

- **Feed Retrieval**: Fetches latest entries from specified RSS feeds, formatting them as Markdown with plain-text summaries.
- **Keyword Filtering**: Filters feeds by keyword in descriptions or categories.
- **OPML Support**: Import feed list from a local OPML file provided by [Chainfeeds](https://raw.githubusercontent.com/chainfeeds/RSSAggregatorforWeb3/main/RAW.opml).
- **LLM Integration**: Includes a prompt for analyzing feed content to summarize key points and identify cryptocurrency market trends.

## Prerequisites

- **Python**: Version 3.10.
- **uv**: Package and dependency manager for Python projects.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kukapay/crypto-rss-mcp.git
   cd crypto-rss-mcp
   ```

2. **Install Dependencies**:
   Add the required dependencies using `uv`:
   ```bash
   uv sync
   ```

## Usage

### Running the Server

Start the FastMCP server in development mode:
```bash
uv run mcp dev cli.py
```

### Installing to Claude Desktop

Install the server as a Claude Desktop application:
```bash
uv run mcp install cli.py --name "Crypto RSS Reader"
```

Configuration file as a reference:

```json
{
   "mcpServers": {
       "Crypto RSS Reader": {
           "command": "uv",
           "args": [ "--directory", "/path/to/crypto-rss-mcp", "run", "crypto-rss-mcp" ] 
       }
   }
}
```

### Available Tools

#### `get_crypto_rss_list`

Lists available RSS feeds from an OPML file, optionally filtered by keyword.

**Parameters**:
- `keyword` (str, optional): Filter feeds where the keyword appears in the description or category (case-insensitive).
- `opml_file` (str, optional): Path to a local OPML file (defaults to `"RAW.opml"`).

**Example**:
> List available cryptocurrency RSS feeds

**Output**:
```
Available Cryptocurrency RSS Feeds:

Category: 05. Research/VC
URL: https://b10c.me/feed.xml
Description: 0xB10C's Blog: German Bitcoin freelance developer on 0xB10C's Blog

Category: 03. Media
URL: https://bitcoinmagazine.com/feed
Description: Bitcoin Magazine
...
```

#### `get_rss_feed`

Fetches and formats the latest 10 entries from a specified RSS feed as Markdown.

**Parameters**:
- `feed_url` (str): The URL of the RSS feed to fetch.

**Example**:
>  Read this RSS feed: https://blog.0xproject.com/feed

**Output**:
```
# Feed: 0x Blog - Medium

## Entry 1
- **Title**: Introducing 0x Protocol v4
- **Link**: [https://blog.0xproject.com/...](https://blog.0xproject.com/...)
- **Published**: Mon, 28 Apr 2025 10:00:00 GMT
- **Summary**: The 0x Protocol v4 brings improved efficiency...

  ### Why This Matters
  This update enhances...
...
```

### Available Prompts

#### `analyze_rss_feed`

Creates a prompt for analyzing RSS feed content, summarizing key points and identifying cryptocurrency market trends.

**Parameters**:
- `url` (str): The RSS feed URL to analyze.

**Example**:
> Analyze the content of this RSS feed https://blog.0xproject.com/feed, summarize the key points, and identify any trends in the cryptocurrency market."

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
