AutomatedTagger
===============

Mines data from various sources to extract weighted-by-relevance data.

Core of the program is main.py, where a quick test can be made (for some number n [1-240], at this moment) by running:

	>>> import main
	>>> main.test(n)

The algorithm(s) for correlation (induction of relevance information, mainly through co-occurrence), are currently stored only in x2.py.
Other documents are currently of very little use, and will be removed in near future.

A test can be run also on x2 alone, by running:

	>>> import x2
	>>> x2.test()

In this case the results are more evident, because the corpus is bigger and the algorithm outcomes get more precise.
In future, when main's GatherCorpus will do its job in a proper way, this will be not so.
