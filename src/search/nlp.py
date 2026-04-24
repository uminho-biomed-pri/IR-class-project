import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords

#class TextProcessor:
#    def __init__(self, language='english'):
#        """
#        Incializa o processador de texto com suporte configurável ao idioma.
#        """
#
#        self.language=language
#        #download dos modelos nltk necessários
#        nltk.download('punkt', quiet=True)
#        nltk.download('averaged_perceptron_tagger', quiet=True)
#        nltk.download('stopwords', quiet=True)
#        nltk.download('wordnet',quiet=True)
#
#        self.stemmer_en = PorterStemmer()
#        self.lemmatizer=WordNetLemmatizer()
#
#        self.stop_words = set(stopwords.words(self.language))


