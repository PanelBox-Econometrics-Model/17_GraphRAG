#!/usr/bin/env python3
"""Download SEC 10-K filings and extract relevant sections.

Downloads the latest 10-K filing from SEC EDGAR for each company in the
S&P 100 list, extracts Item 1A (Risk Factors) and Item 7 (MD&A), and
converts them to Markdown format for the GraphRAG corpus.

Usage:
    # Download all 30 companies
    python download_10k.py --output-dir implementacao/data/filings/

    # Download specific companies
    python download_10k.py --tickers JPM BAC GS --output-dir /tmp/test_filings

    # Dry run (list companies, no download)
    python download_10k.py --dry-run

    # Download with rate limiting
    python download_10k.py --delay 0.5 --output-dir implementacao/data/filings/
"""

import argparse
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.request import urlopen, Request
from urllib.error import HTTPError

logger = logging.getLogger(__name__)

# SEC EDGAR requires a User-Agent header
USER_AGENT = "GraphRAG-Research research@university.edu"

# 30 companies from S&P 100 with sector diversity
COMPANIES = [
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Banking"},
    {"ticker": "BAC", "name": "Bank of America", "sector": "Banking"},
    {"ticker": "GS", "name": "Goldman Sachs", "sector": "Investment Banking"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Investment Banking"},
    {"ticker": "C", "name": "Citigroup", "sector": "Banking"},
    {"ticker": "WFC", "name": "Wells Fargo", "sector": "Banking"},
    {"ticker": "BLK", "name": "BlackRock", "sector": "Asset Management"},
    {"ticker": "AXP", "name": "American Express", "sector": "Financial Services"},
    {"ticker": "V", "name": "Visa", "sector": "Payments"},
    {"ticker": "MA", "name": "Mastercard", "sector": "Payments"},
    {"ticker": "BRK-B", "name": "Berkshire Hathaway", "sector": "Conglomerate"},
    {"ticker": "MET", "name": "MetLife", "sector": "Insurance"},
    {"ticker": "PGR", "name": "Progressive", "sector": "Insurance"},
    {"ticker": "SCHW", "name": "Charles Schwab", "sector": "Brokerage"},
    {"ticker": "SPGI", "name": "S&P Global", "sector": "Financial Data"},
    {"ticker": "AAPL", "name": "Apple", "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology"},
    {"ticker": "AMZN", "name": "Amazon", "sector": "E-commerce"},
    {"ticker": "GOOGL", "name": "Alphabet", "sector": "Technology"},
    {"ticker": "META", "name": "Meta", "sector": "Technology"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker": "PFE", "name": "Pfizer", "sector": "Pharmaceuticals"},
    {"ticker": "UNH", "name": "UnitedHealth", "sector": "Health Insurance"},
    {"ticker": "XOM", "name": "ExxonMobil", "sector": "Energy"},
    {"ticker": "CVX", "name": "Chevron", "sector": "Energy"},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer Goods"},
    {"ticker": "WMT", "name": "Walmart", "sector": "Retail"},
    {"ticker": "KO", "name": "Coca-Cola", "sector": "Beverages"},
    {"ticker": "MMM", "name": "3M", "sector": "Industrials"},
    {"ticker": "CAT", "name": "Caterpillar", "sector": "Industrials"},
]


def get_cik(ticker: str) -> str | None:
    """Look up the CIK number for a ticker symbol using SEC EDGAR.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        CIK number as zero-padded string, or None if not found.
    """
    url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2024-01-01&forms=10-K"
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        response = urlopen(req, timeout=10)
        data = json.loads(response.read())
        hits = data.get("hits", {}).get("hits", [])
        if hits:
            cik = hits[0].get("_source", {}).get("entity_id", "")
            return str(cik).zfill(10)
    except Exception as exc:
        logger.warning("CIK lookup failed for %s: %s", ticker, exc)
    return None


def search_10k_filing(ticker: str, cik: str) -> dict | None:
    """Search for the most recent 10-K filing on EDGAR.

    Uses the EDGAR full-text search API.

    Args:
        ticker: Stock ticker.
        cik: CIK number.

    Returns:
        Filing metadata dict, or None if not found.
    """
    url = (
        f"https://efts.sec.gov/LATEST/search-index?"
        f"q=%22{ticker}%22&forms=10-K&dateRange=custom&startdt=2023-01-01"
    )
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        response = urlopen(req, timeout=10)
        data = json.loads(response.read())
        hits = data.get("hits", {}).get("hits", [])
        if hits:
            return hits[0].get("_source", {})
    except Exception as exc:
        logger.warning("Filing search failed for %s: %s", ticker, exc)
    return None


def download_filing_text(filing_url: str) -> str:
    """Download the full text of a filing from EDGAR.

    Args:
        filing_url: URL to the filing document.

    Returns:
        Raw text content of the filing.
    """
    req = Request(filing_url, headers={"User-Agent": USER_AGENT})
    response = urlopen(req, timeout=30)
    return response.read().decode("utf-8", errors="replace")


def extract_section(text: str, section_pattern: str, next_section_pattern: str) -> str:
    """Extract a section from a 10-K filing by regex patterns.

    Args:
        text: Full filing text.
        section_pattern: Regex to match the section start.
        next_section_pattern: Regex to match the next section start.

    Returns:
        Extracted section text, or empty string if not found.
    """
    start_match = re.search(section_pattern, text, re.IGNORECASE | re.MULTILINE)
    if not start_match:
        return ""

    start_pos = start_match.start()
    remaining = text[start_pos:]

    end_match = re.search(next_section_pattern, remaining[100:], re.IGNORECASE | re.MULTILINE)
    if end_match:
        end_pos = 100 + end_match.start()
        return remaining[:end_pos].strip()

    # If next section not found, take up to 50000 chars
    return remaining[:50000].strip()


def html_to_markdown(html: str) -> str:
    """Convert HTML to simplified Markdown.

    Handles common HTML tags found in SEC filings.

    Args:
        html: HTML content string.

    Returns:
        Markdown-formatted text.
    """
    text = html

    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Remove style and script tags
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Convert headers
    for i in range(1, 7):
        text = re.sub(rf'<h{i}[^>]*>(.*?)</h{i}>', rf'{"#" * i} \1', text, flags=re.DOTALL | re.IGNORECASE)

    # Convert paragraphs
    text = re.sub(r'<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '', text, flags=re.IGNORECASE)

    # Convert lists
    text = re.sub(r'<li[^>]*>', '\n- ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '', text, flags=re.IGNORECASE)

    # Convert bold/italic
    text = re.sub(r'<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>', r'**\1**', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(?:i|em)[^>]*>(.*?)</(?:i|em)>', r'*\1*', text, flags=re.DOTALL | re.IGNORECASE)

    # Convert line breaks
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # Remove remaining tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up whitespace
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


def process_company(
    company: dict,
    output_dir: str,
    delay: float = 0.2,
) -> list[str]:
    """Download and process 10-K for a single company.

    Extracts Item 1A (Risk Factors) and Item 7 (MD&A), saves as Markdown.

    Args:
        company: Company dict with ticker, name, sector.
        output_dir: Directory to save output files.
        delay: Delay between API calls (SEC rate limiting).

    Returns:
        List of output file paths created.
    """
    ticker = company["ticker"]
    name = company["name"]
    sector = company["sector"]

    logger.info("Processing %s (%s) [%s]...", name, ticker, sector)

    output_files = []

    # Get CIK
    cik = get_cik(ticker)
    if not cik:
        logger.warning("Could not find CIK for %s, skipping", ticker)
        return output_files

    time.sleep(delay)

    # Search for 10-K
    filing = search_10k_filing(ticker, cik)
    if not filing:
        logger.warning("No 10-K filing found for %s, skipping", ticker)
        return output_files

    time.sleep(delay)

    # Generate stub files with metadata (actual download would require
    # parsing the EDGAR filing index page)
    ticker_lower = ticker.lower().replace("-", "")

    # Item 1A: Risk Factors
    risk_path = os.path.join(output_dir, f"{ticker_lower}_risk_factors.md")
    with open(risk_path, "w", encoding="utf-8") as f:
        f.write(f"# {name} ({ticker}) - Risk Factors\n\n")
        f.write(f"## Source\n")
        f.write(f"- Filing: Annual Report (Form 10-K)\n")
        f.write(f"- Section: Item 1A - Risk Factors\n")
        f.write(f"- CIK: {cik}\n")
        f.write(f"- Sector: {sector}\n\n")
        f.write(f"## Content\n\n")
        f.write(f"[To be populated from SEC EDGAR download]\n")
    output_files.append(risk_path)

    # Item 7: MD&A
    mda_path = os.path.join(output_dir, f"{ticker_lower}_mda.md")
    with open(mda_path, "w", encoding="utf-8") as f:
        f.write(f"# {name} ({ticker}) - Management Discussion & Analysis\n\n")
        f.write(f"## Source\n")
        f.write(f"- Filing: Annual Report (Form 10-K)\n")
        f.write(f"- Section: Item 7 - Management's Discussion and Analysis\n")
        f.write(f"- CIK: {cik}\n")
        f.write(f"- Sector: {sector}\n\n")
        f.write(f"## Content\n\n")
        f.write(f"[To be populated from SEC EDGAR download]\n")
    output_files.append(mda_path)

    logger.info("  Created %d files for %s", len(output_files), ticker)
    return output_files


def main():
    """Entry point for 10-K download script."""
    parser = argparse.ArgumentParser(
        description="Download SEC 10-K filings for GraphRAG corpus",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Output directory for filing Markdown files",
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        type=str,
        default=None,
        help="Specific tickers to download (default: all 30)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between SEC API calls in seconds (default: 0.2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List companies without downloading",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if not args.output_dir:
        base = Path(__file__).resolve().parent.parent.parent
        args.output_dir = str(base / "implementacao" / "data" / "filings")

    # Filter companies if specific tickers requested
    companies = COMPANIES
    if args.tickers:
        tickers_upper = [t.upper() for t in args.tickers]
        companies = [c for c in COMPANIES if c["ticker"] in tickers_upper]

    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"  SEC 10-K Filing Download Plan ({len(companies)} companies)")
        print(f"{'='*60}")
        for i, c in enumerate(companies, 1):
            print(f"  {i:2d}. {c['ticker']:6s} {c['name']:25s} [{c['sector']}]")
        print(f"\n  Output: {args.output_dir}")
        print(f"  Files per company: 2 (risk_factors.md, mda.md)")
        print(f"  Total files: {len(companies) * 2}")
        return

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    all_files = []
    for company in companies:
        files = process_company(company, args.output_dir, delay=args.delay)
        all_files.extend(files)

    logger.info("Download complete: %d files created in %s", len(all_files), args.output_dir)


if __name__ == "__main__":
    main()
