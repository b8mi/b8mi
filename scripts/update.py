import os, json, random, textwrap, time
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER = os.environ.get('PROFILE_USER', 'b8mi')
PROJECTS = {
    'Python-PDF-Toolkits': ('Five offline PDF utilities for merging, cropping, compression and conversion.', 'pdf'),
    'MISBA7ATY': ('مسبحة إلكترونية | A lightweight Arabic dhikr counter with progress tracking.', 'beads'),
    'Media_Converter': ('Offline audio and video conversion using Python and FFmpeg.', 'media'),
    'MathsTools': ('Interactive graphing, geometry, matrices and other mathematics tools.', 'math'),
}
PANEL = '#101f32'
EDGE = '#254660'
ICE = '#9ce8ff'
BLUE = '#44b9ed'
MUTED = '#9aafc5'
WHITE = '#e2f4ff'


def rect(x, y, w, h, c, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'


def text(x, y, s, size=14, c=WHITE, extra=''):
    return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{c}" {extra}>{escape(str(s))}</text>'


def svg(w, h, label, body, css=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label={quoteattr(label)}><style>{css}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>\n'


def write(name, content):
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(content, encoding='utf-8')


def api(path, payload=None):
    token = os.environ.get('GH_TOKEN')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'b8mi-profile-updater'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        headers['X-GitHub-Api-Version'] = '2022-11-28'
    elif payload is not None:
        raise RuntimeError('GH_TOKEN is required for contribution history.')
    if payload is not None:
        headers['Content-Type'] = 'application/json'
    req = Request('https://api.github.com' + path, headers=headers, data=json.dumps(payload).encode() if payload is not None else None)
    for attempt in range(4):
        try:
            with urlopen(req, timeout=40) as res:
                return json.load(res)
        except HTTPError as exc:
            if exc.code not in (403, 429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'GitHub API {path}: HTTP {exc.code}.') from exc
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)


def streaks(days, today):
    best = run = 0
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


def fetch():
    profile = api('/users/' + USER)
    repos = []
    for page in range(1, 101):
        batch = api(f'/users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=364)
    query = """query($login:String!, $from:DateTime!, $to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){totalCommitContributions totalPullRequestContributions contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    data = api('/graphql', {'query': query, 'variables': {'login': USER, 'from': start.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(), 'to': now.isoformat()}})
    if data.get('errors'):
        raise RuntimeError(str(data['errors']))
    cc = data['data']['user']['contributionsCollection']
    calendar = cc['contributionCalendar']
    days = {d['date']: d['contributionCount'] for w in calendar['weeks'] for d in w['contributionDays']}
    current, best = streaks(days, now.date())
    by_name = {r['name']: r for r in repos}
    return {
        'name': profile.get('name') or USER,
        'followers': profile.get('followers', 0),
        'repos': profile.get('public_repos', 0),
        'stars': sum(r.get('stargazers_count', 0) for r in repos),
        'commits': cc['totalCommitContributions'],
        'prs': cc['totalPullRequestContributions'],
        'total': calendar['totalContributions'],
        'best': best,
        'current': current,
        'days': days,
        'projects': by_name,
        'date': now.date().isoformat(),
    }


def room(data):
    rng = random.Random(91)
    a = [rect(0, 0, 220, 112, '#0a1423'), rect(0, 0, 220, 69, '#12263b'), rect(0, 90, 220, 22, '#0a1826')]
    for x in range(0, 220, 11):
        a.append(rect(x, 0, 1, 90, '#192f45'))
    a += [rect(5, 6, 210, 60, '#06101e'), rect(8, 9, 204, 54, '#0b203d')]
    a.append('<g clip-path="url(#window)">')
    for _ in range(75):
        a.append(rect(rng.randrange(9, 212), rng.randrange(10, 42), 1, 1, rng.choice(['#49718d', '#91d2ef', '#254460'])))
    a += [
        rect(170, 14, 6, 1, '#a7e5f5'),
        rect(169, 15, 8, 1, '#a7e5f5'),
        rect(168, 16, 10, 1, '#a7e5f5'),
        rect(167, 17, 10, 4, '#a7e5f5'),
        rect(168, 21, 10, 1, '#a7e5f5'),
        rect(169, 22, 8, 1, '#a7e5f5'),
        rect(170, 23, 6, 1, '#a7e5f5'),
        rect(171, 15, 5, 1, '#0b203d'),
        rect(171, 16, 6, 1, '#0b203d'),
        rect(172, 17, 5, 4, '#0b203d'),
        rect(171, 21, 6, 1, '#0b203d'),
        rect(171, 22, 5, 1, '#0b203d'),
    ]
    for x in range(8, 212, 9):
        h = rng.randrange(8, 30)
        a.append(rect(x, 61 - h, 8, h, '#132c47'))
        for yy in range(63 - h, 59, 4):
            for xx in (x + 1, x + 5):
                if rng.random() < 0.55:
                    klass = f'tw{rng.randrange(6)}'
                    delay = rng.randrange(0, 24) / 3
                    dur = 4.5 + rng.randrange(0, 20) / 10
                    a.append(rect(xx, yy, 1, 2, rng.choice(['#3e9ec8', '#7de2ff', '#254d6d']), f'class="{klass}" style="animation-delay:-{delay}s;animation-duration:{dur}s"'))
    a += [rect(8, 61, 204, 2, '#236080'), '</g>', rect(109, 9, 2, 54, '#142c43'), rect(5, 64, 210, 3, '#3b5970')]
    for y in range(94, 112, 6):
        a.append(rect(0, y, 220, 1, '#192c40'))

    a += [rect(19, 79, 182, 4, '#35516a'), rect(19, 83, 182, 2, '#183146'), rect(24, 85, 4, 16, '#243c51'), rect(193, 85, 4, 16, '#243c51'), rect(40, 45, 72, 31, '#385871'), rect(42, 47, 68, 27, '#06121f'), rect(72, 76, 8, 3, '#385871'), rect(65, 78, 22, 1, '#56788c')]
    a.append(text(45, 52, '> b8mi / terminal', 3.1, ICE))
    lines = ['> public repositories', '> stars received', '> contributions / 365d']
    vals = [data.get('repos'), data.get('stars'), data.get('total')]
    for i, (label, val) in enumerate(zip(lines, vals)):
        a.append(text(45, 58 + i * 5, label, 2.7, MUTED))
        a.append(text(107, 58 + i * 5, '--' if val is None else val, 3, ICE, 'text-anchor="end"'))
    a.append(rect(45, 70, 3, 1, ICE, 'class="blink"'))
    a += [rect(38, 80, 65, 1, '#7590a4'), rect(116, 77, 7, 2, '#5d7c95'), rect(129, 47, 66, 32, '#51738b'), rect(131, 49, 62, 28, '#123c58'), rect(131, 74, 62, 3, '#24465c')]
    for x in (136, 141, 184, 189):
        for j in range(5):
            a.append(rect(x + (j % 2), 74 - j * 2, 1, 3, '#297a84'))
    a.append('<g clip-path="url(#tank)">')
    for i, (x, y, c) in enumerate([(142, 58, '#7feaff'), (166, 66, '#f4bd79'), (178, 55, '#82a9f5')]):
        a.append(f'<g class="fish" style="animation-delay:-{i * 2}s">')
        a += [rect(x, y, 6, 3, c), rect(x + 6, y - 1, 3, 5, c), rect(x + 1, y + 1, 1, 1, '#0b203d'), '</g>']
    for i in range(7):
        a.append(rect(137 + i * 8, 70 - (i * 3) % 16, 1, 1, '#9fe7f4', f'class="bubble" style="animation-delay:-{i * .6}s"'))
    a += ['</g>', rect(131, 49, 62, 1, '#78c6e2'), rect(131, 49, 1, 28, '#78c6e2'), rect(129, 77, 66, 2, '#5c8095')]
    a += [rect(7, 91, 206, 15, '#081321'), text(12, 101, '3ZMI  /  AFTER HOURS', 5, ICE, 'font-weight="bold"'), text(208, 101, 'CODE  //  CREATE', 3.5, MUTED, 'text-anchor="end"')]
    defs = '<defs><clipPath id="window"><rect x="8" y="9" width="204" height="54"/></clipPath><clipPath id="tank"><rect x="132" y="50" width="60" height="24"/></clipPath></defs>'
    css = '.blink{animation:cursor 1s steps(1) infinite}.fish{animation:fish 8s ease-in-out infinite alternate}.bubble{animation:bubble 4s linear infinite}.tw0{animation:f0 5.0s steps(1) infinite}.tw1{animation:f1 5.7s steps(1) infinite}.tw2{animation:f2 6.1s steps(1) infinite}.tw3{animation:f3 6.8s steps(1) infinite}.tw4{animation:f4 5.4s steps(1) infinite}.tw5{animation:f5 7.2s steps(1) infinite}@keyframes cursor{50%{opacity:0}}@keyframes f0{0%,84%,100%{opacity:1}85%,88%{opacity:.20}}@keyframes f1{0%,12%,100%{opacity:1}13%,16%{opacity:.22}}@keyframes f2{0%,37%,100%{opacity:1}38%,41%{opacity:.26}}@keyframes f3{0%,58%,100%{opacity:1}59%,62%{opacity:.22}}@keyframes f4{0%,72%,100%{opacity:1}73%,76%{opacity:.24}}@keyframes f5{0%,92%,100%{opacity:1}93%,96%{opacity:.18}}@keyframes fish{from{transform:translateX(-5px)}to{transform:translateX(8px)}}@keyframes bubble{to{transform:translateY(-20px);opacity:0}}'
    write('room.svg', svg(880, 448, '3zmi midnight pixel workstation and aquarium', defs + '<g transform="scale(4)" shape-rendering="crispEdges">' + ''.join(a) + '</g>', css))


ICONS = {
    'pdf': ['001111100', '001222100', '001222110', '001222221', '001212221', '001222221', '001211121', '001222221', '001111111'],
    'beads': ['000111000', '001000100', '010000010', '100000001', '100000001', '100000001', '010000010', '001010100', '000111000'],
    'media': ['111111111', '122222221', '120222221', '120022221', '120002221', '120022221', '120222221', '122222221', '111111111'],
    'math': ['100000001', '100000010', '100000100', '100001000', '111111111', '100100000', '101000000', '110000000', '111111111'],
}


def card(name, description, icon, repo):
    a = [rect(.5, .5, 429, 167, PANEL, f'rx="10" stroke="{EDGE}"'), rect(14, 19, 98, 104, '#0b2b45', 'rx="6"'), rect(15, 20, 96, 102, 'none', 'rx="6" stroke="#275472"')]
    icon_x0 = 26 if icon == 'pdf' else 27
    a.append('<g class="float" shape-rendering="crispEdges">')
    for y, row in enumerate(ICONS[icon]):
        for x, v in enumerate(row):
            if v != '0':
                a.append(rect(icon_x0 + x * 8, 35 + y * 8, 8, 8, BLUE if v == '1' else '#205676'))
    a.append('</g>')
    a.append(text(128, 37, name, 16, WHITE, 'font-weight="bold"'))
    description = description.split('|')[-1].strip() if icon == 'beads' else description
    for i, line in enumerate(textwrap.wrap(description, width=33)[:4]):
        a.append(text(128, 60 + i * 17, line, 12, MUTED))
    stars = repo.get('stargazers_count') if repo else None
    language = (repo.get('language') or 'Unknown') if repo is not None else 'Python'
    a.append(text(18, 148, language.upper()[:20], 11, ICE))
    a.append(text(412, 148, 'Stars: ' + ('—' if stars is None else str(stars)), 12, ICE, 'text-anchor="end"'))
    write(name + '.svg', svg(430, 168, name + ' — ' + description, ''.join(a), '.float{animation:float 3.6s ease-in-out infinite}@keyframes float{50%{transform:translateY(-4px)}}'))


def stats(data):
    a = [rect(.5, .5, 879, 129, PANEL, f'rx="10" stroke="{EDGE}"')]
    for i, (key, label) in enumerate([('commits', 'COMMITS / 365D'), ('prs', 'PRs / 365D'), ('stars', 'PUBLIC REPO STARS'), ('best', 'BEST STREAK / 365D')]):
        x = 24 + i * 220
        v = data.get(key)
        a += [text(x, 48, '—' if v is None else v, 32, ICE, 'font-weight="bold"'), text(x, 76, label, 11, MUTED)]
        if i:
            a.append(rect(x - 16, 24, 1, 60, EDGE))
    a.append(text(24, 109, 'Public repositories: ' + str(data.get('repos', '—')) + '   /   Followers: ' + str(data.get('followers', '—')), 12, MUTED))
    a.append(text(855, 109, 'UTC ' + data.get('date', 'awaiting first sync'), 11, MUTED, 'text-anchor="end"'))
    write('stats.svg', svg(880, 130, 'GitHub activity statistics', ''.join(a)))


def activity(data):
    a = [rect(.5, .5, 879, 200, PANEL, f'rx="10" stroke="{EDGE}"'), text(24, 28, '> ACTIVITY / LAST 365 DAYS', 15, ICE, 'font-weight="bold"')]
    if not data.get('days'):
        a.append(text(24, 98, 'Open Actions and run the workflow once to load live contribution history.', 14, MUTED))
    else:
        end = date.fromisoformat(data['date'])
        first = end - timedelta(days=364)
        start = first - timedelta(days=(first.weekday() + 1) % 7)
        palette = ['#152b40', '#1d4768', '#256a93', '#319dc7', '#7de7ff']
        for week in range(53):
            for d in range(7):
                day = start + timedelta(days=week * 7 + d)
                key = day.isoformat()
                if key not in data['days']:
                    continue
                n = data['days'][key]
                level = 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 10 else 4
                a.append(rect(24 + week * 16, 43 + d * 16, 12, 12, palette[level], 'rx="2"'))
        a.append(text(24, 178, str(data['total']) + ' contributions', 14, ICE))
        a.append(text(24, 194, 'Current streak: ' + str(data['current']) + 'd   /   Best: ' + str(data['best']) + 'd', 11, MUTED))
        a.append(text(855, 178, 'UTC ' + data['date'], 12, MUTED, 'text-anchor="end"'))
    write('activity.svg', svg(880, 201, 'GitHub contribution calendar', ''.join(a)))


def render(data):
    room(data)
    stats(data)
    activity(data)
    for name, (desc, icon) in PROJECTS.items():
        card(name, desc, icon, data.get('projects', {}).get(name))


if __name__ == '__main__':
    import sys
    if '--placeholder' in sys.argv:
        render({})
    else:
        render(fetch())
