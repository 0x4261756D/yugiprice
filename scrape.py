#/bin/python3

import requests
import sys
import re
import concurrent.futures
import time
import datetime

start_time = time.time()

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
	was_ratelimited = False
	while r.status_code == 429:
		was_ratelimited = True
		time.sleep(int(r.headers.get("Retry-After")) + .1)
		print(f'---Ratelimited, has been {int(time.time() - start)} seconds---')
		r = session.get(url)
	if was_ratelimited:
		print(f'---Ratelimit over after {int(time.time() - start)} seconds---')
	return r

t = open(sys.argv[1], 'r')
text = t.readlines()
t.close()

# legacy, deprecated in favor of automatic load managing by python directly
def func(start, end):
	global text
	infos = []
	for ind in range(start, end):
		print(f'{start}/{ind}/{end}, {datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")}')
		infos.append(process_single_card(text[ind]))
	r.close()
	return infos
	
def process_single_card(t):
	s = t.replace('\n', '').split('-')
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
				n = r.text.split('<li>')[1].split('href="')[1].split('"')[0]
				print(f"Encountered 'can refer to'. {n}")
				r = req('https://yugipedia.com' + n)
			if "MobileMenu" in r.text:
				print(f"handling mobile site for {n}")
				packname = r.text.split('</h1>')[1].split('<h1 id="section_0">')[1].replace('-', '').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace("'", '').replace('ARC-V', 'ArcV').replace('!', '')
			else:
				packname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace('-', '').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace("'", '').replace('ARC-V', 'ArcV').replace('!', '')
			if packname.endswith('-Structure-Deck'):
				packname = 'Structure-Deck-' + packname.split('-Structure-Deck')[0]
		if cardname == '__ERROR__':
			r = req('https://yugipedia.com/index.php?search=' + i)
			cardname = r.text.split('</h1>')[0].split('<h1 id="firstHeading" class="firstHeading" lang="en">')[1].replace(' &amp; ', '-').replace('<i>', '').replace('</i>', '').replace(' ', '-').replace(':', '').replace('.', '').replace(',', '')
		version = ''
		if len(s) == 3:
			if s[0] == "LDS3":
				version = "-V" + s[2] + "-Ultra-Rare"
			else:
				col = 3
				if re.match(r'\w+-EN\d+', i):
					col -= 1
				versions = r.text.split(i)[-1].split('<td>')[col].split('</table>')[0].split('<br />')
				print(f"Link: {r.url} | card: {s} | {i} | Multiple versions: {versions}")
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
		print(f'-----Too few prices: {t}, {i}-----\n{r.text}, {r}')
		sys.exit(1)
	for f in parts:
		out += f.split('<span>')[1] + '|'
		
	if len(tmp1) < 2:
		print(f'-----Got the wrong page: {t}, {tmp1}, {i}-----\n{r.text}, {r}')
		sys.exit(1)
	name = tmp1[1].split('<span')[0]
	out = i + '|' + out + name
	r.close()
	return out

complete = []
with concurrent.futures.ProcessPoolExecutor() as executor:
	for result in executor.map(process_single_card, text):
		print(result)
		complete.append(result)

if has_output_file:
	if '-o' in sys.argv:
		t = open(sys.argv[sys.argv.index('-o') + 1], 'w')
	else:
		t = open(sys.argv[sys.argv.index('--output') + 1], 'w')

print('All pools completed')

print(f"Start time: {start_time}, End time: {time.time()}")

for i in complete:
	print(i)
	if has_output_file:
		t.write(j + '\n')

if not t.closed:
	t.close()
