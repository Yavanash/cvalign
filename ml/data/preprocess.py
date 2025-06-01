import re
import pandas as pd
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
    txt = re.sub(r"[^\x00-\x7f]", r"", txt)
    txt = re.sub(r"(\n|\r)+", r"\n", txt).strip()
    txt = re.sub(r" +", r" ", txt).strip()
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

# df = pd.read_csv("job_title_des.csv")
# df["pjdesc"] = df["Job Description"].apply(clean_text)
# df = df.drop(columns=["Job Description", "Unnamed: 0"])

# df1 = pd.read_csv("synthetic-resumes.csv")
# df1["cv"] = df1["Resume"].apply(clean_text)
# # print(df1.head(5))
# df1.to_csv("test.csv", index=False)

# print(df.head(3))
# df.to_csv("data.csv", index=False)