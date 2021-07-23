#/bin/python3

import requests
import sys
import re
import concurrent.futures
import time

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
text = t.readlines()

def func(start, end):
	global text
	infos = []
	for ind in range(start, end):
		print(f'{start}/{ind}/{end}, {time.time()}')
		s = text[ind].replace('\n', '').split('-')
		i = s[0] + '-' + '0' * (3 - len(s[1])) + s[1]
		i = i.replace('\n', '')
		r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Search?searchString=' + i)
		while r.status_code == 429:
			print('---Ratelimited---')
			time.sleep(25)
			r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Search?searchString=' + i)
		if 'Sorry, no matches for your query' in r.text or len(s) == 3:
			packname = '__ERROR__'
			cardname = '__ERROR__'
			if s[0] == 'YSD':
				packname = 'Starter-Deck-GX-2006'
			elif s[0] == 'GLD2':
				packname = 'Gold-Series-2'
			elif s[0] == 'DPCT':
				if s[1].endswith('005'):
					packname = 'Duelist-Pack-Collection-Tin-2011'
					cardname = 'Frozen-Fitzgerald'
				else:
					packname = 'Duelist-Pack-Collection-Tin-2010'
			else:
				r = requests.get('http://yugipedia.com/index.php?search=' + i.split('-')[0])
				if 'can refer to ' in r.text:
					n = r.text.split('<li>')[1].split('href="')[1].split('" title')[0]
					r = requests.get('http://yugipedia.com' + n)
				packname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('-', '').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace("'", '').replace('ARC-V', 'ArcV').replace('!', '')
				if packname.endswith('-Structure-Deck'):
					packname = 'Structure-Deck-' + packname.split('-Structure-Deck')[0]
			if cardname == '__ERROR__':
				r = requests.get('http://yugipedia.com/index.php?search=' + i)
				cardname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace(' &amp; ', '-').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace('.', '').replace(',', '')
			version = ''
			if len(s) == 3:
				versions = r.text.split(i)[-1].split('<td>')[3].split('</table>')[0].split('<br />')
				version = re.sub(r'<.+?>', '',versions[int(s[2])-1]).replace(' ', '-')
				version = '-V-' + s[2] + '-' + version
			r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + version)
			while r.status_code == 429:
				print('---Ratelimited---')
				time.sleep(25)
				r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + version)
			if 'Invalid product!' in r.text and len(s) == 3:
				r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + '-V-' + s[2])
				while r.status_code == 429:
					print('---Ratelimited---')
					time.sleep(25)
					r = requests.get('http://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + '-V-' + s[2])
		tmp1 = r.text.split('<h1>')
		tmp2 = r.text.split(' €')
		if len(tmp1) < 2:
			sys.exit(f'-----Got the wrong page: start: {start}, end: {end}, current: {ind}, {i}-----\n{r.text}, {r}')
		if len(tmp2) < 6:
			sys.exit(f'-----Too few prices: start: {start}, end: {end}, current: {ind}, {i}-----\n{r.text}, {r}')
		name = tmp1[1].split('<span')[0]
		parts = tmp2[1:5]
		out = ''
		for f in parts:
			out += f.split('<span>')[1] + '|'
		out = i + '|' + out + name
		infos.append(out)
		time.sleep(10)
	r.close()
	return infos

thread_count = 10
batch_size = int(len(text) / thread_count)
residue = len(text) - (thread_count * batch_size)

complete = []
with concurrent.futures.ThreadPoolExecutor() as executor:
	futures = [executor.submit(func, i * batch_size, (i + 1) * batch_size + int(i / (thread_count - 1)) * residue) for i in range(thread_count)]
	complete = [f.result() for f in futures]

for i in complete:
	print(i)
