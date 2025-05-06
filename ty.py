import pandas as pd
import streamlit as st
import pickle
import requests
import urllib.parse

# TMDb API Key
API_KEY = '87c4de2ca6ee9ad0ad0fe9c7946a3a05'

# Function to fetch poster using movie title
def fetch_poster_by_title(title):
    try:
        # Search movie by title
        query = urllib.parse.quote(title)
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
        search_response = requests.get(search_url, timeout=5)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data.get('results'):
            return "https://via.placeholder.com/400x600?text=No+Poster"

        movie = search_data['results'][0]
        poster_path = movie.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/400x600?text=No+Poster+Found"

    except Exception as e:
        print(f"Error fetching poster for {title}: {e}")
        return "https://via.placeholder.com/400x600?text=Error"

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster_by_title(title)
        if "placeholder" not in poster:  # Skip if no poster
            recommended_movies.append(title)
            recommended_posters.append(poster)
        if len(recommended_movies) == 5:
            break

    # Fill with placeholders if fewer than 5 found
    while len(recommended_movies) < 5:
        recommended_movies.append("N/A")
        recommended_posters.append("https://via.placeholder.com/400x600?text=No+Poster")

    return recommended_movies, recommended_posters

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox("Select a movie you like 👇", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.markdown(f"**{names[i]}**")
            st.image(posters[i], width=200)

# Custom CSS
st.markdown(
    """
    <style>
    img {
        object-fit: cover;
        width: 200px;
        height: 300px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True
)
