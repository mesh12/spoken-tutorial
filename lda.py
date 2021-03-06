import os
from preprocess import clean
from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
# from sklearn.datasets import fetch_20newsgroups

paths = []


def clean_mac(files):
	if '.DS_Store' in files:
		files.remove('.DS_Store')


def populate_paths():
	root = os.path.join(os.getcwd(), 'scripts', 'clean')
	courses = os.listdir(root)
	clean_mac(courses)
	for course in courses:
		paths.append(os.path.join(root, course))


def populate_courses(path):
	files = os.listdir(path)
	clean_mac(files)
	data = []
	for file in files:
		p = os.path.join(path, file)
		with open(p, 'r') as f:
			data.append(f.read())
	return data


def create_dataset():
	populate_paths()
	# libreoffice = []
	c = []
	bash = []
	cpp = []
	courses = [c, bash, cpp]
	for i in range(len(paths)):
		path = paths[i]
		data = populate_courses(path)
		courses[i] = data
	data = []
	for course in courses[:1]:
		data += course
	return data

# =============================================================================================


def lda(data_samples):
	n_samples = 2000
	n_features = 1000
	n_topics = 3
	n_top_words = 20


	def get_top_words(model, feature_names, n_top_words):
		top_words = []
		for topic_idx, topic in enumerate(model.components_):
			top_words.append((topic_idx, " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])))
		return top_words

	# Load the 20 newsgroups dataset and vectorize it. We use a few heuristics
	# to filter out useless terms early on: the posts are stripped of headers,
	# footers and quoted replies, and common English words, words occurring in
	# only one document or in at least 95% of the documents are removed.

	# print "Loading dataset..."
	t0 = time()
	# dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
	# data_samples = dataset.data[:n_samples]
	dataset = create_dataset()
	# data_samples = dataset
	# print "done in %0.3fs." % (time() - t0)
	# print dataset

	# Use tf-idf features for NMF.
	# print "Extracting tf-idf features for NMF..."
	tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=n_features, stop_words='english')
	t0 = time()
	tfidf = tfidf_vectorizer.fit_transform(data_samples)
	# print "done in %0.3fs." % (time() - t0)

	# Use tf (raw term count) features for LDA.
	# print "Extracting tf features for LDA..."
	tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=n_features, stop_words='english')
	t0 = time()
	tf = tf_vectorizer.fit_transform(data_samples)
	# print "done in %0.3fs." % (time() - t0)

	'''
	# Fit the NMF model
	print "Fitting the NMF model with tf-idf features, n_samples=%d and n_features=%d..." % (n_samples, n_features)
	t0 = time()
	nmf = NMF(n_components=n_topics, random_state=1, alpha=.1, l1_ratio=.5).fit(tfidf)
	print "done in %0.3fs." % (time() - t0)

	print "\nTopics in NMF model:"
	tfidf_feature_names = tfidf_vectorizer.get_feature_names()
	print get_top_words(nmf, tfidf_feature_names, n_top_words)
	print 
	'''

	# print "Fitting LDA models with tf features, n_samples=%d and n_features=%d..." % (n_samples, n_features)
	lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5, learning_method='online', learning_offset=50., random_state=0)
	t0 = time()
	lda.fit(tf)
	# print "done in %0.3fs." % (time() - t0)

	# print "\nTopics in LDA model:"
	tf_feature_names = tf_vectorizer.get_feature_names()
	return get_top_words(lda, tf_feature_names, n_top_words)

if __name__ == '__main__':
	path = 'data/Advance C/Command-line-arguments-in-C.txt'
	with open(path, 'r') as f:
		data_samples = clean(f.read())
		data_samples = [x[0] for x in data_samples]
	print(lda(data_samples))