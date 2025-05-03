import pickle
import streamlit as st
import requests
import os
import heapq

# Fetch TMDB API Key from environment variables
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    st.error("TMDB API Key is not set. Please configure it in your environment variables.")
    st.stop()

def fetch_poster(movie_id):
    """Fetch the poster URL for a given movie ID."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            st.warning(f"No poster found for movie ID {movie_id}. Using placeholder image.")
            return "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

def recommend(movie):
    """Recommend movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = list(enumerate(similarity[index]))
        top_5 = heapq.nlargest(6, distances, key=lambda x: x[1])[1:]
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in top_5:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], []

@st.cache
def load_data():
    """Load movies and similarity data."""
    try:
        movies = pickle.load(open('model/movie_list.pkl', 'rb'))
        similarity = pickle.load(open('model/similarity.pkl', 'rb'))
        return movies, similarity
    except FileNotFoundError as e:
        st.error(f"Required data file not found: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Load data
movies, similarity = load_data()

# Streamlit UI
st.header('Movie Recommender System')
st.write("Select a movie from the dropdown below to get recommendations:")

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Fetching recommendations...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    if recommended_movie_names and recommended_movie_posters:
        st.subheader("Recommended Movies:")
        cols = st.columns(len(recommended_movie_names))
        for idx, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[idx])
                st.image(recommended_movie_posters[idx])
    else:
        st.warning("No recommendations found.")