"""Copy the latest three public editions for a manual Pages compatibility trial."""
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SOURCE = 'https://merry-pixie-6a45bd.netlify.app/f9466af4a6d5302fd2027fd150687f8a1dd513b1f87a0acf/feed.xml'
BASE = 'https://oliverbose.github.io/ai-daily-brief-pages'
OUT = Path('_site')
ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')


def read(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def main():
    if OUT.exists():
        raise RuntimeError('Use a clean build directory')
    root = ET.fromstring(read(SOURCE))
    channel = root.find('channel')
    editions = []
    for item in channel.findall('item'):
        guid = item.findtext('guid', '')
        match = re.fullmatch(r'urn:daily-ai-brief:(\d{4}-\d{2}-\d{2})', guid)
        if match:
            editions.append((match[1], item))
        channel.remove(item)
    editions.sort(key=lambda pair: pair[0], reverse=True)
    editions = editions[:3]
    if len(editions) != 3 or len({day for day, _ in editions}) != 3:
        raise RuntimeError('Expected three distinct published editions')
    (OUT / 'episodes').mkdir(parents=True)
    catalog = []
    for day, item in editions:
        enclosure = item.find('enclosure')
        source = urllib.parse.urlparse(enclosure.get('url'))
        if source.scheme != 'https' or source.hostname != urllib.parse.urlparse(SOURCE).hostname:
            raise RuntimeError('Unexpected enclosure host')
        filename = Path(source.path).name
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-f0-9]+\.mp3', filename):
            raise RuntimeError('Unexpected audio filename')
        audio = read(enclosure.get('url'))
        if len(audio) != int(enclosure.get('length')):
            raise RuntimeError('Enclosure length mismatch')
        relative = 'episodes/' + filename
        path = OUT / relative
        path.write_bytes(audio)
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path), '-f', 'null', '-'], check=True)
        duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(path)], text=True))
        enclosure.set('url', BASE + '/' + relative)
        enclosure.set('type', 'audio/mpeg')
        channel.append(item)
        catalog.append(dict(date=day, guid=item.findtext('guid'), script_hash=None,
                            recipe_hash=None, audio_checksum=hashlib.sha256(audio).hexdigest(),
                            filename=relative, size=len(audio), duration=duration))
    for link in channel.findall('{http://www.w3.org/2005/Atom}link'):
        if link.get('rel') == 'self':
            link.set('href', BASE + '/feed.xml')
    if channel.find('link') is not None:
        channel.find('link').text = BASE + '/'
    ET.ElementTree(root).write(OUT / 'feed.xml', encoding='utf-8', xml_declaration=True)
    (OUT / 'publication.json').write_text(json.dumps({'schema_version': 1, 'episodes': catalog}, indent=2) + '\n')
    players = '\n'.join('<section><h2>' + row['date'] + '</h2><audio controls preload="metadata" src="' + html.escape(row['filename']) + '"></audio></section>' for row in catalog)
    (OUT / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Daily AI Brief — Pages playback trial</title><style>body{font:18px system-ui;max-width:700px;margin:3rem auto;padding:0 1rem}audio{width:100%}section{margin:2rem 0}</style><h1>Daily AI Brief</h1><p>GitHub Pages playback trial. AI-generated narration.</p><p><a href="feed.xml">Podcast RSS feed</a></p>' + players + '</html>')
    (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (OUT / '.nojekyll').touch()
    print('Verified and copied three episodes; no speech generated.')


if __name__ == '__main__':
    main()
