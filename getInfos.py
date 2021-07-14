#/bin/python3

import requests
from html import escape
import sys
import re

if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
	print('''
	Usage: ./getInfos.py <filename>
	<filename>: path to a file containing the ids of yugioh cards (<pack id>-<language><number>-<rarity index>).
	The id of a card can be found right hand below the card's picture.
	The rarity index for cards in multiple rarities in the same set is 1-based (hoping there are no discrepancies between yugipedia and cardmarket indexing...)
	''')
	exit(1)

t = open(sys.argv[1])
seen = {}

for line in t.readlines():
	if line in seen:
		print(seen[line])
	else:
		s = line.replace('\n', '').split('-')
		i = s[0] + '-' + '0' * (3 - len(s[1])) + s[1]
		i = i.replace('\n', '')
		print(i, end='|')
		r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Search?searchString=' + i)
		if 'Sorry, no matches for your query' in r.text or len(s) == 3:
			r.close()
			r = requests.get('http://yugipedia.com/index.php?search=' + i.split('-')[0])
			if 'can refer to ' in r.text:
				n = r.text.split('<li>')[1].split('href="')[1].split('" title')[0]
				r.close()
				r = requests.get('http://yugipedia.com' + n)
			packname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace("'", '')
			if packname.endswith('-Structure-Deck'):
				packname = 'Structure-Deck-' + packname.replace('-Structure-Deck', '')
			r.close()
			r = requests.get('http://yugipedia.com/index.php?search=' + i)
			cardname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace('.', '').replace(',', '')
			version = ''
			if len(s) == 3:
				versions = r.text.split(i)[-1].split('<td>')[3].split('<br />')
				version = re.sub(r'<.+?>', '',versions[int(s[2])-1]).replace(' ', '-')
				if version == 'Common':
					version = ''
				else:
					version = '-' + version
				version = '-V-' + s[2] + version
			r.close()
			r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + version)
		name = r.text.split('<h1>')[1].split('<span')[0]
		parts = r.text.split(' €')[1:5]
		out = ''
		for f in parts:
			out += f.split('<span>')[1] + '|'
		print(out, end='')
		out = i + '|' + out + name
		print(name)
		r.close()
		seen[line] = out
