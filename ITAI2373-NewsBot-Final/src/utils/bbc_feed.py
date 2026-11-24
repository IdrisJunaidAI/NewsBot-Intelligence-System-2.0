"""BBC News RSS adapter for a personal educational demonstration.

Uses official BBC RSS entries with attribution and direct BBC links. It never
downloads or republishes full BBC articles and does not scrape article pages.
Commercial usage requires separate publisher permission.
"""
from datetime import datetime, timezone
from threading import Lock
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FEEDS = {
    'top': 'https://feeds.bbci.co.uk/news/rss.xml',
    'technology': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
    'business': 'https://feeds.bbci.co.uk/news/business/rss.xml',
    'world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
    'science': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml'
}
_CACHE = {}
_LOCK = Lock()
TTL_SECONDS = 600

def parse_bbc_rss(raw, channel='top'):
    """Parse original feed headlines without changing titles or claiming article rights."""
    root = ET.fromstring(raw)
    output = []
    for item in root.findall('./channel/item'):
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        date = (item.findtext('pubDate') or '').strip()
        domain = urlsplit(link).hostname or ''
        if not title or not link.startswith('https://') or not (
            domain == 'bbc.co.uk' or domain.endswith('.bbc.co.uk')
            or domain == 'bbc.com' or domain.endswith('.bbc.com')
        ):
            continue
        output.append({'title': title[:220], 'url': link, 'published': date[:90],
                       'publisher': 'BBC News', 'channel': channel})
        if len(output) >= 10:
            break
    return {'source': 'BBC News official RSS', 'attribution': 'BBC News',
            'publisher_url': 'https://www.bbc.com/news',
            'feed_url': FEEDS[channel],
            'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'mode': 'external RSS headlines, not the historical BBC model training corpus',
            'articles': output,
            'disclaimer': 'Educational personal RSS display. Headlines link to the original BBC News pages.'}

def get_bbc_headlines(channel='top'):
    if channel not in FEEDS:
        raise ValueError('Unrecognized feed')
    with _LOCK:
        record = _CACHE.get(channel)
        if record and time.monotonic() - record[0] < TTL_SECONDS:
            return record[1]
    req = Request(FEEDS[channel], headers={
        'User-Agent': 'NewsBot2-Educational-Individual-RSSReader/1.0',
        'Accept': 'application/rss+xml,application/xml,text/xml'})
    with urlopen(req, timeout=6) as response:
        body = response.read(350_000)
    payload = parse_bbc_rss(body,channel)
    if not payload['articles']:
        raise RuntimeError('No valid BBC headlines returned')
    with _LOCK:
        _CACHE[channel] = (time.monotonic(), payload)
    return payload
