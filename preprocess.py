import pandas as pd
import re
import nltk
import joblib
import logging
from nltk.corpus import stopwords
from nltk.tokenize  import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s]%(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='preprocess.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
)

logging.info("Starting preprocessing...")

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

try:
    df = pd.read_csv('movies.csv')
    logging.info('Dataset loaded successfully.')
except Exception as e:
    logging.info(msg='Failed to load dataset: %s', args=str(e))
    raise e

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', str(text))
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

required_columns = ['genres','keywords','overview','title']

df = df[required_columns]

df = df.dropna().reset_index(drop=True)

df['combined'] = df['genres']+' '+df['keywords']+' '+df['overview']

logging.info('cleaneding text...')
df['cleaned_text'] = df['combined'].apply(preprocess_text)
logging.info('text cleaned.')

logging.info('Vectorizing using TF-IDF...')
tfidf = TfidfVectorizer(max_features=5000)
tfidf_matrix = tfidf.fit_transform(df['cleaned_text'])
# logging.info(msg='TF-IDF matrix shape: %s', args=str(tfidf_matrix.shape))

logging.info('Calculating cosine similarity...')
cosine_sim = cosine_similarity(tfidf_matrix,tfidf_matrix)
logging.info('Cosine similarity matrix generated.')

joblib.dump(df,filename='df_cleaned.pkl')
joblib.dump(tfidf_matrix,filename='tfidf_matrix.pkl')
joblib.dump(cosine_sim,filename='cosine_sim.pkl')
logging.info('Data saved to file')

logging.info('Preprocessing completed')