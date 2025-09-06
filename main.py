import os
import json
import streamlit as st
from recommend import df, recommend_movies
from omdb_utils import get_movie_details
import gdown

gdown.download("https://drive.google.com/uc?id=1tvoEPsG1716et27BlxzHOWOlq4_6iVjX", "config.json", quiet=False)

# Load configuration
config = json.load(open("config.json"))
OMDB_API_KEY = config['OMDB_API_KEY']

# Page configuration
st.set_page_config(
    page_title='CineVault - Movie Recommender',
    page_icon='🎬',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Custom CSS for modern dark theme without pink
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling for dark theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: #E8E8E8;
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        background: transparent;
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Main title styling with holographic effect */
    .main-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient 8s ease infinite;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        letter-spacing: -2px;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.4rem;
        color: #A8B2D1;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced movie recommendation container */
    .movie-recommendation-container {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        border-radius: 25px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.4),
            inset 0 1px 0 rgba(255,255,255,0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        position: relative;
        overflow: hidden;
    }
    
    .movie-recommendation-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #4facfe);
        border-radius: 25px 25px 0 0;
    }
    
    .movie-recommendation-container:hover {
        transform: translateY(-10px) scale(1.01);
        box-shadow: 
            0 30px 80px rgba(0,0,0,0.5),
            0 0 50px rgba(102, 126, 234, 0.1),
            inset 0 1px 0 rgba(255,255,255,0.15);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    /* Poster styling with reflection effect */
    .poster-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 20px;
        position: relative;
    }
    
    .poster-image {
        border-radius: 20px;
        box-shadow: 
            0 15px 40px rgba(0,0,0,0.6),
            0 0 20px rgba(102, 126, 234, 0.1);
        border: 2px solid rgba(255,255,255,0.1);
        transition: all 0.4s ease;
        max-width: 200px;
        position: relative;
    }
    
    .poster-image:hover {
        transform: scale(1.05) rotateY(5deg);
        box-shadow: 
            0 20px 50px rgba(0,0,0,0.7),
            0 0 30px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .poster-placeholder {
        width: 200px;
        height: 300px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
        font-weight: 500;
        text-align: center;
        box-shadow: 
            0 15px 40px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.1);
        transition: all 0.4s ease;
    }
    
    .poster-placeholder:hover {
        transform: scale(1.05) rotateY(5deg);
        box-shadow: 
            0 20px 50px rgba(0,0,0,0.7),
            0 0 30px rgba(102, 126, 234, 0.3);
    }
    
    .movie-rank {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 1rem;
        font-weight: 600;
        padding: 12px 20px;
        border-radius: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        text-align: center;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .movie-rank:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
    }
    
    /* Content container with better spacing */
    .content-container {
        padding: 25px 30px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    
    .movie-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    
    .movie-plot {
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 25px;
        color: #C4C4C4;
        text-align: justify;
        flex-grow: 1;
        padding: 20px;
        background: rgba(30, 30, 46, 0.6);
        border-radius: 15px;
        border-left: 4px solid #667eea;
        backdrop-filter: blur(10px);
        font-weight: 300;
    }
    
    .movie-details {
        background: linear-gradient(145deg, #1a1a2e, #2d2d44);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin-top: 20px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }
    
    .movie-details p {
        margin: 12px 0;
        color: #A8B2D1;
        font-size: 1.05rem;
        font-weight: 400;
    }
    
    .movie-details strong {
        color: #E8E8E8;
        font-weight: 600;
    }
    
    /* Search section with modern glass effect */
    .search-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(116, 75, 162, 0.2));
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 50px;
        margin-bottom: 50px;
        text-align: center;
        color: white;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .search-section h2 {
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: #FFD700;
    }
    
    .search-section p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 1rem 3rem;
        font-size: 1.3rem;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 
            0 8px 30px rgba(102, 126, 234, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.1);
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.6),
            inset 0 1px 0 rgba(255,255,255,0.2);
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    /* Select box modern styling */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        color: #E8E8E8;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 
            0 0 20px rgba(102, 126, 234, 0.3),
            inset 0 1px 0 rgba(255,255,255,0.1);
    }
    .stSelectbox input {
        color: #FFD700 !important;   /* golden text */
        font-weight: 500;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        color: #FFD700 !important;   /* selected option color */
    }
            /* Center align spinner text */
    .stSpinner > div {
        text-align: center !important;
        display: flex;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 500;
    }


    /* Success message with gradient text */
    .success-header {
        text-align: center;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #4CAF50, #8BC34A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 40px 0;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
        letter-spacing: -1px;
    }
    
    /* Enhanced stats styling */
    .stat-box {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        color: white;
        padding: 25px 35px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 
            0 10px 30px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
    }
    
    .stat-box:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 50px rgba(0,0,0,0.4),
            0 0 30px rgba(79,172,254,0.3),
            inset 0 1px 0 rgba(255,255,255,0.15);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 1.1rem;
        color: #A8B2D1;
        margin-top: 8px;
        font-weight: 400;
    }
    
    /* Footer styling */
    .footer-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(116, 75, 162, 0.1));
        backdrop-filter: blur(20px);
        border-radius: 25px;
        margin-top: 60px;
        padding: 35px;
        text-align: center;
        box-shadow: 
            0 15px 40px rgba(0,0,0,0.2),
            inset 0 1px 0 rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .footer-section h3 {
        color: #FFD700;
        margin-bottom: 15px;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .footer-section p {
        color: #A8B2D1;
        margin: 0;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
</style>
""", unsafe_allow_html=True)

# Header section with enhanced styling
st.markdown('<h1 class="main-title">🎬 CineVault</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover cinematic masterpieces with AI-powered precision</p>', unsafe_allow_html=True)

# Statistics section
col1, col2, col3 = st.columns(3)
total_movies = len(df['title'].dropna().unique())

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{total_movies:,}</div>
        <div class="stat-label">Movies Available</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">AI</div>
        <div class="stat-label">Neural Engine</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">∞</div>
        <div class="stat-label">Possibilities</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Search section with glass morphism effect
with st.container():
    st.markdown("""
    <div class="search-section">
        <h2>🔍 Discover Your Next Obsession</h2>
        <p>Select a movie you love, and watch our AI uncover cinematic gems tailored just for you</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Movie selection with enhanced styling
    movie_list = sorted(df['title'].dropna().unique())
    # Custom colored label above
    st.markdown(
        "<p style='font-size:1.2rem; font-weight:bold; color:#FFD700; margin-bottom:15px;'>Select a movie you love:</p>",
        unsafe_allow_html=True
    )

    # Add "None" option at the top so initially nothing is selected
    movie_list_with_blank = [""] + list(movie_list)

    selected_movie = st.selectbox(
        '',
        movie_list_with_blank,
        index=0,   # first one = blank
        help="Select from our curated database to get intelligent recommendations"
    )

    # Replace empty string with None for easier handling
    if selected_movie == "":
        selected_movie = None

    
    # Center the enhanced button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        recommend_button = st.button("🚀 Generate Recommendations", use_container_width=True)

# Enhanced recommendation results
if recommend_button:
    if selected_movie:
        with st.spinner(f"Fetching details for {selected_movie}..."):
            plot, poster, director, actors, year = get_movie_details(selected_movie, OMDB_API_KEY)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#FFD700;'>🎥 Your Selection: {selected_movie}</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])

        with col1:
            if poster != 'N/A':
                st.image(poster, use_container_width=True)
            else:
                st.markdown("""
                <div class="poster-placeholder">
                    <div style="font-size: 2rem;">🎬</div>
                    <div>No Poster Available</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="movie-details">
                <p><strong>📖 Plot:</strong> {plot if plot != 'N/A' else 'No plot information available.'}</p>
                <p><strong>🎬 Director:</strong> {director if director != 'N/A' else 'Not available'}</p>
                <p><strong>🎭 Cast:</strong> {actors if actors != 'N/A' else 'Not available'}</p>
                <p><strong>📅 Year:</strong> {year if year != 'N/A' else 'Not available'}</p>
            </div>
            """, unsafe_allow_html=True)

        with st.spinner(f"🎯 Analyzing cinematic DNA and curating perfect matches..."):
            recommendations = recommend_movies(selected_movie)
            
        if recommendations is None or recommendations.empty:
            st.error("🚫 No recommendations found for this selection. Please try another movie.")
        else:
            st.markdown('<h2 class="success-header">🌟 Your Personalized Cinema Collection</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #A8B2D1; margin-bottom: 3rem; font-weight: 300;'>Curated based on: <strong style='color: #FFD700;'>{selected_movie}</strong></p>", unsafe_allow_html=True)
            
            # Create enhanced movie cards
            for index, row in recommendations.iterrows():
                movie_title = row['title']
                
                with st.spinner(f"🎬 Loading cinematic details for {movie_title}..."):
                    plot, poster, director, actors = get_movie_details(movie_title, OMDB_API_KEY)
                
                # Movie recommendation container
                st.markdown(f"""
                <div class="movie-recommendation-container">
                """, unsafe_allow_html=True)
                
                # Create columns with optimal proportions
                col1, col2 = st.columns([1, 2.2], gap="large")
                
                with col1:
                    st.markdown('<div class="poster-container">', unsafe_allow_html=True)
                    if poster != 'N/A':
                        st.image(poster, use_container_width=True, caption="")
                        st.markdown(f'<div class="movie-rank">#{index} Recommendation</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="poster-placeholder">
                            <div style="font-size: 2.5rem; margin-bottom: 15px;">🎬</div>
                            <div>Poster<br>Unavailable</div>
                        </div>
                        <div class="movie-rank">#{index} Recommendation</div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="content-container">', unsafe_allow_html=True)
                    
                    # Movie title with gradient effect
                    st.markdown(f'<div class="movie-title">{movie_title}<br>Year: {year}</div>', unsafe_allow_html=True)
                    
                    # Enhanced plot section
                    plot_text = plot if plot != 'N/A' else 'Plot information is currently unavailable for this cinematic piece. This could be a rare gem or independent film that our algorithm has identified based on sophisticated pattern matching and thematic analysis.'
                    st.markdown(f'<div class="movie-plot">📖 {plot_text}</div>', unsafe_allow_html=True)
                    
                    # Enhanced movie details
                    st.markdown(f"""
                    <div class="movie-details">
                        <p><strong>🎬 Director:</strong> {director if director != 'N/A' else 'Information currently unavailable'}</p>
                        <p><strong>🎭 Featured Cast:</strong> {actors if actors != 'N/A' else 'Cast information not available'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)
            
            # Enhanced footer message
            st.markdown("""
            <div class="footer-section">
                <h3>🎉 Your Cinematic Journey Awaits</h3>
                <p>Found something intriguing? Select any of these recommendations to discover even more hidden gems!</p>
            </div>
            """, unsafe_allow_html=True)
