import json
import os
import random
import re
import textwrap
import time
from datetime import date, datetime, timedelta, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER = os.environ.get('PROFILE_USER', 'b8mi')
PROJECTS = {
    'Python-PDF-Toolkits': ('Five offline PDF utilities for merging, cropping, compression and conversion.', 'pdf'),
    'MISBA7ATY': ('A lightweight Arabic dhikr counter with progress tracking.', 'beads'),
    'Media_Converter': ('Offline audio and video conversion using Python and FFmpeg.', 'media'),
    'MathsTools': ('Interactive graphing, geometry, matrices and mathematics tools.', 'math'),
}
PANEL = '#081321'
EDGE = '#254660'
ICE = '#9ce8ff'
BLUE = '#44b9ed'
MUTED = '#9aafc5'
WHITE = '#e2f4ff'
DARK = '#081321'

FONT = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01111', '10000', '10000', '10000', '10000', '10000', '01111'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01111', '10000', '10000', '10111', '10001', '10001', '01111'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('111', '010', '010', '010', '010', '010', '111'),
    'J': ('00111', '00010', '00010', '00010', '10010', '10010', '01100'),
    'K': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'Q': ('01110', '10001', '10001', '10001', '10101', '10010', '01101'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '10101', '01010'),
    'X': ('10001', '10001', '01010', '00100', '01010', '10001', '10001'),
    'Y': ('10001', '10001', '01010', '00100', '00100', '00100', '00100'),
    'Z': ('11111', '00001', '00010', '00100', '01000', '10000', '11111'),
    '0': ('01110', '10001', '10011', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00010', '00100', '01000', '11111'),
    '3': ('11110', '00001', '00001', '01110', '00001', '00001', '11110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '10000', '11110', '00001', '00001', '11110'),
    '6': ('01110', '10000', '10000', '11110', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00010', '00100', '01000', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00001', '01110'),
    '/': ('00001', '00010', '00010', '00100', '01000', '01000', '10000'),
    ':': ('000', '010', '010', '000', '010', '010', '000'),
    '.': ('000', '000', '000', '000', '000', '011', '011'),
    ',': ('000', '000', '000', '000', '011', '011', '010'),
    '-': ('00000', '00000', '00000', '11111', '00000', '00000', '00000'),
    '+': ('00000', '00100', '00100', '11111', '00100', '00100', '00000'),
    '>': ('10000', '01000', '00100', '00010', '00100', '01000', '10000'),
    '<': ('00001', '00010', '00100', '01000', '00100', '00010', '00001'),
    '!': ('010', '010', '010', '010', '010', '000', '010'),
    '?': ('01110', '10001', '00001', '00010', '00100', '00000', '00100'),
    '|': ('010', '010', '010', '010', '010', '010', '010'),
    '_': ('00000', '00000', '00000', '00000', '00000', '00000', '11111'),
    '(': ('001', '010', '100', '100', '100', '010', '001'),
    ')': ('100', '010', '001', '001', '001', '010', '100'),
    "'": ('010', '010', '001', '000', '000', '000', '000'),
    ' ': ('000', '000', '000', '000', '000', '000', '000'),
}

ICONS = {
    'pdf': ['001111100', '001222100', '001222111', '001222221', '001212221', '001222221', '001211121', '001222221', '001111111'],
    'beads': ['000111000', '001000100', '010000010', '100000001', '100000001', '100000001', '010000010', '001010100', '000111000'],
    'media': ['111111111', '122222221', '120222221', '120022221', '120002221', '120022221', '120222221', '122222221', '111111111'],
    'math': ['100000001', '100000010', '100000100', '100001000', '111111111', '100100000', '101000000', '110000000', '111111111'],
}


class ContributionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []
        self.tooltips = {}
        self.active_tooltip = None
        self.tooltip_text = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag.lower() == 'td' and values.get('data-date'):
            self.cells.append({
                'date': values.get('data-date'),
                'level': int(values.get('data-level', '0') or 0),
                'id': values.get('id'),
                'aria': values.get('aria-label', ''),
                'count': values.get('data-count'),
            })
        if tag.lower() == 'tool-tip' and values.get('for'):
            self.active_tooltip = values['for']
            self.tooltip_text = []

    def handle_data(self, data):
        if self.active_tooltip is not None:
            self.tooltip_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == 'tool-tip' and self.active_tooltip is not None:
            self.tooltips[self.active_tooltip] = ' '.join(self.tooltip_text)
            self.active_tooltip = None
            self.tooltip_text = []


def rect(x, y, w, h, color, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" {extra}/>'


def pixel_text(x, y, value, size=10, color=WHITE, extra=''):
    value = str(value).upper()
    scale = size / 7
    advance = 6 * scale
    width = max(0, len(value) * advance - scale)
    if 'text-anchor="end"' in extra:
        x -= width
    elif 'text-anchor="middle"' in extra:
        x -= width / 2
    top = y - 7 * scale
    path = []
    for index, char in enumerate(value):
        glyph = FONT.get(char, FONT[' '])
        for row, pattern in enumerate(glyph):
            for col, bit in enumerate(pattern):
                if bit == '1':
                    px = round(x + index * advance + col * scale, 3)
                    py = round(top + row * scale, 3)
                    sw = round(scale, 3)
                    path.append(f'M{px} {py}h{sw}v{sw}h-{sw}z')
    return f'<path d="{"".join(path)}" fill="{color}" shape-rendering="crispEdges"/>'


def svg(width, height, label, body, css=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label={quoteattr(label)}><style>{css}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>\n'


def write(name, content):
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(content, encoding='utf-8')


def request_json(url, token=None, accept='application/vnd.github+json'):
    headers = {'Accept': accept, 'User-Agent': 'b8mi-pixel-profile'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        headers['X-GitHub-Api-Version'] = '2022-11-28'
    req = Request(url, headers=headers)
    for attempt in range(4):
        try:
            with urlopen(req, timeout=35) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (403, 429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'GitHub API returned HTTP {error.code}: {url}') from error
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError(f'Could not retrieve {url}')


def request_text(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 b8mi-pixel-profile'})
    for attempt in range(4):
        try:
            with urlopen(req, timeout=35) as response:
                return response.read().decode('utf-8', 'replace')
        except HTTPError as error:
            if error.code not in (403, 429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'GitHub contributions page returned HTTP {error.code}') from error
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError('Could not retrieve GitHub contribution history')


def parse_contributions(source):
    parser = ContributionParser()
    parser.feed(source)
    if not parser.cells:
        raise RuntimeError('GitHub returned no contribution-day cells. The contribution page format may have changed.')
    counts = {}
    levels = {}
    exact = True
    for cell in parser.cells:
        day = cell['date']
        level = cell['level']
        raw_count = cell.get('count')
        count = int(raw_count) if raw_count and raw_count.isdigit() else None
        tooltip = parser.tooltips.get(cell.get('id'), '') if cell.get('id') else ''
        tooltip = unescape(re.sub(r'<[^>]+>', ' ', tooltip))
        if count is None and tooltip:
            if re.search(r'no contributions', tooltip, re.I):
                count = 0
            else:
                match = re.search(r'([\d,]+)\s+contributions?', tooltip, re.I)
                if match:
                    count = int(match.group(1).replace(',', ''))
        if count is None and cell.get('aria'):
            aria = unescape(cell['aria'])
            if re.search(r'no contributions', aria, re.I):
                count = 0
            else:
                match = re.search(r'([\d,]+)\s+contributions?', aria, re.I)
                if match:
                    count = int(match.group(1).replace(',', ''))
        if count is None:
            if level == 0:
                count = 0
            else:
                exact = False
                count = 1
        counts[day] = count
        levels[day] = level
    if len(counts) < 300:
        raise RuntimeError(f'GitHub returned only {len(counts)} contribution days; refusing to publish incomplete stats.')
    if not exact:
        raise RuntimeError('Some active contribution days did not include exact tooltip counts; refusing to publish partial totals.')
    return counts, levels


def streaks(days, today):
    best = 0
    run = 0
    previous = None
    for key in sorted(days):
        day = date.fromisoformat(key)
        if day > today:
            continue
        if previous is not None and day != previous + timedelta(days=1):
            run = 0
        run = run + 1 if days[key] > 0 else 0
        best = max(best, run)
        previous = day
    end = today if days.get(today.isoformat(), 0) else today - timedelta(days=1)
    current = 0
    while days.get(end.isoformat(), 0) > 0:
        current += 1
        end -= timedelta(days=1)
    return current, best


def request_graphql(query, variables, token):
    if not token:
        return None
    headers = {
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'User-Agent': 'b8mi-pixel-profile',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    payload = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
    req = Request('https://api.github.com/graphql', data=payload, headers=headers, method='POST')
    try:
        with urlopen(req, timeout=35) as response:
            result = json.load(response)
        if result.get('errors') or not result.get('data', {}).get('user'):
            return None
        return result['data']['user']['contributionsCollection']
    except Exception:
        return None


def search_count(query, token, accept='application/vnd.github+json', endpoint='issues'):
    url = 'https://api.github.com/search/' + endpoint + '?' + urlencode({'q': query, 'per_page': 1})
    result = request_json(url, token, accept=accept)
    return result.get('total_count')


def fetch():
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    profile = request_json(f'https://api.github.com/users/{USER}', token)
    repos = []
    for page in range(1, 101):
        url = 'https://api.github.com/users/' + USER + '/repos?' + urlencode({'type': 'owner', 'per_page': 100, 'page': page})
        batch = request_json(url, token)
        repos.extend(batch)
        if len(batch) < 100:
            break

    by_name = {repo['name'].casefold(): repo for repo in repos}
    for name in PROJECTS:
        if name.casefold() not in by_name:
            try:
                by_name[name.casefold()] = request_json(f'https://api.github.com/repos/{USER}/{name}', token)
            except Exception:
                pass
    project_map = {name: by_name.get(name.casefold()) for name in PROJECTS}

    now = datetime.now(timezone.utc)
    first_day = now.date() - timedelta(days=364)
    first = first_day.isoformat()
    last = now.date().isoformat()
    days = {}
    levels = {}
    contributions = None
    commits = None
    prs = None
    current = None
    best = None

    query = "query($login:String!, $from:DateTime!, $to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){totalCommitContributions totalPullRequestContributions contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"
    graph_data = request_graphql(query, {
        'login': USER,
        'from': first_day.isoformat() + 'T00:00:00Z',
        'to': last + 'T23:59:59Z',
    }, token)

    if graph_data:
        calendar = graph_data['contributionCalendar']
        days = {day['date']: day['contributionCount'] for week in calendar['weeks'] for day in week['contributionDays']}
        level_map = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
        levels = {day['date']: level_map.get(day['contributionLevel'], 0) for week in calendar['weeks'] for day in week['contributionDays']}
        contributions = calendar['totalContributions']
        commits = graph_data.get('totalCommitContributions')
        prs = graph_data.get('totalPullRequestContributions')
    else:
        try:
            html = request_text(f'https://github.com/users/{USER}/contributions?' + urlencode({'from': first, 'to': last}))
            days, levels = parse_contributions(html)
            contributions = sum(days.values())
        except Exception:
            days, levels = {}, {}

    if days:
        current, best = streaks(days, now.date())

    if commits is None:
        try:
            commit_query = f'author:{USER} committer-date:{first}..{last}'
            commits = search_count(commit_query, token, 'application/vnd.github.cloak-preview+json', 'commits')
        except Exception:
            commits = None
    if prs is None:
        try:
            pr_query = f'is:pr author:{USER} created:{first}..{last}'
            prs = search_count(pr_query, token)
        except Exception:
            prs = None

    featured_stars = None if any(repo is None for repo in project_map.values()) else sum(repo.get('stargazers_count', 0) for repo in project_map.values())
    return {
        'name': profile.get('name') or USER,
        'followers': profile.get('followers', 0),
        'repos': profile.get('public_repos', len(repos)),
        'stars': featured_stars,
        'commits': commits,
        'prs': prs,
        'contributions': contributions,
        'total': sum(days.values()) if days else None,
        'current': current,
        'best': best,
        'days': days,
        'levels': levels,
        'projects': project_map,
        'date': now.date().isoformat(),
        'year': now.year,
        'synced': now.strftime('%Y-%m-%d %H:%M UTC'),
        'cache_version': now.strftime('%Y%m%d%H%M%S'),
    }


def moon(x, y):
    pattern = [
        '0011110',
        '0110000',
        '1100000',
        '1100000',
        '1100000',
        '1100000',
        '1100000',
        '0110000',
        '0011110',
    ]
    parts = []
    for row, line in enumerate(pattern):
        for col, bit in enumerate(line):
            if bit == '1':
                parts.append(rect(x + col * 2, y + row * 2, 2, 2, '#a7e5f5'))
    return ''.join(parts)


def line_points(start, end):
    x1, y1 = start
    x2, y2 = end
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    error = dx + dy
    points = []
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        twice = 2 * error
        if twice >= dy:
            error += dy
            x1 += sx
        if twice <= dx:
            error += dx
            y1 += sy
    return points


def draw_math_icon(parts):
    x0, y0, step = 27, 35, 8
    axis = '#6250c8'
    y_equals_3 = '#4f9fe0'
    y_equals_x = '#76e6ff'

    # Solid coordinate axes.
    for row in range(9):
        parts.append(rect(x0, y0 + row * step, 8, 8, axis))
    for col in range(9):
        parts.append(rect(x0 + col * step, y0 + 8 * step, 8, 8, axis))

    # y = 3: a horizontal line across the graph.
    for col in range(1, 9):
        parts.append(rect(x0 + col * step, y0 + 5 * step, 8, 8, y_equals_3))

    # y = x: a rising, stepped pixel line.
    diagonal = [(1, 7), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 1), (8, 0)]
    for col, row in diagonal:
        parts.append(rect(x0 + col * step, y0 + row * step, 8, 8, y_equals_x))


def draw_beads_icon(parts):
    icon_x = 27
    colors = {'1': BLUE, '2': '#205676'}
    parts.append('<g shape-rendering="crispEdges">')
    for row, line in enumerate(ICONS['beads']):
        for col, value in enumerate(line):
            if value != '0':
                parts.append(rect(icon_x + col * 8, 35 + row * 8, 8, 8, colors.get(value, BLUE)))
    parts.append('</g>')


def room(data):
    rng = random.Random(91)
    fish_rng = random.Random(time.time_ns())
    parts = [rect(0, 0, 220, 112, '#0a1423'), rect(0, 0, 220, 69, '#12263b'), rect(0, 90, 220, 22, '#0a1826')]
    for x in range(0, 220, 11):
        parts.append(rect(x, 0, 1, 90, '#192f45'))
    parts += [rect(5, 6, 210, 60, '#06101e'), rect(8, 9, 204, 54, '#0b203d')]
    parts.append('<g clip-path="url(#window)">')
    for _ in range(82):
        sx = rng.randrange(9, 212)
        sy = rng.randrange(10, 42)
        if 27 <= sx <= 49 and 14 <= sy <= 33:
            continue
        color = rng.choice(['#49718d', '#91d2ef', '#254460'])
        parts.append(rect(sx, sy, 1, 1, color))
    parts.append(moon(28, 14))
    parts.append('<g class="meteor meteor-ltr" shape-rendering="crispEdges">')
    parts += [rect(-6, 2, 2, 1, '#2d5f78'), rect(-5, 2, 1, 1, '#417f9f'), rect(-4, 1, 2, 1, '#5fa8c7'), rect(-2, 1, 2, 1, '#91d8f0'), rect(0, 0, 2, 1, '#d8f7ff'), rect(2, 0, 1, 1, '#ffffff')]
    parts.append('</g>')
    parts.append('<g class="meteor meteor-rtl" shape-rendering="crispEdges">')
    parts += [rect(6, 2, 2, 1, '#2d5f78'), rect(5, 2, 1, 1, '#417f9f'), rect(3, 1, 2, 1, '#5fa8c7'), rect(1, 1, 2, 1, '#91d8f0'), rect(-1, 0, 2, 1, '#d8f7ff'), rect(-2, 0, 1, 1, '#ffffff')]
    parts.append('</g>')
    flicker_css = []
    light_index = 0
    for x in range(8, 212, 9):
        height = rng.randrange(8, 30)
        parts.append(rect(x, 61 - height, 8, height, '#132c47'))
        for yy in range(63 - height, 59, 4):
            for xx in (x + 1, x + 5):
                if rng.random() < 0.55:
                    light_index += 1
                    class_name = f'light{light_index}'
                    delay = rng.randrange(0, 100) / 10
                    duration = rng.randrange(45, 90) / 10
                    dim = rng.choice(['.08', '.16', '.24', '.34'])
                    off_start = rng.randrange(8, 76)
                    off_end = min(99, off_start + rng.randrange(2, 7))
                    flicker_css.append(f'@keyframes {class_name}{{0%,{off_start - 1}%,{off_end + 1}%,100%{{opacity:1}}{off_start}%,{off_end}%{{opacity:{dim}}}}}.{class_name}{{animation:{class_name} {duration}s steps(1) -{delay}s infinite}}')
                    parts.append(rect(xx, yy, 1, 2, rng.choice(['#3e9ec8', '#7de2ff', '#254d6d']), f'class="{class_name}"'))
    parts += [rect(8, 61, 204, 2, '#236080'), '</g>', rect(5, 64, 210, 3, '#3b5970')]
    for y in range(94, 112, 6):
        parts.append(rect(0, y, 220, 1, '#192c40'))
    parts += [rect(19, 79, 182, 4, '#35516a'), rect(19, 83, 182, 2, '#183146'), rect(24, 85, 4, 16, '#243c51'), rect(193, 85, 4, 16, '#243c51'), rect(40, 45, 72, 31, '#385871'), rect(42, 47, 68, 27, '#06121f'), rect(72, 76, 8, 3, '#385871'), rect(65, 78, 22, 1, '#56788c')]
    parts.append(pixel_text(45, 52, '> B8MI / TERMINAL', 3.1, ICE))
    labels = ['> PUBLIC REPOSITORIES', '> FEATURED STARS', f'> CONTRIBUTIONS / {data.get("year", "YEAR")}']
    values = [data.get('repos'), data.get('stars'), data.get('contributions')]
    for index, (label, value) in enumerate(zip(labels, values)):
        parts.append(pixel_text(45, 58 + index * 5, label, 2.55, MUTED))
        parts.append(pixel_text(107, 58 + index * 5, '--' if value is None else value, 2.8, ICE, 'text-anchor="end"'))
    parts.append(rect(45, 70, 3, 1, ICE, 'class="blink"'))
    parts += [rect(38, 80, 65, 1, '#7590a4'), rect(116, 77, 7, 2, '#5d7c95'), rect(129, 47, 66, 32, '#51738b'), rect(131, 49, 62, 28, '#123c58'), rect(131, 74, 62, 3, '#24465c')]
    parts.append('<g clip-path="url(#tank)">')
    plants = [
        (135, 66, [(0, 3, 1, 4, '#24545b'), (-1, 2, 1, 2, '#1d4b52'), (1, 1, 1, 2, '#285c60'), (2, 3, 1, 2, '#1e5056')]),
        (141, 67, [(0, 2, 1, 4, '#214e55'), (-1, 1, 1, 2, '#1b454d'), (1, 0, 1, 2, '#285a60')]),
        (182, 66, [(0, 3, 1, 4, '#24545b'), (-1, 2, 1, 2, '#1d4b52'), (1, 1, 1, 2, '#285c60'), (2, 3, 1, 2, '#1e5056')]),
        (188, 67, [(0, 2, 1, 4, '#214e55'), (-1, 1, 1, 2, '#1b454d'), (1, 0, 1, 2, '#285a60')]),
    ]
    for base_x, base_y, pixels in plants:
        for dx, dy, width, height, color in pixels:
            parts.append(rect(base_x + dx, base_y + dy, width, height, color))
    for column in range(60):
        if column in (0, 1, 58, 59):
            height = 4
        elif column < 8 or column > 51:
            height = 3
        else:
            height = fish_rng.choice([2, 2, 2, 3])
        if 17 <= column <= 42 and fish_rng.random() < 0.18:
            height = 3
        top = 74 - height
        color = fish_rng.choice(['#667568', '#718071', '#596b68', '#7a806e'])
        parts.append(rect(132 + column, top, 1, height, color))
        if column % 4 == 0:
            parts.append(rect(132 + column, top, 1, 1, '#92917a'))

    fish_colors = ['#7feaff', '#f4bd79', '#82a9f5']
    fish_starts = [(142, 56), (159, 61), (175, 66)]
    lane_ranges = [(54, 58), (59, 63), (64, 68)]
    fish_css = []
    for index, ((start_x, start_y), color, lane) in enumerate(zip(fish_starts, fish_colors, lane_ranges)):
        route = [(start_x, start_y)]
        for _ in range(5):
            previous = route[-1]
            target_x = max(138, min(184, round(fish_rng.gauss(160, 9))))
            if abs(target_x - previous[0]) < 8:
                target_x = previous[0] + (10 if target_x <= previous[0] else -10)
            target_x = max(138, min(184, target_x))
            target_y = fish_rng.randint(lane[0], lane[1])
            route.append((target_x, target_y))
        route.append((start_x, start_y))
        waits = [fish_rng.randint(5, 12) for _ in range(len(route) - 1)]
        travels = [3 + fish_rng.random() * 1.2 for _ in range(len(route) - 1)]
        total = sum(waits) + sum(travels)
        elapsed = 0.0
        motion_frames = [(0.0, 0, 0)]
        facing_frames = [(0.0, 'right' if route[1][0] >= route[0][0] else 'left')]
        for segment, (current, target) in enumerate(zip(route, route[1:])):
            facing = 'right' if target[0] >= current[0] else 'left'
            facing_frames.append((elapsed, facing))
            elapsed += waits[segment]
            motion_frames.append((elapsed, current[0] - start_x, current[1] - start_y))
            elapsed += travels[segment]
            motion_frames.append((elapsed, target[0] - start_x, target[1] - start_y))
            facing_frames.append((elapsed, facing))
        route_name = f'fish-route-{index}'
        left_name = f'fish-left-{index}'
        right_name = f'fish-right-{index}'
        route_rules = []
        for moment, dx, dy in motion_frames:
            percent = moment / total * 100
            route_rules.append(f'{percent:.4f}%{{transform:translate({dx}px,{dy}px)}}')
        phase = fish_rng.random() * total
        fish_css.append(f'@keyframes {route_name}{{{"".join(route_rules)}}}.fish-{index}{{animation:{route_name} {total:.3f}s linear -{phase:.3f}s infinite}}')
        left_rules = []
        right_rules = []
        for moment, direction in facing_frames:
            percent = moment / total * 100
            left_rules.append(f'{percent:.4f}%{{opacity:{1 if direction == "left" else 0}}}')
            right_rules.append(f'{percent:.4f}%{{opacity:{1 if direction == "right" else 0}}}')
        fish_css.append(f'@keyframes {left_name}{{{"".join(left_rules)}}}.fish-left-{index}{{animation:{left_name} {total:.3f}s steps(1,end) -{phase:.3f}s infinite}}')
        fish_css.append(f'@keyframes {right_name}{{{"".join(right_rules)}}}.fish-right-{index}{{animation:{right_name} {total:.3f}s steps(1,end) -{phase:.3f}s infinite}}')
        parts.append(f'<g class="fish fish-{index}">')
        parts.append(f'<g class="fish-left-{index}" shape-rendering="crispEdges">')
        parts += [rect(start_x + 7, start_y + 1, 2, 3, color), rect(start_x + 3, start_y + 1, 4, 3, color), rect(start_x, start_y, 3, 5, color), rect(start_x + 1, start_y + 1, 1, 1, '#0b203d')]
        parts.append('</g>')
        parts.append(f'<g class="fish-right-{index}" shape-rendering="crispEdges">')
        parts += [rect(start_x, start_y + 1, 2, 3, color), rect(start_x + 2, start_y + 1, 4, 3, color), rect(start_x + 6, start_y, 3, 5, color), rect(start_x + 7, start_y + 1, 1, 1, '#0b203d')]
        parts.append('</g></g>')

    for index, y in enumerate([67, 63, 60, 56, 65, 59, 54]):
        parts.append(rect(137 + index * 8, y, 1, 1, '#9fe7f4', f'class="bubble" style="animation-delay:-{index * .6}s"'))
    parts.append('</g>')
    parts += [rect(131, 49, 62, 1, '#78c6e2'), rect(131, 49, 1, 28, '#78c6e2'), rect(129, 77, 66, 2, '#5c8095')]
    parts += [rect(7, 91, 206, 15, '#081321'), pixel_text(12, 101, '3ZMI AQUARIUM', 5, ICE), pixel_text(208, 101, 'CODE // EFFICIENT', 3.5, MUTED, 'text-anchor="end"')]
    definitions = '<defs><clipPath id="window"><rect x="8" y="9" width="204" height="54"/></clipPath><clipPath id="tank"><rect x="132" y="50" width="60" height="24"/></clipPath></defs>'
    meteor_css = '@keyframes meteor-ltr{0%{transform:translate(-8px,33px);opacity:0}0.2%{opacity:1}1.1%{transform:translate(38px,21px);opacity:1}2.2%{transform:translate(92px,14px);opacity:1}3.3%{transform:translate(152px,18px);opacity:1}4.6%{transform:translate(228px,34px);opacity:1}4.8%,100%{transform:translate(228px,34px);opacity:0}}@keyframes meteor-rtl{0%{transform:translate(228px,34px);opacity:0}0.2%{opacity:1}1.1%{transform:translate(176px,20px);opacity:1}2.2%{transform:translate(122px,13px);opacity:1}3.3%{transform:translate(62px,17px);opacity:1}4.6%{transform:translate(-8px,32px);opacity:1}4.8%,100%{transform:translate(-8px,32px);opacity:0}}.meteor{opacity:0}.meteor-ltr{animation:meteor-ltr 30s linear 3s infinite}.meteor-rtl{animation:meteor-rtl 30s linear 18s infinite}'
    css = '.blink{animation:cursor 1s steps(1) infinite}.bubble{animation:bubble 4s linear infinite}@keyframes cursor{50%{opacity:0}}@keyframes bubble{to{transform:translateY(-20px);opacity:0}}' + meteor_css + ''.join(flicker_css) + ''.join(fish_css)
    body = definitions + '<g transform="scale(4)" shape-rendering="crispEdges">' + ''.join(parts) + '</g>'
    write('room.svg', svg(880, 448, 'Midnight pixel-art workstation, city skyline and aquarium with moving fish and shooting stars', body, css))


def card(name, description, icon, repo):
    parts = [rect(.5, .5, 429, 167, PANEL, f'rx="10" stroke="{EDGE}"'), rect(14, 19, 98, 104, '#0b2b45', 'rx="6"'), rect(15, 20, 96, 102, 'none', 'rx="6" stroke="#275472"')]
    if icon == 'math':
        draw_math_icon(parts)
    elif icon == 'beads':
        draw_beads_icon(parts)
    else:
        icon_x = 19 if icon == 'pdf' else 27
        parts.append('<g shape-rendering="crispEdges">')
        for row, line in enumerate(ICONS[icon]):
            for col, value in enumerate(line):
                if value != '0':
                    parts.append(rect(icon_x + col * 8, 35 + row * 8, 8, 8, BLUE if value == '1' else '#205676'))
        parts.append('</g>')
    parts.append(pixel_text(128, 37, name, 13, WHITE))
    for index, line in enumerate(textwrap.wrap(description, width=39)[:4]):
        parts.append(pixel_text(128, 59 + index * 15, line, 8.5, MUTED))
    stars = repo.get('stargazers_count') if repo else None
    language = (repo.get('language') or 'PYTHON') if repo is not None else 'PYTHON'
    parts.append(pixel_text(18, 148, language[:20], 8.5, ICE))
    parts.append(pixel_text(412, 148, 'STARS: ' + ('--' if stars is None else str(stars)), 8.5, ICE, 'text-anchor="end"'))
    write(name + '.svg', svg(430, 168, name + ' project card with live repository stars', ''.join(parts)))


def intro():
    parts = [pixel_text(440, 28, 'I BUILD SOFTWARE, GAMES AND TOOLS THAT MAKE THINGS A LITTLE EASIER.', 10, WHITE, 'text-anchor="middle"'), pixel_text(440, 49, 'STAR A REPOSITORY IF YOU FIND IT USEFUL.', 9, ICE, 'text-anchor="middle"')]
    write('intro.svg', svg(880, 62, 'Pixel-art introduction', ''.join(parts)))



def projects_heading():
    parts = [pixel_text(24, 24, 'PROJECTS', 14, ICE), rect(126, 20, 730, 1, EDGE), rect(126, 22, 730, 1, '#18354d')]
    write('projects-heading.svg', svg(880, 34, 'Projects section', ''.join(parts)))


def stats(data):
    parts = [rect(.5, .5, 879, 129, PANEL, f'rx="10" stroke="{EDGE}"')]
    metrics = [
        ('repos', 'PUBLIC REPOSITORIES'),
        ('followers', 'FOLLOWERS'),
        ('stars', 'FEATURED REPO STARS'),
        ('contributions', 'CONTRIBUTIONS / YEAR'),
    ]
    for index, (key, label) in enumerate(metrics):
        x = 24 + index * 220
        value = data.get(key)
        shown = '--' if value is None else value
        parts.append(pixel_text(x, 48, shown, 23, ICE))
        parts.append(pixel_text(x, 76, label, 7.5, MUTED))
        if index:
            parts.append(rect(x - 16, 24, 1, 60, EDGE))
    parts.append(pixel_text(24, 109, f'FEATURED PROJECTS: {len(PROJECTS)} / PROFILE: {USER.upper()}', 8, MUTED))
    parts.append(pixel_text(855, 109, 'UPDATED ' + data.get('synced', 'READY'), 7.5, MUTED, 'text-anchor="end"'))
    write('stats.svg', svg(880, 130, 'Live GitHub profile statistics', ''.join(parts)))


def update_readme_cache_bust(version):
    readme = ROOT / 'README.md'
    source = readme.read_text(encoding='utf-8')
    source = re.sub(r'(assets/[A-Za-z0-9_.-]+\.svg)(?:\?v=[^" )]+)?', rf'\1?v={version}', source)
    readme.write_text(source, encoding='utf-8')


def render(data):
    room(data)
    intro()
    projects_heading()
    stats(data)
    for name, (description, icon) in PROJECTS.items():
        card(name, description, icon, data.get('projects', {}).get(name))
    update_readme_cache_bust(data.get('cache_version', datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')))


def seed_data():
    projects = {
        'Python-PDF-Toolkits': {'name': 'Python-PDF-Toolkits', 'language': 'Python', 'stargazers_count': 24},
        'MISBA7ATY': {'name': 'MISBA7ATY', 'language': 'Python', 'stargazers_count': 8},
        'Media_Converter': {'name': 'Media_Converter', 'language': 'Python', 'stargazers_count': 23},
        'MathsTools': {'name': 'MathsTools', 'language': 'Python', 'stargazers_count': 20},
    }
    return {
        'repos': 12,
        'followers': 17,
        'stars': 75,
        'commits': None,
        'prs': None,
        'contributions': 273,
        'total': None,
        'current': None,
        'best': None,
        'days': {},
        'levels': {},
        'projects': projects,
        'date': '2026-11-26',
        'year': 2026,
        'synced': 'PROFILE SNAPSHOT',
        'cache_version': datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S'),
    }


if __name__ == '__main__':
    import sys
    if '--seed' in sys.argv:
        render(seed_data())
    else:
        live = fetch()
        render(live)
        print(json.dumps({key: live[key] for key in ('repos', 'followers', 'stars', 'commits', 'prs', 'contributions', 'total', 'current', 'best', 'synced')}, indent=2))
