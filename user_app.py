import streamlit as st
import mysql.connector
from db_connection import get_db_connection
from mysql.connector.cursor import MySQLCursorDict

# Set page config
st.set_page_config(page_title="MovieVerse", page_icon="🎬", layout="wide")

# Inject custom CSS styles for better visuals
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
            font-family: 'Arial', sans-serif;
        }
        
        .title {
            color: #FF6347;
            text-align: center;
            font-size: 3em;
            margin-top: 20px;
            font-weight: bold;
        }

        .movie-entry {
            background-color: #e8f7e7;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 5px solid #28a745;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .movie-title {
            color: #FF6347;
            font-size: 1.8em;
            font-weight: bold;
        }

        .movie-details {
            margin-top: 5px;
            color: #555555;
        }

        .movie-description {
            margin-top: 10px;
            color: #444444;
        }

        .button-like {
            background-color: #28a745;
            color: white;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 1em;
            cursor: pointer;
            margin-top: 15px;
        }

        .button-like:hover {
            background-color: #218838;
        }

        .expander-header {
            color: #28a745;
            font-weight: bold;
        }

        .stCheckbox > div {
            font-size: 1em;
            color: #555555;
        }

        .stVideo {
            border: 2px solid #ddd;
            border-radius: 10px;
            margin-top: 20px;
        }

        .admin-link {
            text-align: center;
            font-size: 1.1em;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Fetching movies data from the database
def fetch_movies(sort_option, search_query):
    conn = get_db_connection()
    if conn is None:
        print("Failed to establish a database connection.")
        return []

    cursor = conn.cursor(cursor_class=MySQLCursorDict)
    query = "SELECT * FROM movies WHERE title LIKE %s ORDER BY %s"
    cursor.execute(query, (f"%{search_query}%", sort_option))
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return movies

# Updating views count in the database
def update_views(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET views = views + 1 WHERE id = %s", (movie_id,))
    conn.commit()
    cursor.close()
    conn.close()

# Updating like count in the database
def update_likes(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET likes = likes + 1 WHERE id = %s", (movie_id,))
    conn.commit()
    cursor.close()
    conn.close()

# Title for user interface
st.markdown('<div class="title">Welcome to MovieVerse</div>', unsafe_allow_html=True)

# Admin Panel Link
st.markdown('<div class="admin-link"><a href="https://movie-universe.streamlit.app/?script=app.py" target="_blank">Go to Admin Panel</a></div>', unsafe_allow_html=True)

# Search bar to search movies
search_query = st.text_input("Search for a movie:", placeholder="Enter movie title...")

# Sorting options
sort_option = st.selectbox("Sort by:", ["Most Watched", "Newest", "All"])

# Fetch and display movies based on the selected sort option or search query
movies = fetch_movies(sort_option, search_query)

if movies:
    for movie in movies:
        with st.container():
            # Movie entry layout without the card borders
            st.markdown(f'<div class="movie-entry">', unsafe_allow_html=True)
            
            # Display movie title with some styling
            st.markdown(f'<div class="movie-title">{movie["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="movie-details">**Views**: {movie["views"]} | **Likes**: {movie["likes"]} | **Uploaded on**: {movie["upload_date"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="movie-description">**Description**: {movie["description"]}</div>', unsafe_allow_html=True)
            
            # Update views every time a movie is displayed
            update_views(movie["id"])

            # Hide/Unhide movies feature with a checkbox
            hide_movie = st.checkbox(f"Hide {movie['title']}", key=f"hide_{movie['id']}", value=movie.get("hidden", False))
            
            if hide_movie:
                # Mark the movie as hidden in the database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE movies SET hidden=TRUE WHERE id=%s", (movie["id"],))
                conn.commit()
                cursor.close()
                conn.close()
                st.write(f"**{movie['title']}** is now hidden.")
                continue

            # Video display with better presentation
            video_source = movie['video_url']
            
            # Slide down/up feature for movie details
            with st.expander(f"Watch {movie['title']}", expanded=False):
                st.markdown(f'<div class="expander-header">Watch Now</div>', unsafe_allow_html=True)
                if video_source.startswith("http"):  # If it's a URL
                    st.video(video_source)
                else:  # If it's a local file
                    st.video(video_source)  # Plays local files

            # Like Button Feature (increments likes when clicked)
            if st.button(f"Like {movie['title']} 👍"):
                update_likes(movie["id"])  # Update the like count
                st.success(f"You liked {movie['title']}!")
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close movie entry div

else:
    st.warning("No movies available.")
