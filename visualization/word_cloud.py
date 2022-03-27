from config import run_query, TABLE_ROOT_MESSAGES, TABLE_THREAD_REPLIES
import spacy
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS #, ImageColorGenerator
import matplotlib.pyplot as plt


sp = spacy.load("en_core_web_sm")
spacy_stopwords = sp.Defaults.stop_words
wordcloud_stopwords = set(STOPWORDS)
wordcloud_stopwords.update([
                            "use", "run","try", "work", "create","start","help", "find","need",
                            "week", "error", "issue", "question" ,"video", "file","course", "datum","hello"])





# Resource: https://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html
def tokenize_lemmatize_messages(message):
    message = message.lower()
    doc = sp(message)
    lemmas = [token.lemma_ for token in doc]
    lemmas = [lemma for lemma in lemmas if len(lemma) > 2 if not lemma in stopwords.words('english')]
    lemmas = [lemma for lemma in lemmas if not lemma in spacy_stopwords]
    return " ".join(lemmas)

def transform_data(df):
    # apply lemmatization transformation on text column
    # to reduce the word variety and focus the topics
    df_text= df['text'].apply(lambda x: tokenize_lemmatize_messages(x))
    return df_text

def create_wordcloud_figure(df_text):
    wordcloud = WordCloud(width = 1000, height = 1000,
                background_color ='white',
                stopwords = wordcloud_stopwords,
                min_font_size = 10).generate(" ".join(df_text.values))
    plt.figure(figsize=(13, 13))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("./images/wordcloud.png", format="png")


def populate_wordcloud(df):
    df_text = transform_data(df=df)
    create_wordcloud_figure(df_text=df_text)
    print(f"The WordClod figure is created for {TABLE_ROOT_MESSAGES}")


