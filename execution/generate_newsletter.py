import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"

STYLES = {
    'iran_us':       ('#FFB3BA', '#9b2335', '#ffe4e8'),
    'iran_ir':       ('#FFFACD', '#8B7500', '#fffff0'),
    'iran_dropsite': ('#B5EAD7', '#1a6644', '#e0f7ef'),
    'eu_economy':    ('#BAE1FF', '#1a4d7c', '#e6f4ff'),
    'dk_economy':    ('#E2BAFF', '#5a2d82', '#f3e8ff'),
    'stocks':        ('#D3D3D3', '#3a3a3a', '#f0f0f0'),
}

MONTHS_DA = {
    'January': 'januar', 'February': 'februar', 'March': 'marts',
    'April': 'april', 'May': 'maj', 'June': 'juni', 'July': 'juli',
    'August': 'august', 'September': 'september', 'October': 'oktober',
    'November': 'november', 'December': 'december',
}


def date_da():
    d = datetime.now().strftime('%d. %B %Y')
    for en, da in MONTHS_DA.items():
        d = d.replace(en, da)
    return d


def sticky_note(key, article):
    bg, accent, _ = STYLES.get(key, ('#f0f0f0', '#333', '#fafafa'))
    label = article.get('label', key)
    title = article.get('title', '')
    summary = article.get('summary', '')
    link = article.get('link', '')
    recent = article.get('recent', True)

    badge = '' if recent else ' <span style="font-size:10px;color:#aaa;">(ældre)</span>'
    link_html = (
        f'<a href="{link}" style="color:{accent};font-size:11px;text-decoration:none;">Læs artikel &#8594;</a>'
        if link else ''
    )

    return f"""<td width="185" valign="top" style="background:{bg};border-radius:6px;padding:16px 14px 14px 14px;box-shadow:3px 4px 8px rgba(0,0,0,0.18);">
  <div style="text-align:center;margin-bottom:10px;">
    <span style="display:inline-block;width:16px;height:16px;background:radial-gradient(circle at 40% 35%,#ff6b6b,#cc2222);border-radius:50%;border:2px solid #991111;box-shadow:0 2px 4px rgba(0,0,0,0.3);"></span>
  </div>
  <div style="color:{accent};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:7px;">{label}{badge}</div>
  <div style="color:#222;font-size:13px;font-weight:bold;line-height:1.4;margin-bottom:8px;">{title}</div>
  <div style="color:#555;font-size:11px;line-height:1.6;margin-bottom:10px;">{summary}</div>
  {link_html}
</td>"""


def text_box(key, article):
    _, accent, bg_light = STYLES.get(key, ('#f0f0f0', '#333', '#fafafa'))
    body = article.get('body', '') or article.get('summary', '')

    # ~40 tokens ≈ 300 tegn
    if len(body) > 300:
        body = body[:300].rsplit(' ', 1)[0] + ' …'

    body_html = f'<p style="margin:0;">{body}</p>' if body.strip() else ''

    if not body_html:
        body_html = '<p style="margin:0;color:#aaa;">Ingen tekst tilgængelig.</p>'

    return f"""<td width="185" valign="top" style="background:{bg_light};border-radius:0 0 6px 6px;border-top:2px solid {accent};padding:14px;box-shadow:3px 4px 8px rgba(0,0,0,0.10);">
  <div style="color:{accent};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">Artiklens essens</div>
  <div style="color:#444;font-size:11px;line-height:1.7;">
    {body_html}
  </div>
</td>"""


def spacer():
    return '<td width="12"></td>'


def make_note_row(keys, articles):
    cells = spacer().join(sticky_note(k, articles.get(k, {})) for k in keys)
    return f'<tr>{spacer()}{cells}{spacer()}</tr>'


def make_body_row(keys, articles):
    cells = spacer().join(text_box(k, articles.get(k, {})) for k in keys)
    return f'<tr>{spacer()}{cells}{spacer()}</tr>'


def generate():
    articles_file = TMP_DIR / 'articles.json'
    if not articles_file.exists():
        raise FileNotFoundError("Kør fetch_news.py først — articles.json mangler")

    articles = json.loads(articles_file.read_text(encoding='utf-8'))
    dato = date_da()

    row1_notes = make_note_row(['iran_us', 'iran_ir', 'iran_dropsite'], articles)
    row1_body  = make_body_row(['iran_us', 'iran_ir', 'iran_dropsite'], articles)
    row2_notes = make_note_row(['eu_economy', 'dk_economy', 'stocks'], articles)
    row2_body  = make_body_row(['eu_economy', 'dk_economy', 'stocks'], articles)

    html = f"""<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Dagligt Nyhedsbrev {dato}</title>
</head>
<body style="margin:0;padding:0;background:#e0e0e0;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#e0e0e0;padding:30px 0;">
  <tr><td align="center">
  <table width="640" cellpadding="0" cellspacing="0">

    <!-- Header -->
    <tr>
      <td style="text-align:center;padding:0 0 28px 0;">
        <h1 style="margin:0;font-size:28px;color:#333;font-family:Georgia,serif;letter-spacing:1px;">Dagligt Nyhedsbrev</h1>
        <p style="margin:6px 0 0 0;color:#888;font-size:14px;">{dato}</p>
      </td>
    </tr>

    <!-- Sektion: Iran-krigen -->
    <tr>
      <td style="padding:0 0 6px 12px;">
        <span style="font-size:12px;color:#666;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">&#9656; Iran-krigen</span>
      </td>
    </tr>
    <tr><td>
      <table width="100%" cellpadding="0" cellspacing="0">
        {row1_notes}
        <tr><td height="4"></td></tr>
        {row1_body}
        <tr><td height="20"></td></tr>
      </table>
    </td></tr>

    <!-- Sektion: Økonomi & Marked -->
    <tr>
      <td style="padding:4px 0 6px 12px;">
        <span style="font-size:12px;color:#666;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">&#9656; Økonomi &amp; Marked</span>
      </td>
    </tr>
    <tr><td>
      <table width="100%" cellpadding="0" cellspacing="0">
        {row2_notes}
        <tr><td height="4"></td></tr>
        {row2_body}
        <tr><td height="20"></td></tr>
      </table>
    </td></tr>

    <!-- Footer -->
    <tr>
      <td style="text-align:center;padding:16px 0 0 0;color:#aaa;font-size:11px;border-top:1px solid #ccc;">
        Automatisk genereret &middot; {dato}
      </td>
    </tr>

  </table>
  </td></tr>
</table>
</body>
</html>"""

    out = TMP_DIR / 'newsletter.html'
    out.write_text(html, encoding='utf-8')
    print(f"OK: HTML genereret: {out}")
    return html


if __name__ == '__main__':
    generate()
