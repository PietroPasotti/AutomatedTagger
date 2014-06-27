# Implementation of X2 - X² Co-occurrence -- based keyword extractor.
# as described in:
# Matsuo & Ishizuka (2004): 
# keyword extraction from a single document using word co-occurrence statistical information 

import re
import time
import math
import nltk

_text = None
_text_tokenized = None # list(list(str()))

punctuation = (';', ':', ',', '.', '!', '?','(',')','[',']','{','}','-','”','“',"'") 
stopwords = []
RESULTS = None

co_occurrences = {}
words_count = {}

def NiceDisplay(tuplelist):
	
	for elem in tuplelist:
		a,b = elem
		
		if (isinstance(a,tuple) or isinstance(a,frozenset) or isinstance(a,list)) and len(a) == 2:
			a1,a2 = a
			a = "	{} {}".format(a1,a2)
		else:
			a = '	'+a
		
		b = str(b)
		
		print(a,' --> ',b)

def HighestNumbers(maxno,dictionary,threshold = None,getvalues = False):
	"""
	Compute and print the highest-valued entries of the dictionary. The dictionary must be of the form "X : int()".
	Set threshold in order to filter out uninterestingly infrequent results. (May be risky with very small _text.)
	"""
	
	if threshold is None:	
		mlist = [(key,dictionary[key]) for key in dictionary] 	# key-value pairs; in the word_count case will be a 'hallo' : 25;
																# in the co_occurr. will be a frozenset('hi','baby') : 130 pair.
	
	else:
		mlist = [(key,dictionary[key]) for key in dictionary if dictionary[key] >= threshold ]
	
	# now we sort the list
	
	sortedresults = []
	
	for i in range(min(maxno,len(mlist))):
		maxvalue = max([ elem[1] for elem in mlist ])
		topitems = [elem for elem in mlist if elem[1] == maxvalue ]
		topitem = topitems[0]
		mlist.remove(topitem)
		sortedresults.append(topitem)
		
		if len(mlist) == 0:
			break
		
	
	
	if getvalues:
		NiceDisplay(sortedresults)
		return sortedresults

def LoadTextFromDefault():
	
	global _text
	with open ("data.txt", "r") as myfile:
		data = myfile.read().replace('\n', '')
		_text = data
		
	print("Loaded default .txt document.")

def IsNumber(word):
	
	try:
		int(word)
		return True
	except ValueError:
		try: 
			float(word)
			return True
		except ValueError:
			return False

def Normalize(word):
	"""Removes punctuation from a word."""
	
	global punctuation
	
	word = list(word.lower()) # we lowercase it!
	
	for letter in word:
		if letter in punctuation:
			word.remove(letter)
	
	word = ''.join(word)
	
	return word		

def CleanUp():
	
	global _text_tokenized
	
	newtxt = []
	
	for sentence in _text_tokenized:
		
		newsentence = []	
		for word in sentence:
			if word in punctuation or len(word) <= 2 or IsNumber(word) or word in stopwords:
				sentence.remove(word)
			else:	
				newsentence.append(word)
		
		if newsentence != []:		
			newtxt.append(newsentence)
			
	_text_tokenized = newtxt

def Split(text = None):
	
	global _text,_text_tokenized,stopwords,punctuation
	
	if text == None:
		noinput = True
		text = _text
	else:
		noinput = False
	
	# we first detect sentences and split the text.
	
	sent_detector = nltk.tokenize.PunktSentenceTokenizer()
	sentences = sent_detector.tokenize(text.strip())
	
	# now a list of strings;
	
	word_detector = nltk.tokenize.PunktWordTokenizer()
	splittext = []
	
	for sent in sentences:
		towords = word_detector.tokenize(sent.strip()) # a list of words
		
		for word in towords:
			towords[towords.index(word)] = Normalize(word)
		
		splittext.append(towords)
	
	_text_tokenized = splittext	
	# CLEANUP
	CleanUp()
	
	if noinput is False:
		return splittext
	else:
		return None
	
def ComputePointwiseMutualInformation_GOOGLE(worda,wordb):
	
	from googlecounter import googleHitCounter
	
	
	hitsAB = googleHitCounter(""" "{} * {}" | "{} * {}" """.format(worda,wordb,wordb,worda))
	hitsA = googleHitCounter(""" "{}" """.format(worda))
	hitsB = googleHitCounter(""" "{}" """.format(wordb))
	
	PMI = math.log(int(hitsAB) / (int(hitsA) * int(hitsB)), 2)
	
	return PMI
	
def EvaluatePairsRelevance(wordsDB,threshold):
	
	if not isinstance(wordsDB,dict):		
		raise BaseException('Bad.')
	
	keys = list(wordsDB.keys()) # now a list of pair -- sets

	for key in keys:
		a = key.pop()
		b = key.pop()
		PMIab = ComputePointwiseMutualInformation(a,b)
		
		if PMIab <= threshold: 	# if the mutual information is too low (threshold) we remove the pair straight away: 
							# even if they co-occur for some reason, they're not relevant to each other and should be ignored
			wordsDB.pop(key)
	
	return wordsDB

def CompileStopWordsDB():
	global stopwords
	
	lines = None
	with open('stopwords.txt','r') as stops:
		lines = stops.readlines()
	
	for line in lines:

		line = line.replace('\n','')
		line = line.replace('\t',' ') # we capture away tabs
		listedline = line.split(' ')
		stopwords.extend(listedline)
		
	stopwords.extend(['',' ','.',',',';',':','-','_',"'",'"','*','···','...'])
	
	if stopwords == []:
		print('Bad: stopwords is empty.')
	
def EvaluateCoOccurrence():
	global stopwords,_text_tokenized,co_occurrences
	
	wordsDB = {} # will be a dictionary pointing from sets to numbers: e.g. frozenset({"analytics","googleplex"}) : 4 meaning they co-occur 4 times.
	
	for sentence in _text_tokenized:
		
		for worda in sentence:
			for wordb in sentence:
				if wordb == worda:
					pass
				else:
					pair = frozenset({worda,wordb})
					if len(pair) == 2:		
						if pair in wordsDB.keys():
							wordsDB[pair] += 1
						else:
							wordsDB[pair] = 1

	#wordsDB = EvaluatePairsRelevance(wordsDB, threshold = <some-threshold-here> )

	co_occurrences = wordsDB
	
	# we run a test:
	
	return None

def WordCount():
	global words_count,stopwords,_text_tokenized
	
	for sentence in _text_tokenized:
		for word in sentence:
			if word in words_count.keys():
				words_count[word] +=1
			else:
				words_count[word] = 1
	
	return None

def Stem_All():
	"""We integrate co_occurrence and words_count results after stemming all words."""
	
	#curAlg = (nltk.stem.WordNetLemmatizer,'WordNet')
	curAlg = (nltk.stem.lancaster.LancasterStemmer,'Lancaster')
	#curAlg = (nltk.stem.PorterStemmer,'Porter')
	
	print('Running stemming algorithm [{}].'.format(curAlg[1]))
	
	global co_occurrences,words_count
	
	# we define the stemmer ###############
	stemmer = curAlg[0]()
	#######################################
	
	newcooccurr = {}
	
	for ori_key in co_occurrences.keys():
		ori_value = co_occurrences[ori_key]
		worda,wordb = ori_key
		
		if isinstance(stemmer,nltk.stem.WordNetLemmatizer):	
			sta = stemmer.lemmatize(worda)
			stb = stemmer.lemmatize(wordb)
		else:	
			sta = stemmer.stem(worda)
			stb = stemmer.stem(wordb)
		
		if sta != stb:
		
			newkey = frozenset({sta,stb})
			
			if newkey in newcooccurr.keys():
				newcooccurr[newkey] += ori_value
			else:
				newcooccurr[newkey] = ori_value
				
	co_occurrences = newcooccurr
			
	newordscount = {}
	
	for ori_word in words_count:
		ori_value = words_count[ori_word]
		
		if isinstance(stemmer,nltk.stem.WordNetLemmatizer):	
			new_word = stemmer.lemmatize(ori_word)		
		else:
			new_word = stemmer.stem(ori_word)
		
		if new_word in newordscount:
			newordscount[new_word] += ori_value
		else:
			newordscount[new_word] = ori_value
			
	words_count = newordscount
	
	print( 'Done.')
	return None

def DetectCompoundTerms():
	
	global _text_tokenized
	
	pairs = {}
	
	for sentence in _text_tokenized:
		
		length = len(sentence)
		prec_word = None
		
		for pointer in range(length -1):
			curword = sentence[pointer]
			if pointer == 0:
				prec_word = sentence[pointer]
				pass
			elif pointer == length:
				pass
			else:
				curword = sentence[pointer]
				pair = (prec_word,curword)
				prec_word = curword
				
				if pair in pairs:
					pairs[pair] +=1
				else:
					pairs[pair] = 1
	
	print('Candidates for compound 2-word terms are: ')
	
	highestpairs = HighestNumbers(10,pairs,threshold = 2)

def ComputeX2prime(termA,termB):
	
	global co_occurrences,words_count
	
	X2 = 0
	
	def frequency(A,B):
		return co_occurrences[frozenset({A,B})]
	
	def expectedFrequency(A,B):
		
		n = lambda word : words_count[word]						#
		T = sum([words_count[word] for word in words_count]) 	# total number of words in the doc/corpus
		p = lambda word : n(word) / T
		result = n(A) * p(B)
		return result
	
	allGs = {}
	
	for g in words_count:
		
		FR = (frequency(termA,termB) - expectedFrequency(termA,termB)) ** 2
		tempchi2 = FR / expectedFrequency(termA,termB)
		
		X2 += tempchi2
		allGs.add(X2)
		
	return X2 - max(allGs)

def ComputeTFIDF(term):
	global _text_tokenized
	
	def TF(term):
		c = 0
		for sentence in _text_tokenized:
			c += sentence.count(term)
		return c
		
	# corpus of comparison is now starfish
	import pickle
	export = pickle.load(open( '/home/pietro/Perceptum/code/starfish/similarity/pickled_export/export_starfish_tjp_12jun.pickle' , 'rb' ))
	data = export['items']
		
	def IDF(term):
		alltexts = {item : data[item].get('text',data[item].get('about')) \
					for item in data if data[item].get('text',data[item].get('about')) not in [None,'',' '] \
					and not isinstance(data[item].get('text',data[item].get('about')) , int) }
		counter = 0
		for text in alltexts:
			A = re.compile(term)
			#print(alltexts[text])
			if A.findall(alltexts[text]):
				counter += 1
		
		if counter == 0:
			return 0
		return math.log((len(alltexts) / counter),2)
	
	return TF(term) * IDF(term)

def TestTFIDF():
	global _text_tokenized
	
	allterms = {term for term in [sentence for sentence in _text_tokenized]}
	
	idfs = {term : ComputeTFIDF(term) for term in allterms}
	
	return idfs
		
def RunFullX2prime():
	
	oriwordcorpus = []

	for sentence in _text_tokenized:
		for word in sentence:
			oriwordcorpus.append(word)
	
	wordcorpus = []
		
	for i in range(len(oriwordcorpus)//3):
		bestone = [word for word in oriwordcorpus if words_count.get(word) == max( [words_count.get(w,0) for w in oriwordcorpus] )]
		bestone = bestone[0]
		oriwordcorpus.remove(bestone)
		wordcorpus.append(bestone)
	
	# we run the analysis only on the 30% of most frequent words
	
	# CLUSTERING
	def P(W,G):
		a = co_occurrences.get(frozenset({W,G}),0)
		b = words_count.get(G,0)
		if b == 0:
			return 0
		return a/b	
		
	clusterlist = []
	
	def J(termA,termB):
		
		smm = 0
		
		def h(x):
			if x <= 0:
				return 0
			else:
				return -x * math.log(x)

		smm = 0
		for i in wordcorpus:
			divergence = h(P(i,termA)+P(i,termB)) - h(P(i,termA) - h(P(i,termB)))
			smm += divergence
		
		val = math.log(2) + 1/2 * smm
		return val
	
	def cluster(A,B):
		for clus in clusterlist: # we search through all existing clusters
			if A in clus:   # if either word is in a cluster
				if B not in clus: 
					clus.append(B)
				return None
			elif B in clus: # we add the other one to the same one and return
				if A not in clus:
					clus.append(A)
				return None
		clusterlist.append([A,B]) # otherwise, we form a new cluster
		return None

	def mutualinfo(terma,termb):
		if words_count.get(terma,0) * words_count.get(termb,0) == 0:
			return 0
		return P(terma,termb) / words_count.get(terma,0) * words_count.get(termb,0)
		
	for terma in wordcorpus:
		for termb in wordcorpus:
			if termb != terma: 
				if mutualinfo(terma,termb) >= math.log(2):
					cluster(terma,termb)
				elif J(terma,termb) >= (0.95 * math.log(2)):
					cluster(terma,termb)
	
	print('Clustering: ' + str(clusterlist))
	return clusterlist
	

		
	


def test():
	
	##### FLAGS #####
	
	nostemming = False
	compounds = False
	compare = True
	
	#################
	
	global _text,stopwords
	start = time.clock()
	print("Running x2 algorythm...")

	if _text is None:
		LoadTextFromDefault()
	
	if stopwords == []:
		CompileStopWordsDB()
	
	
	if isinstance(_text,str):
		print('Tokenizing corpus...')
		Split()
	else:
		print('Corpus is already tokenized; proceed...')
	
	print('Evaluating co-occurrences...')
	EvaluateCoOccurrence()
	print('Counting words...')
	WordCount()
	
	if nostemming:
		print()
		print('--- pre-stemming ---')
		print('Running HighestNumbers(20,words_count)...')
		HighestNumbers(20,words_count)
		print()
		print('Running HighestNumbers(20,co_occurrences)...')
		HighestNumbers(20,co_occurrences)
	else:
		print()
		Stem_All()
		print('Running HighestNumbers(20,words_count)...')
		HighestNumbers(20,words_count)
		print()
		print('Running HighestNumbers(20,co_occurrences)...')
		HighestNumbers(20,co_occurrences)	
	
	if compounds:
		print()
		print('Running compounds detection...')
		DetectCompoundTerms()
	else:
		pass
	
	if compare:
		print()
		print('Comparing tfidf and co-occurrence ranking...')
		
	
	elapsed = (time.clock() - start)
	print('Done.')
	print("[ Runtime -- {} ]".format(elapsed))
	return None
		
# test()

def RunFullAnalysis(text):
	"""Wants an input of type list(list(str()))."""
	
	global _text
	
	_text = text
	
	test()


