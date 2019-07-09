#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, requests, json, zlib, time
from bs4 import BeautifulSoup
from base64 import b64decode, b64encode
from sjcl import SJCL
from ebooklib import epub
from random import randint

def write_epubs(output, title, chapters):
	book = epub.EpubBook()
	book.set_identifier("id%d" % randint(10000,100000))
	book.set_title(title)
	book.set_language("en")
	book.add_author("Trojahn")

	links = []
	for i in range(len(chapters)):
		cpt = epub.EpubHtml(title=chapters[i][0], file_name="chap_%d.xhtml" % (i+1), lang="en")
		text = u"<h1>" + chapters[i][0] + u"</h1>"
		for c in chapters[i][1]:
			text = text + u"<p>" + c + u"</p>"

		cpt.content = text
		book.add_item(cpt)

	toc = []
	for i in range(len(chapters)):
		toc.append(epub.Link("chap_%d.xhtml" % (i+1), chapters[i][0], "c%d" % i))
	book.toc = tuple(toc)

	book.add_item(epub.EpubNcx())
	book.add_item(epub.EpubNav())

	style = 'BODY {color: white;}'
	nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
	book.add_item(nav_css)

	spine = ['nav']
	for cpt in links:
		spine.append(cpt)
	book.spine = spine

	epub.write_epub(output, book, {})

def download_parse(url):
	x = requests.get(url, headers={'X-Requested-With' : 'JSONHttpRequest'}).json()

	# Debug code to avoid blacklist. Ignore it :D
	# with open("out.json",'w') as f:
		# json.dump(x, f)
	# with open("out.json", "r") as json_file:
	# 	x = json.load(json_file)
	data = decode(url[url.find("#")+1:], x)
	soup = BeautifulSoup(data, 'html5lib')
	out = []
	title = soup.find_all("h2")
	for t in title:
		p = []
		for elem in t.next_siblings:
			if elem.name == 'h2':
				break
			if elem.name == 'p':
				p.append(elem.get_text())
			if str(type(elem)) == "<class 'bs4.element.NavigableString'>" :
				if str(type(elem)) == "<class 'bs4.element.NavigableString'>":
					elem = elem.replace("\n\n", "\n")
					elem = elem.split("\n")
					elem = [x for x in elem if x]
					if len(p) > 0:
						p = p + elem
					else:
						p = elem
					
		out.append((t.text, p))
	return out

def decompress(s):
	return zlib.decompress(bytearray(map(lambda c:ord(c)&255, b64decode(s.encode('utf-8')).decode('utf-8'))), -zlib.MAX_WBITS)

def decode(pas, data):
	key = b64encode(b64decode(pas))
	c_text = json.loads(data['data'])

	text = SJCL().decrypt(c_text, key)	
	return decompress(text.decode())

def main(args):
	chs = []
	for url in args[3:]:
		chs = chs + download_parse(url)
		time.sleep(5)
	write_epubs(sys.argv[1], str(sys.argv[2]), chs)

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print("./privtoepub <destination_file> <novel_title> <link1> [link2...]")
		sys.exit(0)
	main(sys.argv)