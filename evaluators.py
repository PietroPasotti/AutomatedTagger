
import pickled_export.data as data
import corpusmaking

export = data.readData()

# where we will store all sentences/chunks of text for the engine to search on.
CORPUS = []

# where we store all pairs of tags and associate to them their similarity likelihood ratio. ('LearningAnalytics','AnalyticAbcLearning') : 0.43223467
RATINGS = {}

corpusmaking.makeCorpus()

# the evaluation criteria and their weights
CRITERIA = { 	"chasm" : 0.5, # to catch situations such as weblectures = videocolleges = videolectures = webcolleges
				"appears_in_other_words_glossary" : 0.5,
				"appears_in_other_words_glossary_both" : 0.8
}

def makeRestrictedCorpus(word):
	
	restr_CORPUS = []
	
	global CORPUS
	
	for chunk in CORPUS:
		if word in str(chunk):
			restr_CORPUS.append(str(chunk))
			
	return restr_CORPUS

def tagToGlossaryDict():
	
	tagToGlossaryDict = {}
	
	for tag in export['tags'].keys():
		if export['tags'][tag]['glossary'] is not None:
			
			glosnum = export['tags'][tag]['glossary']
			
			glositem = export['items'][glosnum]
			
			glossary_text = glositem['text']
			
			tagToGlossaryDict[tag] = glossary_text
	
	return tagToGlossaryDict

def wordify(tag):
	
	word = ''
	
	word += tag[0]
	
	tag = tag[1:]
	
	for letter in tag:
		if letter.isupper():
			word += " " + letter
		else:
			word += letter
	
	return word

def inGlossaries(word):
	"""
	1) we make a list of all glossaries
	2) we search each glossary for *word*
		3) if word in glossary: correspondent tag is evaluated positively
		 4) update RATINGS accordingly
	"""
	
	alltags = list(export['tags'].keys())
	
	tagtoglosdict = tagToGlossaryDict()
		
	alltagsminusword = [tag for tag in list(export['tags'].keys()) if tag != word]	
	
	global CRITERIA, RATINGS
	
def isThereAChasm(word):	# e.g. 'weblectures'
	
	alltags = list(export['tags'].keys())
	
	tagswithword = []
	
	for tag in alltags:
		if word in tag:
			tagswithword.append(tag) # we catch 'weblectures-based-teaching'
	
	strippedtags = []
	
	for tag in tagswithword:
		strippedtag = tag.replace(word,'') # we eliminate the word from the tag; e.g. 
		if strippedtag == '' or strippedtag == ' ':
			pass
		else:
			strippedtags.append(strippedtag)
	
	

def evaluate(word,corpus = CORPUS):
	
	# we only consider relevant chunks, namely those which contain the word (for the moment)
	restr_CORPUS = makeRestrictedCorpus(word)
	
	#if isThereAChasm(word):
	#	matching_criteria.append('chasm')
		
	inGlossaries(word) # returns all tags whose glossaries name *word*
	
