import feedparser
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

CUTOFF = datetime.now(timezone.utc) - timedelta(hours=24)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

SOURCES = {
    'iran_us': {
        'label': 'Iran-krigen · Amerikansk perspektiv',
        'url': 'https://news.google.com/rss/search?q=Iran+war+attack&hl=en-US&gl=US&ceid=US:en',
        'type': 'rss',
    },
    'iran_ir': {
        'label': 'Iran-krigen · Iransk perspektiv',
        'url': 'https://en.mehrnews.com/rss',
        'type': 'rss',
        'keyword': 'iran',
    },
    'iran_dropsite': {
        'label': 'Iran-krigen · Drop Site News',
        'url': 'https://www.dropsitenews.com/',
        'type': 'scrape',
        'keyword': 'iran',
    },
    'eu_economy': {
        'label': 'Europæisk økonomi',
        'url': 'https://news.google.com/rss/search?q=european+economy&hl=en-US&gl=US&ceid=US:en',
        'type': 'rss',
    },
    'dk_economy': {
        'label': 'Dansk økonomi',
        'url': 'https://www.dr.dk/nyheder/service/feeds/penge',
        'type': 'rss',
    },
    'stocks': {
        'label': 'Globalt aktiemarked',
        'url': 'https://news.google.com/rss/search?q=stock+market+today&hl=en-US&gl=US&ceid=US:en',
        'type': 'rss',
    },
}


def clean_html(text):
    if not text:
        return ''
    return BeautifulSoup(text, 'html.parser').get_text(' ', strip=True)


def parse_date(entry):
    for field in ('published_parsed', 'updated_parsed'):
        val = getattr(entry, field, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def scrape_article_body(url, max_chars=1800):
    """Scrape fuld artikeltekst fra URL. Springer Google News-links over."""
    if not url or 'news.google.com' in url:
        return ''
    try:
        r = requests.get(url, timeout=12, headers=HEADERS, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Fjern støj
        for tag in soup(['script', 'style', 'nav', 'header', 'footer',
                         'aside', 'figure', 'figcaption', 'iframe', 'form']):
            tag.decompose()

        # Find artikelkerne
        body = (
            soup.find('article') or
            soup.find('main') or
            soup.find(class_=re.compile(r'article[-_]?(body|content|text)', re.I)) or
            soup.find(id=re.compile(r'article[-_]?(body|content|text)', re.I)) or
            soup.body
        )

        paragraphs = body.find_all('p') if body else soup.find_all('p')

        lines = []
        total = 0
        for p in paragraphs:
            text = p.get_text(' ', strip=True)
            if len(text) < 40:
                continue
            lines.append(text)
            total += len(text)
            if total >= max_chars:
                break

        return '\n\n'.join(lines)
    except Exception:
        return ''


def fetch_rss(url, keyword=None):
    feed = feedparser.parse(url)
    best = None
    for entry in feed.entries:
        title = clean_html(entry.get('title', ''))
        summary = clean_html(entry.get('summary', '') or entry.get('description', ''))
        if keyword and keyword.lower() not in (title + ' ' + summary).lower():
            continue
        pub = parse_date(entry)
        article = {
            'title': title,
            'summary': summary[:500],
            'link': entry.get('link', ''),
            'published': pub.isoformat(),
            'source': feed.feed.get('title', url),
            'recent': pub >= CUTOFF,
        }
        if pub >= CUTOFF:
            return article
        if best is None:
            best = article
    return best


def scrape_dropsite(keyword='iran'):
    try:
        r = requests.get('https://www.dropsitenews.com/', timeout=12, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            if len(title) < 20 or keyword.lower() not in title.lower():
                continue
            href = a['href']
            if not href.startswith('http'):
                href = 'https://www.dropsitenews.com' + href
            summary = ''
            parent = a.find_parent(['article', 'div', 'li', 'section'])
            if parent:
                p = parent.find('p')
                if p:
                    summary = p.get_text(strip=True)[:500]
            return {
                'title': title,
                'summary': summary,
                'link': href,
                'published': datetime.now(timezone.utc).isoformat(),
                'source': 'Drop Site News',
                'recent': True,
            }
    except Exception as e:
        return {
            'title': 'Kunne ikke hente fra Drop Site News',
            'summary': str(e),
            'link': 'https://www.dropsitenews.com',
            'source': 'Drop Site News',
            'recent': False,
        }
    return None


def fetch_all():
    results = {}
    for key, cfg in SOURCES.items():
        print(f"  Henter {key}...")
        try:
            if cfg['type'] == 'scrape':
                art = scrape_dropsite(cfg.get('keyword', ''))
            else:
                art = fetch_rss(cfg['url'], cfg.get('keyword'))

            if art:
                art['label'] = cfg['label']
                # Scrape fuld artikeltekst
                body = scrape_article_body(art.get('link', ''))
                art['body'] = body if body else art.get('summary', '')
                results[key] = art
            else:
                results[key] = {
                    'title': 'Ingen artikel fundet',
                    'summary': 'Ingen artikler fra denne kilde i dag.',
                    'body': '',
                    'link': '',
                    'label': cfg['label'],
                    'recent': False,
                }
        except Exception as e:
            results[key] = {
                'title': 'Fejl ved hentning',
                'summary': str(e),
                'body': '',
                'link': '',
                'label': cfg['label'],
                'recent': False,
            }
        time.sleep(0.5)

    out = TMP_DIR / 'articles.json'
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"OK: {len(results)} artikler gemt til {out}")
    return results


if __name__ == '__main__':
    fetch_all()
