import os
import streamlit as st
import mysql.connector
from db_connection import get_db_connection

st.set_page_config(page_title="Admin Panel", page_icon="🎬", layout="wide")

# ----------------------------------
# Inject custom CSS styles
# ----------------------------------
st.markdown("""<style> ... (your CSS unchanged) ... </style>""", unsafe_allow_html=True)

# ----------------------------------
# Admin Login Function
# ----------------------------------
def login():
    st.title("Admin Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM admins WHERE username=%s AND password=%s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

            cursor.close()
            conn.close()
        else:
            st.error("Failed to connect to the database. Please check your connection settings.")

# Show login page if user is not logged in
if "logged_in" not in st.session_state:
    login()

# ----------------------------------
# Logout
# ----------------------------------
if st.session_state.get("logged_in"):
    if st.button("Logout"):
        del st.session_state["logged_in"]
        st.success("Logged out successfully!")
        st.rerun()

# ----------------------------------
# Fetch Movies Function
# ----------------------------------
def fetch_movies():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM movies ORDER BY upload_date DESC")
            movies = cursor.fetchall()
            cursor.close()
            conn.close()
            return movies
    except Exception as e:
        st.error(f"Failed to fetch movies: {e}")
        return []

# ----------------------------------
# Admin Panel
# ----------------------------------
if st.session_state.get("logged_in"):
    st.markdown('<div class="title">Admin Panel</div>', unsafe_allow_html=True)
    st.write("Manage your movie uploads and videos here.")
    
    # Fetch movies data
    movies = fetch_movies()

    # Display all movies
    st.subheader("All Movies")
    for movie in movies:
        st.markdown(f'<div class="movie-entry">', unsafe_allow_html=True)
        st.markdown(f'<div class="movie-title">{movie["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="movie-details">**Description**: {movie["description"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="movie-details">**Upload Date**: {movie["upload_date"]} | **Views**: {movie["views"]} | **Hidden**: {"Yes" if movie["hidden"] else "No"}</div>', unsafe_allow_html=True)
        st.markdown(f'</div>', unsafe_allow_html=True)

    # ----------------------------------
    # Add Movie
    # ----------------------------------
    st.subheader("Add New Movie")
    with st.form("add_movie_form"):
        upload_method = st.radio("Select Upload Method", ("Upload File", "Enter Video URL"), key="upload_method")

        if upload_method == "Upload File":
            uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi", "mkv", "flv", "wmv", "webm", "m4v"], key="movie_file")
            video_url = None
        else:
            uploaded_file = None
            video_url = st.text_input("Video URL", key="video_url")

        title = st.text_input("Movie Title", key="movie_title")
        description = st.text_area("Description", key="movie_description")
        submit_button = st.form_submit_button("Add Movie")

        if submit_button:
            if title and description and (uploaded_file or video_url):
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    if uploaded_file:
                        movies_dir = "movies"
                        if not os.path.exists(movies_dir):
                            os.makedirs(movies_dir)
                        video_path = os.path.join(movies_dir, uploaded_file.name)
                        with open(video_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        query = "INSERT INTO movies (title, description, video_url, upload_date, hidden) VALUES (%s, %s, %s, NOW(), %s)"
                        cursor.execute(query, (title, description, video_path, False))
                    elif video_url:
                        query = "INSERT INTO movies (title, description, video_url, upload_date, hidden) VALUES (%s, %s, %s, NOW(), %s)"
                        cursor.execute(query, (title, description, video_url, False))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Movie added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to connect to the database.")
            else:
                st.error("All fields are required!")

    # ----------------------------------
    # Update Movie
    # ----------------------------------
    st.subheader("Update Movie Details")
    movie_titles = [movie['title'] for movie in movies]

    if movie_titles:
        movie_to_update = st.selectbox("Select Movie to Update", movie_titles, key="update_movie")
        selected_movie = next((movie for movie in movies if movie['title'] == movie_to_update), None)
        if selected_movie:
            new_title = st.text_input("New Title", value=selected_movie['title'], key="update_title")
            new_description = st.text_area("New Description", value=selected_movie['description'], key="update_description")
            new_video_url = st.text_input("New Video URL", value=selected_movie['video_url'], key="update_video_url")
            hide_movie = st.checkbox("Hide this movie", value=selected_movie['hidden'])

            if st.button("Update Movie", key="update_button"):
                if new_title and new_description and new_video_url:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        update_query = """
                            UPDATE movies 
                            SET title=%s, description=%s, video_url=%s, hidden=%s
                            WHERE id=%s
                        """
                        cursor.execute(update_query, (new_title, new_description, new_video_url, hide_movie, selected_movie['id']))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("Movie updated successfully!")
                        st.rerun()
                else:
                    st.error("All fields are required!")

    # ----------------------------------
    # Delete Movie
    # ----------------------------------
    st.subheader("Delete Movie")
    if movie_titles:
        movie_to_delete = st.selectbox("Select Movie to Delete", movie_titles, key="delete_movie")
        selected_movie = next((movie for movie in movies if movie['title'] == movie_to_delete), None)

        if st.button("Delete Movie", key="delete_button") and selected_movie:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM movies WHERE id=%s", (selected_movie['id'],))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Movie deleted successfully!")
                st.rerun()
