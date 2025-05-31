import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# nltk.download('stopwords')
# nltk.download('punkt_tab')
# nltk.download('wordnet')
stpwrds = stopwords.words('english')

def clean_text(txt):
    txt = re.sub(r'\s+', ' ', txt).strip()
    txt = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', txt)
    txt = txt.lower()

    #now the text is in lower and without extra spaces
    sentences = sent_tokenize(txt)
    for i in range(len(sentences)):
        words = word_tokenize(sentences[i])
        lemmatizer = WordNetLemmatizer()

        #now let us remove the stop words and lemmatize the others
        words = [lemmatizer.lemmatize(word, 'v') for word in words if word not in stpwrds]
        sentences[i] = ' '.join(words)

    return txt