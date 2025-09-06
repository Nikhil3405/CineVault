import joblib 
import logging
import gdown  # for Google Drive

logging.basicConfig(
    level=logging.INFO,  # <-- FIXED HERE
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='recommend.log',encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Google Drive file ID
gdown.download(f"https://drive.google.com/drive/folders/1bTs1KKyIOXREN3gOo-j265lXlafmxo9m?usp=sharing", "df_cleaned.pkl", quiet=False)
gdown.download(f"https://drive.google.com/drive/folders/1bTs1KKyIOXREN3gOo-j265lXlafmxo9m?usp=sharing", "cosine_sim", quiet=False)

logging.info("loading data...")
try:
    df = joblib.load('df_cleaned.pkl')
    cosine_sim = joblib.load('cosine_sim.pkl')
    logging.info('Data loaded successfully.')
except Exception as e:
    logging.info('Failed to load data: %s', str(e))
    raise e

def recommend_movies(movie_name,top_n=10):
    logging.info("Recommending movies for '%s'", movie_name)
    idx = df[df['title'].str.lower() == movie_name.lower()].index
    if len(idx) == 0:
        logging.info("Movie not found in dataset.")
        return None
    idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores,key=lambda x: x[1],reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]
    logging.info('Top %d recommendations ready.', top_n)

    result_df = df[['title']].iloc[movie_indices].reset_index(drop=True)
    result_df.index = result_df.index+1
    result_df.index.name = 'S.No.'

    return result_df
