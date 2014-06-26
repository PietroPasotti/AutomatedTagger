# data 

import pickle

def readData():
	
	with open('/home/pietro/Perceptum/code/starfish/similarity/pickled_export/export_starfish_tjp_12jun.pickle','rb') as f:
		data = pickle.load(f)
	
	return data

def getpage(search):
	page = "https://www.google.nl/?gfe_rd=cr&ei=JfinU9m1Aork-gaAhYGgAw&gws_rd=ssl#q={}".format(search)
	
	import urllib.request
	
	urlpage = urllib.request.urlopen(page)
	
	strpage = str(urlpage.read())
	return strpage
