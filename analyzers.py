#analyzers.py

from main import _export,test,x2,RESULTS,evaluation


def overlap(dic1,dic2):
	summ = len(set(dic1).union(set(dic2))) 	# if it's a dic, here we take the mere keys()
											# if it's a list, we take all
	overlapOfPlaindics = len(set(dic1)) + len(set(dic2)) - summ
	return overlapOfPlaindics

def unpackKWS_CO(COres):
	kws = []
	for CO in COres:
		CO1,CO2 = CO
		kws.extend([CO1,CO2])		
	return kws

def matcher(item1,item2):
	
	val = 0
	
	COres1,FRres1 = RESULTS[item1]
	COres2,FRres2 = RESULTS[item2]

	overlapCORES = overlap(COres1, COres2)
			
	kws1 = unpackKWS_CO(COres1)
	kws2 = unpackKWS_CO(COres2)
	
	overlapKWS_fromCO = overlap(kws1,kws2) 		# overlapping co_occurrence-extracted words
	overlapKWS_fromFR = overlap(FRres1,FRres2) 	# overlapping words extracted by frequency
	
	weight = 1.65 # ?
	
	weightedoverlapKWS = weight*overlapKWS_fromCO + overlapKWS_fromFR
	
	return weightedoverlapKWS

def analyze(RESULTS,verbose):
	
	for item in _export['items']:
		test(item,verbose)
				
		top_co_occurr = x2.HighestNumbers(5, x2.co_occurrences ,getvalues = True)
		top_freq = x2.HighestNumbers(5, x2.words_count ,getvalues = True)
		
		RESULTS[item] = (top_co_occurr,top_freq)
	
	for elem in _export['items']:
		for otherelem in _export['items']:
			if elem != otherelem and frozenset({elem,otherelem}) not in evaluation:
				evaluation[frozenset({elem,otherelem})] = 'n/a.'
	
	for pair in evaluation:
		A,B = pair
		evaluation[pair] = matcher(A,B)
		
	return evaluation

