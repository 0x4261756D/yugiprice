#/bin/python3

import requests
from html import escape
import sys

if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
	print('''
	Usage: ./getInfos.py <filename>
	<filename>: path to a file containing the ids of yugioh cards (<pack id>-<language><number>).
	The id of a card can be found right hand below the card's picture.
	''')
	exit(1)

t = open(sys.argv[1])

for i in t.readlines():
	s = i.replace('\n', '').split('-')
	i = s[0] + '-' + '0' * (3 - len(s[1])) + s[1]
	print(i, end='|')
	r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Search?searchString=' + i.replace('\n', ''))
	if 'Sorry, no matches for your query' in r.text:
		r.close()
		r = requests.get('http://yugipedia.com/index.php?search=' + i.replace('\n', '').split('-')[0])
		packname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '')
		r.close()
		r = requests.get('http://yugipedia.com/index.php?search=' + i.replace('\n', ''))
		cardname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace('.', '').replace(',', '')
		r.close()
		r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname)
	name = r.text.split('<h1>')[1].split('<span')[0]
	parts = r.text.split(' €')[1:5]
	for f in parts:
		print(f.split('<span>')[1], end='|')
	print(name)
	r.close()
