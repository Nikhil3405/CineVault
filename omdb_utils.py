import requests

def get_movie_details(title,api_key):
    url = f'https://www.omdbapi.com/?t={title}&plot=full&apikey={api_key}'
    res = requests.get(url).json()
    if res.get('Response') == 'True':
        result = res.get("Plot",'N/A'),res.get('Poster','N/A'),res.get('Director','N/A'),res.get('Actors','N/A')
        plot = result[0]
        poster = result[1]
        director = result[2]
        actors = result[3]
        return plot,poster,director,actors
    
    return 'N/A','N/A','N/A','N/A'