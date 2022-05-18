#/bin/python3

import requests
import sys
import re
import concurrent.futures
import time
import datetime

has_output_file = '-o' in sys.argv or '--output' in sys.argv
should_use_tor = '-t' in sys.argv or '--tor' in sys.argv

if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
	print('''
	Usage: ./getInfos.py <filename> [-o <output filename>] [-t]
	<filename>: path to a file containing the ids of yugioh cards (<pack id>-<language><number>-<rarity index>).
	The id of a card can be found right hand below the card's picture.
	The rarity index for cards in multiple rarities in the same set is 1-based (hoping there are no discrepancies between yugipedia and cardmarket indexing...)
	(optional)
	-o <output filename>: path to a file the data is written to in addition to stdout
	-t: Use tor (needs the pip module requests[socks])
	''')
	exit(1)

session = requests.session()
if should_use_tor:
	session.proxies = {}
	session.proxies['http'] = 'socks5h://localhost:9050'
	session.proxies['https'] = 'socks5h://localhost:9050'

print(session.get("https://httpbin.org/ip").text)

def req(url):
	r = session.get(url)
	start = time.time()
	while r.status_code == 429:
		time.sleep(30)
		print(f'---Ratelimited, has been {int(time.time() - start)} seconds---')
		r = session.get(url)
	return r

t = open(sys.argv[1], 'r')
text = t.readlines()
t.close()
def func(start, end):
	global text
	infos = []
	for ind in range(start, end):
		print(f'{start}/{ind}/{end}, {datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")}')
		s = text[ind].replace('\n', '').split('-')
		i = s[0] + '-' + '0' * (3 - len(s[1])) + s[1]
		i = i.replace('\n', '')
		if len(s) != 3:
			r = req('https://www.cardmarket.com/en/YuGiOh/Products/Search?searchString=' + i)
		if len(s) == 3 or 'Sorry, no matches for your query' in r.text:
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
			elif s[0] == '5DS2':
				packname = 'Starter-Deck-2009'
			else:
				r = req('https://yugipedia.com/index.php?search=' + i.split('-')[0])
				if 'can refer to ' in r.text:
					n = r.text.split('<li>')[1].split('href="')[1].split('" title')[0]
					print(f"Encountered 'can refer to'. {n}")
					r = req('https://yugipedia.com' + n)
				packname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('-', '').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace("'", '').replace('ARC-V', 'ArcV').replace('!', '')
				if packname.endswith('-Structure-Deck'):
					packname = 'Structure-Deck-' + packname.split('-Structure-Deck')[0]
			if cardname == '__ERROR__':
				r = req('https://yugipedia.com/index.php?search=' + i)
				cardname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace(' &amp; ', '-').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace('.', '').replace(',', '')
			version = ''
			if len(s) == 3:
				col = 3
				if re.match(r'\w+-EN\d+', i):
					col -= 1
				versions = r.text.split(i)[-1].split('<td>')[col].split('</table>')[0].split('<br />')
				print(f"Link: {r.url} | {i} | Multiple versions, selecting {s[2]}: {versions}")
				print(f"Link: {r.url} | {i} | {versions[int(s[2])-1]}")
				version = re.sub(r'<.+?>', '', versions[int(s[2])-1]).replace(' ', '-')
				version = '-V-' + s[2] + '-' + version
				print(f"Selected: {version}")
			r = req('https://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + version)
			if 'Invalid product!' in r.text and len(s) == 3:
				r = req('https://www.cardmarket.com/en/YuGiOh/Products/Singles/' + packname + '/' + cardname + '-V-' + s[2])
		tmp1 = r.text.split('<h1>')
		tmp2 = r.text.split(' €')
		out = ''
		parts = tmp2[1:5]
		if '£' in tmp2[0]:
			out = r.text.split('col-offer')[1].split(' €')[0].split('text-nowrap">')[-1] + '|'
			parts = tmp2[1:4]
		if len(tmp2) < 6:
			print(f'-----Too few prices: start: {start}, end: {end}, current: {ind}, {i}-----\n{r.text}, {r}')
			sys.exit(1)
		for f in parts:
			out += f.split('<span>')[1] + '|'
			
		if len(tmp1) < 2:
			print(f'-----Got the wrong page: start: {start}, end: {end}, current: {ind}, {i}-----\n{r.text}, {r}')
			sys.exit(1)
		name = tmp1[1].split('<span')[0]
		out = i + '|' + out + name
		infos.append(out)
		time.sleep(10)
	r.close()
	return infos

fallback_number = 2
thread_count = 10
if thread_count > len(text):
	thread_count = int(len(text) / fallback_number)
batch_size = int(len(text) / thread_count)
residue = len(text) - (thread_count * batch_size)

complete = []
with concurrent.futures.ThreadPoolExecutor() as executor:
	futures = [executor.submit(func, i * batch_size, (i + 1) * batch_size + int(i / (thread_count - 1)) * residue) for i in range(thread_count)]
	complete = [f.result() for f in futures]

if has_output_file:
	if '-o' in sys.argv:
		t = open(sys.argv[sys.argv.index('-o') + 1], 'w')
	else:
		t = open(sys.argv[sys.argv.index('--output') + 1], 'w')

print('All pools completed')

for i in complete:
	for j in i:
		print(j)
		if has_output_file:
			t.write(j + '\n')

if not t.closed:
	t.close()
