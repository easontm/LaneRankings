from bs4 import BeautifulSoup
import urllib
r = urllib.urlopen('http://champion.gg/statistics/#?sortBy=general.winPercent&order=descend&roleSort=Jungle').read()
soup = BeautifulSoup(r)
print soup.prettify()[0:1000]
