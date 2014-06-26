
from bs4 import BeautifulSoup,SoupStrainer
from evaluators import wordify as Wordify
import httplib2
import math
import sys
import itertools
import x2
import re

_export = None

_corpus = [] # type list(list(list(list( ))) 		· that is: corpus, texts, sentences, words

_links = [] # type int():float()					· links to other items, mapped to their weights

_keywords = [] # type list(str())  					· the vocabulary surrounding the concept, ordered by relevance

_known_datatypes = ['Person','Good Practice','Project','Question','Answer','Information','Glossary']

_urls = []	#										· temporary list of urls for the algorythm

_relevance_hierarchy = {
'Person' : 				('headline','name','about','links','tags'),
'Good Practice' : 		('text','title','author','links','tags'),
'Project' : 			('title','text','author','links','tags'),
'Information' : 		('title','text','links','tags','author'),
'Question' : 			('text','title','tags','links','author'),
'Answer'  : 			('text','title','author','links','tags'),
'Glossary'	:			('text','title','tags','links','author') 
 }

lower_significance_bound = 2000

__satisfied = False # Flag that goes true when the algorythm settles on a state.

def ReDodge(name,threshold = 10):
	"""Generates a RE that will match the given name tolerating an error of threshold/100."""
		
	finalREname = ''
	
	allperms = itertools.permutations(name)
	
	
	allperms_ERRORS = []
	
	for permname in allperms: # e.g. ['Pietro','Pasotti','Molen','Der','Van']
		dodgedname = r' '.join(permname)  # = "Pietro Pasotti Molen Der Wan"
		
		errlist = []
		for index in range(len(dodgedname)-1):
			errname = list(dodgedname)
			
			if errname[index] != ' ': # We do nothing when the cursor reaches a space
				errname[index] = r'\w'
				
				finame = ''.join(errname).strip()
			
			# This will generate:
			# r'\wietro Pas...'
			# r'P\wietro Pas...'
			# ...
			# r'Pietro \was...'
			
				finame =  finame.replace(r' ',r'[\b\s\b]?')
				
				finam = r'\b' + finame + r'\b'
			
			# Now \r'\wietro\sPasotti\sMol...'
			
				errlist.append(finame)
		
		# errlist is now the list of all 1-tolerant versions of permname		
		
		dodgedperm = r'|'.join(errlist) # we OR all alternatives
		
		allperms_ERRORS.append(dodgedperm)
		
	# now allperms_ERRORS is a list of 1-tolerant versions of all the permutations given. if name is Al Jon:
	# allperm_ERRORS = ['\wl\sJon|A\w\sJon|Al\s\won|...',[\won\sAl|J\wn\sAl...]]
	
	finalREname = r'|'.join(allperms_ERRORS)

	return re.compile(finalREname)

def LoadExport():
	try:
		import pickle
		global _export
		doc = open( '/home/pietro/Perceptum/code/starfish/similarity/pickled_export/export_starfish_tjp_12jun.pickle' , 'rb' )
		export = pickle.load(doc)
		_export = export
		doc.close()
		return True
	except BaseException:
		return False
	
def CleanOfHtml(text):
	
	global _urls
	
	print('Cleaning...')
	soup = BeautifulSoup(text)
	puretxt = soup.get_text()
	
	#################### --------- We retrieve maybe-useful urls --------- #
	
	allinks = soup.find_all('a') # if there is HTML in the text...
	for link in allinks:
		link = link.get('href')
		if link is not None:
			_urls.append(link)
			
	# if the links are in the plain text:
	
	pattern = re.compile(r'http://\S+')
	otherurls = pattern.findall(puretxt)
	
	puretxt = pattern.sub('',puretxt) # we remove the urls from the text!
	
	for url in otherurls:
		otherurl = url.strip('.,')
		_urls.append(otherurl)
		
	_urls = list(set(_urls)) 	# 	Remove duplicates (TODO : repetition is an index of relevance also for websites, 
								#	but a link often appears twice in any case, due to the href structure)
	
	return puretxt
			
def Corpus_FeedWithText(item):
	
	global lower_significance_bound,satisfied,_corpus
	
	if isinstance(item,str):
		text = item
	else:
		text = item['text']
	
	if len(text) < lower_significance_bound:
		__satisfied = False
	else:
		__satisfied = True
	
	text = CleanOfHtml(text)
	
	#text = x2.Split(text)
	
	_corpus.append(text)

def Corpus_FeedWithHeadline(item):
	
	global _corpus
	
	txt = item['headline']
	txt = CleanOfHtml(txt)
	_corpus.append(txt)
	
	pass

def Corpus_FeedWithName(item):
	
	global _text,_export,_links

	allpeople = [_export['items'][itemno]['name'] for itemno in _export['items'] if _export['items'][itemno]['type'] == 'Person']
	
	name = item['name']
	
	errormargin = 10 # percentage of name which can be wrong to still suggest a match
	
	if ' ' not in list(name):
		
		def isthereacapital(name):
			for i in range(len(name)-1):
				if name[i].isupper():
					return True
				else:
					pass
			return False	
		
		if isthereacapital(name):
			name = Wordify(name)
			
			for elem in name: # strip all spaces
				elem = elem.strip()
				namelist[namelist.index(elem)] = elem
		else:
			
			name = [name] # we try to take it as a single entity
	else:
		name = name.split(' ')

	# name is now a list of parts of the full name; e.g. ['Pietro','Pasotti']
	
	if len(name) <= 2:
		name = ReDodge(name) # returns a compiled re object which matches name with error tolerance 1; also matches a tag with the full name
	
	else:
		name = re.compile(r'{}'.format(name))
	
	print('Searching match for: ',name.pattern)	
	
	matchingpeopleL = name.findall(','.join(allpeople))
	
	matchingpeople = list(set(matchingpeopleL)) # remove duplicates; but there shouldn't be!
	
	if len(matchingpeopleL) != len(matchingpeople):
		print('[Warning:] duplicates were found in names.')
	
	if len(matchingpeople) == 1:
		match = matchingpeople.pop() # a string: 'Pietro Pasotti'
		sys.stdout.write('Matching name found: {}'.format(match))

		person_l = [ value for value in _export['items'].keys() if _export['items'][value].get('name') == match ]
		person_link = person_l[0] # link for 'Pietro Pasotti' - Person item there
		
		sys.stdout.write('Existing link [{}] detected for Person "{}".'.format(person_link,_export['items'][person_link]['name']))
		
		_links.append(person_link)
		
		return True		
		
	elif len(matchingpeople) == 0:
		print('No matching name found in database.')
		return None
	else:
		print('No single match found with name; suggestions are: {}'.format(matchingpeople))
		return False
	
def Corpus_FeedWithLinks(item):

	pass
	
def Corpus_FeedWithTags(item):
	
	pass

def Corpus_FeedWithAuthor(item):

	pass
	
	

def GatherCorpus(itemno):
	"""Receives as input the number of an unpickled item as exported from Starfish."""
	
	global _relevance_hierarchy,_export,_corpus,pickle
	
	sys.stdout.write('Gathering corpus around item [{}]...'.format(itemno))
	sys.stdout.write('      [ Done. ]\n')
	
	if _export is None:
		sys.stdout.write('Populating _export database...')
		LoadExport()
		sys.stdout.write('      [ Done. ]\n')
	
	if itemno not in _export['items']: # LOCK
		print('>>>   No item corresponding to search, sorry.   <<<')
		return None
	
	else:
		item = _export['items'][itemno]
		
	relevanceHierarchy = _relevance_hierarchy[ item['type'] ]
	
	for content in relevanceHierarchy:
		
		if content == 'headline' and item.get('headline',None) is not None:
			Corpus_FeedWithHeadline(item)
		elif content == 'name' and item.get('name',None) is not None:
			Corpus_FeedWithName(item)
		elif content == 'about' and item.get('about',None) is not None:
			Corpus_FeedWithText(item['about']) # about and text point to same datatype
		elif content == 'tags' and item.get('tags',None) is not None:
			Corpus_FeedWithTags(item)
		elif content == 'links' and item.get('links',None) is not None:
			Corpus_FeedWithLinks(item)
		elif content == 'author' and item.get('author',None) is not None:
			Corpus_FeedWithAuthor(item)
		elif content == 'text' and item.get('text',None) is not None:
			Corpus_FeedWithText(item)
		else:
			print("Lost item info: '{}'".format(str(content)))
		
def ParseCorpus():
	"""Function that, given a nonempty corpus and a __satisfied True condition, populates the _links and _keywords lists."""
	
	global _corpus
	
	for text in _corpus:
		
		x2.RunFullAnalysis(text)

def test(itemno):
	
	global _corpus,_urls,_links,_export

	if _export is None:
		sys.stdout.write('Populating _export database...')
		LoadExport()
		sys.stdout.write('      [ Done. ]\n')	
	
	if itemno not in _export['items']:
		print('ERROR : Not a valid item number! Try with {}.'.format([itemN for itemN in list(_export['items'].keys()) if -4 < (itemN - itemno) < 4 ]))
		return None
		
	GatherCorpus(itemno)
	print('    ***Corpus:', _corpus,'\n','    ***Urls:',_urls, '    ***Links:',_links)
	
	print()
	print("*** [Launching x2 algorithm...] ***")
	print()
	
	ParseCorpus()
	
	print("[ Done. ]")
	
#test(1)
