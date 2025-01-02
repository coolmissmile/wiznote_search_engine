#!encoding:utf-8
from bs4 import BeautifulSoup

# notes/page_41396b67-ee4e-404e-9940-3e053059d98d/index.html

fp = open("notes/page_41396b67-ee4e-404e-9940-3e053059d98d/index.html", "r")
html = fp.read()

soup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')
for i in soup.body:
    print i.get_text()
