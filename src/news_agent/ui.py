#!/usr/bin/env python
import html
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from news_agent.main import generate_notes

NOTES_PATH = Path("notes.md")

# Demo/local-only credentials as requested. Not secure for production use.
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "password"
AUTH_COOKIE_NAME = "news_agent_session"
_AUTH_SESSIONS = set()
_AUTH_LOCK = threading.Lock()

_COUNTRY_FLAGS = [
    ("AF", "Afghanistan"), ("AL", "Albania"), ("DZ", "Algeria"), ("AS", "American Samoa"),
    ("AD", "Andorra"), ("AO", "Angola"), ("AI", "Anguilla"), ("AQ", "Antarctica"),
    ("AG", "Antigua and Barbuda"), ("AR", "Argentina"), ("AM", "Armenia"), ("AW", "Aruba"),
    ("AU", "Australia"), ("AT", "Austria"), ("AZ", "Azerbaijan"), ("BS", "Bahamas"),
    ("BH", "Bahrain"), ("BD", "Bangladesh"), ("BB", "Barbados"), ("BY", "Belarus"),
    ("BE", "Belgium"), ("BZ", "Belize"), ("BJ", "Benin"), ("BM", "Bermuda"),
    ("BT", "Bhutan"), ("BO", "Bolivia"), ("BA", "Bosnia and Herzegovina"), ("BW", "Botswana"),
    ("BR", "Brazil"), ("IO", "British Indian Ocean Territory"), ("VG", "British Virgin Islands"),
    ("BN", "Brunei"), ("BG", "Bulgaria"), ("BF", "Burkina Faso"), ("BI", "Burundi"),
    ("KH", "Cambodia"), ("CM", "Cameroon"), ("CA", "Canada"), ("CV", "Cape Verde"),
    ("KY", "Cayman Islands"), ("CF", "Central African Republic"), ("TD", "Chad"), ("CL", "Chile"),
    ("CN", "China"), ("CX", "Christmas Island"), ("CC", "Cocos Islands"), ("CO", "Colombia"),
    ("KM", "Comoros"), ("CG", "Congo - Brazzaville"), ("CD", "Congo - Kinshasa"),
    ("CK", "Cook Islands"), ("CR", "Costa Rica"), ("CI", "Côte d’Ivoire"), ("HR", "Croatia"),
    ("CU", "Cuba"), ("CW", "Curaçao"), ("CY", "Cyprus"), ("CZ", "Czechia"),
    ("DK", "Denmark"), ("DJ", "Djibouti"), ("DM", "Dominica"), ("DO", "Dominican Republic"),
    ("EC", "Ecuador"), ("EG", "Egypt"), ("SV", "El Salvador"), ("GQ", "Equatorial Guinea"),
    ("ER", "Eritrea"), ("EE", "Estonia"), ("SZ", "Eswatini"), ("ET", "Ethiopia"),
    ("FK", "Falkland Islands"), ("FO", "Faroe Islands"), ("FJ", "Fiji"), ("FI", "Finland"),
    ("FR", "France"), ("GF", "French Guiana"), ("PF", "French Polynesia"), ("GA", "Gabon"),
    ("GM", "Gambia"), ("GE", "Georgia"), ("DE", "Germany"), ("GH", "Ghana"),
    ("GI", "Gibraltar"), ("GR", "Greece"), ("GL", "Greenland"), ("GD", "Grenada"),
    ("GP", "Guadeloupe"), ("GU", "Guam"), ("GT", "Guatemala"), ("GG", "Guernsey"),
    ("GN", "Guinea"), ("GW", "Guinea-Bissau"), ("GY", "Guyana"), ("HT", "Haiti"),
    ("HN", "Honduras"), ("HK", "Hong Kong"), ("HU", "Hungary"), ("IS", "Iceland"),
    ("IN", "India"), ("ID", "Indonesia"), ("IR", "Iran"), ("IQ", "Iraq"),
    ("IE", "Ireland"), ("IM", "Isle of Man"), ("IL", "Israel"), ("IT", "Italy"),
    ("JM", "Jamaica"), ("JP", "Japan"), ("JE", "Jersey"), ("JO", "Jordan"),
    ("KZ", "Kazakhstan"), ("KE", "Kenya"), ("KI", "Kiribati"), ("XK", "Kosovo"),
    ("KW", "Kuwait"), ("KG", "Kyrgyzstan"), ("LA", "Laos"), ("LV", "Latvia"),
    ("LB", "Lebanon"), ("LS", "Lesotho"), ("LR", "Liberia"), ("LY", "Libya"),
    ("LI", "Liechtenstein"), ("LT", "Lithuania"), ("LU", "Luxembourg"), ("MO", "Macao"),
    ("MG", "Madagascar"), ("MW", "Malawi"), ("MY", "Malaysia"), ("MV", "Maldives"),
    ("ML", "Mali"), ("MT", "Malta"), ("MH", "Marshall Islands"), ("MQ", "Martinique"),
    ("MR", "Mauritania"), ("MU", "Mauritius"), ("YT", "Mayotte"), ("MX", "Mexico"),
    ("FM", "Micronesia"), ("MD", "Moldova"), ("MC", "Monaco"), ("MN", "Mongolia"),
    ("ME", "Montenegro"), ("MS", "Montserrat"), ("MA", "Morocco"), ("MZ", "Mozambique"),
    ("MM", "Myanmar"), ("NA", "Namibia"), ("NR", "Nauru"), ("NP", "Nepal"),
    ("NL", "Netherlands"), ("NC", "New Caledonia"), ("NZ", "New Zealand"), ("NI", "Nicaragua"),
    ("NE", "Niger"), ("NG", "Nigeria"), ("NU", "Niue"), ("NF", "Norfolk Island"),
    ("KP", "North Korea"), ("MK", "North Macedonia"), ("MP", "Northern Mariana Islands"),
    ("NO", "Norway"), ("OM", "Oman"), ("PK", "Pakistan"), ("PW", "Palau"),
    ("PS", "Palestine"), ("PA", "Panama"), ("PG", "Papua New Guinea"), ("PY", "Paraguay"),
    ("PE", "Peru"), ("PH", "Philippines"), ("PN", "Pitcairn Islands"), ("PL", "Poland"),
    ("PT", "Portugal"), ("PR", "Puerto Rico"), ("QA", "Qatar"), ("RE", "Réunion"),
    ("RO", "Romania"), ("RU", "Russia"), ("RW", "Rwanda"), ("WS", "Samoa"),
    ("SM", "San Marino"), ("ST", "São Tomé and Príncipe"), ("SA", "Saudi Arabia"),
    ("SN", "Senegal"), ("RS", "Serbia"), ("SC", "Seychelles"), ("SL", "Sierra Leone"),
    ("SG", "Singapore"), ("SX", "Sint Maarten"), ("SK", "Slovakia"), ("SI", "Slovenia"),
    ("SB", "Solomon Islands"), ("SO", "Somalia"), ("ZA", "South Africa"), ("KR", "South Korea"),
    ("SS", "South Sudan"), ("ES", "Spain"), ("LK", "Sri Lanka"), ("BL", "St. Barthélemy"),
    ("SH", "St. Helena"), ("KN", "St. Kitts and Nevis"), ("LC", "St. Lucia"),
    ("MF", "St. Martin"), ("PM", "St. Pierre and Miquelon"),
    ("VC", "St. Vincent and Grenadines"), ("SD", "Sudan"), ("SR", "Suriname"),
    ("SE", "Sweden"), ("CH", "Switzerland"), ("SY", "Syria"), ("TW", "Taiwan"),
    ("TJ", "Tajikistan"), ("TZ", "Tanzania"), ("TH", "Thailand"), ("TL", "Timor-Leste"),
    ("TG", "Togo"), ("TK", "Tokelau"), ("TO", "Tonga"), ("TT", "Trinidad and Tobago"),
    ("TN", "Tunisia"), ("TR", "Turkey"), ("TM", "Turkmenistan"),
    ("TC", "Turks and Caicos Islands"), ("TV", "Tuvalu"), ("UG", "Uganda"),
    ("UA", "Ukraine"), ("AE", "United Arab Emirates"), ("GB", "United Kingdom"),
    ("US", "United States"), ("UY", "Uruguay"), ("UZ", "Uzbekistan"), ("VU", "Vanuatu"),
    ("VA", "Vatican City"), ("VE", "Venezuela"), ("VN", "Vietnam"),
    ("WF", "Wallis and Futuna"), ("EH", "Western Sahara"), ("YE", "Yemen"),
    ("ZM", "Zambia"), ("ZW", "Zimbabwe"),
]


def _flag_emoji(code: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


_COUNTRY_BY_CODE = {code: name for code, name in _COUNTRY_FLAGS}


def _country_label(code: str) -> str:
    code = (code or "").strip().upper()
    if not code or code == "GLOBAL":
        return "Global"
    name = _COUNTRY_BY_CODE.get(code)
    return f"{name} ({code})" if name else code


def _flags_sidebar_html(side: str) -> str:
    mid = (len(_COUNTRY_FLAGS) + 1) // 2
    flags = _COUNTRY_FLAGS[:mid] if side == "left" else _COUNTRY_FLAGS[mid:]
    items = "".join(
        f'<span class="flag" title="{html.escape(name)}">{_flag_emoji(code)}</span>'
        for code, name in flags
    )
    return f'<aside class="flags-rail flags-{side}" aria-label="World flags">{items}</aside>'


def _render_inline(text: str) -> str:
    s = html.escape(text)
    code_spans = []

    def stash_code(match):
        code_spans.append(f"<code>{match.group(1)}</code>")
        return f"@@CODESPAN{len(code_spans)-1}@@"

    s = re.sub(r"`([^`]+)`", stash_code, s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<em>\1</em>", s)
    for i, span in enumerate(code_spans):
        s = s.replace(f"@@CODESPAN{i}@@", span)
    return s


def _render_markdown(md: str) -> str:
    if not md:
        return '<p class="empty">No notes.md generated yet.</p>'

    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    in_ul = False
    in_ol = False
    paragraph = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def flush_paragraph():
        if paragraph:
            text = " ".join(p.strip() for p in paragraph if p.strip())
            if text:
                close_lists()
                out.append(f"<p>{_render_inline(text)}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            fence_lang = stripped[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code_text = "\n".join(code_lines)
            code = html.escape(code_text)
            if fence_lang.lower() == "mermaid":
                out.append(f'<pre class="mermaid">{code}</pre>')
                out.append(
                    f'<details class="mermaid-source"><summary>Mermaid source</summary>'
                    f'<pre><code class="language-mermaid">{code}</code></pre></details>'
                )
            else:
                class_attr = f' class="language-{html.escape(fence_lang)}"' if fence_lang else ""
                out.append(f"<pre><code{class_attr}>{code}</code></pre>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            close_lists()
            level = len(heading.group(1))
            out.append(f"<h{level}>{_render_inline(heading.group(2).strip())}</h{level}>")
            i += 1
            continue

        ul_match = re.match(r"^[-*+]\s+(.*)$", stripped)
        ol_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ul_match:
            flush_paragraph()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_render_inline(ul_match.group(1).strip())}</li>")
            i += 1
            continue
        if ol_match:
            flush_paragraph()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{_render_inline(ol_match.group(1).strip())}</li>")
            i += 1
            continue

        if not stripped:
            flush_paragraph()
            close_lists()
            i += 1
            continue

        close_lists()
        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    close_lists()
    return "\n".join(out)


def _country_options_html(selected_country: str = "") -> str:
    selected = (selected_country or "GLOBAL").strip().upper() or "GLOBAL"
    options = ['<option value="GLOBAL">Global (all countries)</option>']
    for code, name in _COUNTRY_FLAGS:
        sel = " selected" if code == selected else ""
        options.append(
            f'<option value="{html.escape(code)}"{sel}>{html.escape(name)} ({html.escape(code)})</option>'
        )
    return "\n        ".join(options)


def _page(topic: str = "", country: str = "GLOBAL", status: str = "", notes: str = "", error: str = "") -> bytes:
    topic_escaped = html.escape(topic)
    country_options = _country_options_html(country)
    status_html = f'<p class="status">{html.escape(status)}</p>' if status else ""
    error_html = f'<pre class="error">{html.escape(error)}</pre>' if error else ""
    notes_source = html.escape(notes) if notes else ""
    preview_html = _render_markdown(notes or "")
    download_html = (
        '<p><a href="/notes.md" download="notes.md">Download notes.md</a></p>'
        if notes
        else ""
    )
    logo_svg = """
    <svg class="logo" width="44" height="44" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="logoBg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#2563eb"/>
          <stop offset="100%" stop-color="#06b6d4"/>
        </linearGradient>
      </defs>
      <rect x="4" y="4" width="56" height="56" rx="14" fill="url(#logoBg)"/>
      <rect x="17" y="18" width="22" height="28" rx="3" fill="#ffffff" opacity="0.96"/>
      <rect x="21" y="24" width="14" height="2.5" rx="1.25" fill="#2563eb"/>
      <rect x="21" y="29" width="14" height="2.5" rx="1.25" fill="#93c5fd"/>
      <rect x="21" y="34" width="10" height="2.5" rx="1.25" fill="#93c5fd"/>
      <circle cx="41" cy="41" r="7" fill="#0f172a" opacity="0.18"/>
      <circle cx="41" cy="41" r="6" fill="none" stroke="#ffffff" stroke-width="3"/>
      <line x1="45.2" y1="45.2" x2="49.5" y2="49.5" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
    </svg>
    """
    left_flags = _flags_sidebar_html("left")
    right_flags = _flags_sidebar_html("right")
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>News Agent - World News Platform</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      line-height: 1.5;
      color: #1f2328;
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(6, 182, 212, 0.16), transparent 24%),
        linear-gradient(180deg, #eef4ff 0%, #f7fafc 45%, #eef2f7 100%);
      min-height: 100vh;
    }}
    .page {{ padding: 36px 32px; box-sizing: border-box; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(140px, 1fr) minmax(0, 980px) minmax(140px, 1fr);
      gap: 28px;
      align-items: start;
      min-height: calc(100vh - 72px);
    }}
    .flags-rail {{
      display: grid;
      grid-template-columns: repeat(auto-fill, 34px);
      grid-auto-rows: 34px;
      gap: 12px;
      justify-content: center;
      align-content: start;
      justify-items: center;
      align-items: center;
      padding: 24px 12px;
      min-height: calc(100vh - 72px);
      box-sizing: border-box;
    }}
    .flag {{
      width: 34px;
      height: 34px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      line-height: 1;
      text-align: center;
      cursor: default;
      filter: drop-shadow(0 1px 1px rgba(15, 23, 42, 0.12));
    }}
    .container {{
      width: 100%;
      margin: 0 auto;
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(4px);
      border: 1px solid rgba(208, 215, 222, 0.8);
      border-radius: 16px;
      box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
      padding: 24px;
    }}
    @media (max-width: 1100px) {{
      .page {{ padding: 24px 18px; }}
      .layout {{ grid-template-columns: 1fr; gap: 18px; min-height: auto; }}
      .flags-rail {{
        min-height: auto;
        grid-template-columns: repeat(auto-fill, 30px);
        grid-auto-rows: 30px;
        gap: 10px;
        justify-content: center;
        align-content: start;
        padding: 12px 8px;
      }}
      .flags-left {{ order: 1; }}
      .container {{ order: 2; }}
      .flags-right {{ order: 3; }}
      .flag {{ width: 30px; height: 30px; font-size: 20px; }}
    }}
    .header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }}
    .logo {{ flex: 0 0 auto; display: block; }}
    .brand h1 {{ margin: 0; font-size: 1.8rem; line-height: 1.1; }}
    .brand p {{ margin: 4px 0 0; }}
    .channels-section {{ margin: 18px 0 8px; }}
    .channels-title {{ font-size: 13px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: #475569; margin-bottom: 8px; }}
    .channels-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
    .channel-card {{ border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08); transition: transform 0.15s ease, box-shadow 0.15s ease; }}
    .channel-card:hover {{ transform: translateY(-1px); box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12); }}
    .channel-logo {{ display: block; width: 100%; height: auto; }}
    form {{ display: flex; gap: 8px; margin: 16px 0; flex-wrap: wrap; }}
    input[type=text] {{ flex: 1; min-width: 260px; padding: 10px 12px; font-size: 16px; border: 1px solid #cfd8e3; border-radius: 8px; background: #fff; }}
    select {{ min-width: 240px; padding: 10px 12px; font-size: 16px; border: 1px solid #cfd8e3; border-radius: 8px; background: #fff; }}
    button {{
      padding: 10px 16px;
      font-size: 16px;
      cursor: pointer;
      border: none;
      border-radius: 8px;
      color: #fff;
      background: linear-gradient(135deg, #2563eb, #0891b2);
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }}
    button:disabled {{ opacity: 0.7; cursor: default; }}
    .status {{ color: #0a7a43; background: #ecfdf3; border: 1px solid #b7ebc6; padding: 10px 12px; border-radius: 8px; }}
    .error {{ color: #b00020; background: #fff5f5; padding: 12px; border: 1px solid #f2caca; border-radius: 8px; white-space: pre-wrap; }}
    .hint {{ color: #555; font-size: 14px; }}
    .panel {{ border: 1px solid #d0d7de; border-radius: 10px; padding: 16px; margin: 16px 0; background: #fff; }}
    .preview h1, .preview h2, .preview h3 {{ margin-top: 1.2em; margin-bottom: 0.5em; }}
    .preview h2 {{ border-bottom: 1px solid #d8dee4; padding-bottom: 0.2em; }}
    .preview p {{ margin: 0.6em 0; }}
    .preview ul, .preview ol {{ margin: 0.6em 0 0.6em 1.4em; }}
    .preview li {{ margin: 0.25em 0; }}
    .preview pre {{ background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 12px; overflow-x: auto; }}
    .preview code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.95em; }}
    .preview :not(pre) > code {{ background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4px; padding: 0.1em 0.3em; }}
    .preview pre.mermaid {{ background: #fff; border: 1px solid #d0d7de; border-radius: 6px; padding: 12px; overflow-x: auto; text-align: center; }}
    .preview pre.mermaid svg {{ max-width: 100%; height: auto; }}
    .preview .mermaid-source {{ margin-top: 8px; }}
    .preview .mermaid-source > pre {{ margin-top: 8px; }}
    .preview a {{ color: #0969da; }}
    .empty {{ color: #666; font-style: italic; }}
    details {{ margin: 16px 0; }}
    summary {{ cursor: pointer; font-weight: 500; }}
    textarea {{ width: 100%; min-height: 320px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; padding: 12px; box-sizing: border-box; border: 1px solid #d0d7de; border-radius: 8px; background: #fff; }}
  </style>
</head>
<body>
  <div class="page">
    <div class="layout">
      {left_flags}
      <div class="container">
      <div class="header">
        {logo_svg}
        <div class="brand">
          <h1>News Agent</h1>
          <p class="hint">Global, web-search-backed, cited briefings saved to <code>notes.md</code>.</p>
        </div>
      </div>
      <p class="hint">A world news platform view: enter a topic and select a country to get local news, or choose Global for worldwide coverage.</p>
      <div class="channels-section" aria-label="News channels">
        <div class="channels-title">Channels</div>
        <div class="channels-grid">
          <div class="channel-card">
            <svg class="channel-logo" viewBox="0 0 120 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Global Wire">
              <defs><linearGradient id="cw1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0ea5e9"/><stop offset="100%" stop-color="#2563eb"/></linearGradient></defs>
              <rect x="1" y="1" width="118" height="46" rx="10" fill="#0b1220"/>
              <circle cx="24" cy="24" r="12" fill="none" stroke="url(#cw1)" stroke-width="3"/>
              <ellipse cx="24" cy="24" rx="5" ry="12" fill="none" stroke="url(#cw1)" stroke-width="2"/>
              <line x1="12" y1="24" x2="36" y2="24" stroke="url(#cw1)" stroke-width="2"/>
              <text x="42" y="22" fill="#ffffff" font-size="11" font-weight="700" font-family="-apple-system,Segoe UI,sans-serif">GLOBAL</text>
              <text x="42" y="34" fill="#7dd3fc" font-size="10" font-weight="600" font-family="-apple-system,Segoe UI,sans-serif">WIRE</text>
            </svg>
          </div>
          <div class="channel-card">
            <svg class="channel-logo" viewBox="0 0 120 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Tech Pulse">
              <defs><linearGradient id="cw2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#22c55e"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient></defs>
              <rect x="1" y="1" width="118" height="46" rx="10" fill="#071b17"/>
              <polyline points="14,30 22,30 27,18 33,34 38,24 44,24" fill="none" stroke="url(#cw2)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              <text x="50" y="22" fill="#ffffff" font-size="11" font-weight="700" font-family="-apple-system,Segoe UI,sans-serif">TECH</text>
              <text x="50" y="34" fill="#86efac" font-size="10" font-weight="600" font-family="-apple-system,Segoe UI,sans-serif">PULSE</text>
            </svg>
          </div>
          <div class="channel-card">
            <svg class="channel-logo" viewBox="0 0 120 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Market Desk">
              <defs><linearGradient id="cw3" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#ef4444"/></linearGradient></defs>
              <rect x="1" y="1" width="118" height="46" rx="10" fill="#1c1408"/>
              <rect x="14" y="28" width="6" height="8" rx="1.5" fill="#fbbf24"/>
              <rect x="22" y="23" width="6" height="13" rx="1.5" fill="#fb923c"/>
              <rect x="30" y="17" width="6" height="19" rx="1.5" fill="#f87171"/>
              <path d="M14 20 L23 16 L31 12 L38 14" fill="none" stroke="url(#cw3)" stroke-width="2.5" stroke-linecap="round"/>
              <text x="46" y="22" fill="#ffffff" font-size="11" font-weight="700" font-family="-apple-system,Segoe UI,sans-serif">MARKET</text>
              <text x="46" y="34" fill="#fcd34d" font-size="10" font-weight="600" font-family="-apple-system,Segoe UI,sans-serif">DESK</text>
            </svg>
          </div>
          <div class="channel-card">
            <svg class="channel-logo" viewBox="0 0 120 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Civic Lens">
              <defs><linearGradient id="cw4" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#a78bfa"/><stop offset="100%" stop-color="#6366f1"/></linearGradient></defs>
              <rect x="1" y="1" width="118" height="46" rx="10" fill="#15132b"/>
              <path d="M24 13 L34 17 V24 C34 30 29.5 34 24 36 C18.5 34 14 30 14 24 V17 Z" fill="none" stroke="url(#cw4)" stroke-width="2.5"/>
              <path d="M20 24 L23 27 L29 21" fill="none" stroke="#c4b5fd" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <text x="42" y="22" fill="#ffffff" font-size="11" font-weight="700" font-family="-apple-system,Segoe UI,sans-serif">CIVIC</text>
              <text x="42" y="34" fill="#c4b5fd" font-size="10" font-weight="600" font-family="-apple-system,Segoe UI,sans-serif">LENS</text>
            </svg>
          </div>
          <div class="channel-card">
            <svg class="channel-logo" viewBox="0 0 120 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Science Now">
              <defs><linearGradient id="cw5" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#14b8a6"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient></defs>
              <rect x="1" y="1" width="118" height="46" rx="10" fill="#071a1f"/>
              <ellipse cx="24" cy="24" rx="13" ry="5.5" fill="none" stroke="url(#cw5)" stroke-width="2"/>
              <ellipse cx="24" cy="24" rx="13" ry="5.5" transform="rotate(60 24 24)" fill="none" stroke="url(#cw5)" stroke-width="2"/>
              <ellipse cx="24" cy="24" rx="13" ry="5.5" transform="rotate(120 24 24)" fill="none" stroke="url(#cw5)" stroke-width="2"/>
              <circle cx="24" cy="24" r="2.5" fill="#5eead4"/>
              <text x="44" y="22" fill="#ffffff" font-size="11" font-weight="700" font-family="-apple-system,Segoe UI,sans-serif">SCIENCE</text>
              <text x="44" y="34" fill="#99f6e4" font-size="10" font-weight="600" font-family="-apple-system,Segoe UI,sans-serif">NOW</text>
            </svg>
          </div>
        </div>
      </div>
      <form method="post" action="/generate">
        <input type="text" name="topic" placeholder="e.g. AI agents in enterprise software" value="{topic_escaped}" required />
        <select name="country" aria-label="Country">
          {country_options}
        </select>
        <button type="submit">Generate briefing</button>
      </form>
      {status_html}
      {error_html}
      {download_html}
      <h2>Briefing preview</h2>
      <div class="panel preview">{preview_html}</div>
      <details>
        <summary>Raw notes.md</summary>
        <textarea readonly placeholder="Generated notes.md will appear here...">{notes_source}</textarea>
      </details>
      </div>
      {right_flags}
    </div>
  </div>
  <script>
    const form = document.querySelector('form');
    if (form) {{
      form.addEventListener('submit', () => {{
        const btn = form.querySelector('button');
        if (btn) {{ btn.disabled = true; btn.textContent = 'Generating...'; }}
      }});
    }}
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>
    if (window.mermaid) {{
      mermaid.initialize({{ startOnLoad: true, securityLevel: 'strict' }});
    }}
  </script>
</body>
</html>"""
    return body.encode("utf-8")


def _login_page(error: str = "", username: str = "") -> bytes:
  error_html = f'<p class="error">{html.escape(error)}</p>' if error else ""
  username_escaped = html.escape(username)
  body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Login - News Agent</title>
  <style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 28%),
      radial-gradient(circle at top right, rgba(6, 182, 212, 0.16), transparent 24%),
      linear-gradient(180deg, #eef4ff 0%, #f7fafc 45%, #eef2f7 100%);
    color: #1f2328;
  }}
  .card {{
    width: 100%;
    max-width: 420px;
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(208,215,222,0.8);
    border-radius: 16px;
    box-shadow: 0 12px 40px rgba(15,23,42,0.08);
    padding: 28px;
    margin: 24px;
  }}
  h1 {{ margin: 0 0 8px; font-size: 1.6rem; }}
  p {{ margin: 0 0 16px; color: #555; }}
  label {{ display: block; font-weight: 500; margin: 12px 0 6px; }}
  input {{
    width: 100%;
    box-sizing: border-box;
    padding: 10px 12px;
    font-size: 16px;
    border: 1px solid #cfd8e3;
    border-radius: 8px;
  }}
  button {{
    margin-top: 18px;
    width: 100%;
    padding: 10px 16px;
    font-size: 16px;
    cursor: pointer;
    border: none;
    border-radius: 8px;
    color: #fff;
    background: linear-gradient(135deg, #2563eb, #0891b2);
  }}
  .error {{ color: #b00020; background: #fff5f5; padding: 10px 12px; border: 1px solid #f2caca; border-radius: 8px; margin-bottom: 12px; }}
  .note {{ font-size: 13px; color: #666; margin-top: 14px; }}
  code {{ background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4px; padding: 0.1em 0.3em; }}
  </style>
</head>
<body>
  <div class="card">
  <h1>News Agent Login</h1>
  <p>Sign in to access the world news briefing UI.</p>
  {error_html}
  <form method="post" action="/login">
    <label for="username">Username</label>
    <input id="username" name="username" type="text" value="{username_escaped}" autocomplete="username" required />
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required />
    <button type="submit">Log in</button>
  </form>
  <p class="note">Demo/local login configured for this UI.</p>
  </div>
</body>
</html>"""
  return body.encode("utf-8")


class NewsAgentHandler(BaseHTTPRequestHandler):
    server_version = "NewsAgentUI/1.0"

    def _parse_cookies(self):
        header = self.headers.get("Cookie", "")
        cookies = {}
        for part in header.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                cookies[k.strip()] = v.strip()
        return cookies

    def _is_authenticated(self):
        token = self._parse_cookies().get(AUTH_COOKIE_NAME, "")
        if not token:
            return False
        with _AUTH_LOCK:
            return token in _AUTH_SESSIONS

    def _redirect(self, location, extra_headers=None):
        self.send_response(302)
        self.send_header("Location", location)
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if self.path == "/login":
            if self._is_authenticated():
                self._redirect("/")
                return
            self._send_html(_login_page())
            return

        if not self._is_authenticated():
            self._redirect("/login")
            return

        if self.path in ("/", "/index.html"):
            notes = NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else ""
            self._send_html(_page(notes=notes))
            return
        if self.path == "/notes.md":
            if not NOTES_PATH.exists():
                self.send_error(404, "notes.md not found")
                return
            data = NOTES_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Disposition", 'attachment; filename="notes.md"')
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404, "Not found")

    def do_POST(self):
        if self.path == "/login":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
            except ValueError:
                length = 0
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            params = parse_qs(body)
            username = (params.get("username", [""])[0] or "").strip()
            password = params.get("password", [""])[0] or ""
            if secrets.compare_digest(username, AUTH_USERNAME) and secrets.compare_digest(password, AUTH_PASSWORD):
                token = secrets.token_urlsafe(32)
                with _AUTH_LOCK:
                    _AUTH_SESSIONS.add(token)
                cookie = f"{AUTH_COOKIE_NAME}={token}; HttpOnly; Path=/; SameSite=Lax"
                self._redirect("/", extra_headers=[("Set-Cookie", cookie)])
                return
            self._send_html(_login_page(error="Invalid username or password.", username=username), status=401)
            return

        if not self._is_authenticated():
            self._redirect("/login")
            return

        if self.path != "/generate":
            self.send_error(404, "Not found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            length = 0
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        params = parse_qs(body)
        topic = (params.get("topic", [""])[0] or "").strip()
        country_code = (params.get("country", ["GLOBAL"])[0] or "GLOBAL").strip().upper()
        country_label = _country_label(country_code)

        if not topic:
            self._send_html(_page(topic=topic, country=country_code, error="A topic is required."), status=400)
            return

        try:
            generate_notes(topic, output_path=NOTES_PATH, country=country_label)
            notes = NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else ""
            self._send_html(
                _page(
                    topic=topic,
                    country=country_code,
                    status=f'Briefing generated for "{topic}" ({country_label}) and saved to notes.md.',
                    notes=notes,
                )
            )
        except Exception as e:
            existing = NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else ""
            self._send_html(_page(topic=topic, country=country_code, notes=existing, error=str(e)), status=500)

    def log_message(self, format, *args):
        # Keep UI output concise; uncomment for request logs.
        return

    def _send_html(self, content: bytes, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run_server(host: str = "127.0.0.1", port: int = 8000):
    server = ThreadingHTTPServer((host, port), NewsAgentHandler)
    print(f"News Agent UI running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
