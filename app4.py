import pandas as pd
import numpy as np
import pickle
import streamlit as st
import os
import requests

# Load movie data and similarity matrix
movies = pickle.load(open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\movie_list.pkl", 'rb'))
similarity = pickle.load(open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\similarity.pkl", 'rb'))

# Function to fetch movie poster
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    
    # Check if poster_path is not None
    if poster_path is not None:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return None  # or handle the case where poster_path is None appropriately


# Function for user authentication (signup and login)
def authenticate_user():
    st.header('User Authentication')
    new_user = st.checkbox('New User?')
    username = st.text_input('Username:')
    password = st.text_input('Password:', type='password')

    if new_user:
        new_username = st.text_input('Create a new username:')
        new_password = st.text_input('Create a new password:', type='password')

        if st.button('Sign Up'):
            if not new_username or not new_password:
                st.error('Username and password cannot be empty')
            else:
                # Check if the user already exists
                if os.path.exists(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl"):
                    user_credentials = pickle.load(open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl", "rb"))
                    if new_username in user_credentials:
                        st.error('Username already exists. Please choose a different one.')
                        return

                # Save the new user's credentials
                user_credentials = {}
                if os.path.exists(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl"):
                    user_credentials = pickle.load(open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl", "rb"))
                user_credentials[new_username] = new_password
                pickle.dump(user_credentials, open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl", "wb"))
                st.success('Sign up successful! You can now log in.')

    else:  # Existing user trying to log in
        if st.button('Log In'):
            if os.path.exists(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl"):
                user_credentials = pickle.load(open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\user_credentials.pkl", "rb"))
                if username in user_credentials and user_credentials[username] == password:
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    # Add logic to navigate to admin panel or any other page upon successful login
                else:
                    st.error("Invalid username or password")
            else:
                st.error("No user registered. Please sign up first.")

# Admin Panel with login
def admin_panel_with_login():
    st.header('Admin Panel: Login Required')
    admin_id = st.text_input("Enter Admin ID:")
    admin_password = st.text_input("Enter Admin Password:", type="password")
    
    if admin_id == "admin" and admin_password == "password":
        st.success("Logged in as admin")
        delete_movie()
        update_movie_details()  # Add the function to update movie details
    elif admin_id or admin_password:
        st.error("Invalid Admin ID or Password")

# Admin Panel without login
def admin_panel_without_login():
    st.header('Admin Panel: No Login Required')
    add_new_movie()

# Function to recommend movies
def recommend(movie):
    # Reload the movie dataset to get the latest updates
    movies = pickle.load(open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\movie_list.pkl", 'rb'))
    
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies_details = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        # Fetch movie details from the API
        movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(movie_details_url)
        if response.status_code == 200:
            movie_data = response.json()
            genre = ', '.join([genre['name'] for genre in movie_data['genres']])
            overview = movie_data['overview']
            poster_path = movie_data['poster_path']
            
            # Check if poster_path is not None
            if poster_path is not None:
                recommended_movie_details = {
                    'name': movie_data['title'],
                    'poster': fetch_poster(movie_id),
                    'genre': genre,
                    'overview': overview,
                    'poster_path': poster_path
                }
                recommended_movies_details.append(recommended_movie_details)
            else:
                # Handle the case where poster_path is None
                print(f"Skipping movie '{movie_data['title']}' because poster path is None.")
    return recommended_movies_details

# Function to add new movie
def add_new_movie():
    global movies  # Declare movies as global
    new_movie_title = st.text_input('Enter new movie title:')
    new_movie_id = st.text_input('Enter new movie ID:')
    new_movie_genre = st.text_input('Enter movie genre:')
    new_movie_cast = st.text_input('Enter movie cast:')
    new_movie_overview = st.text_area('Enter movie overview:')
    new_movie_keywords = st.text_input('Enter movie keywords:')
    new_movie_poster_path = st.text_input('Enter movie poster path:')
    
    if st.button('Add Movie'):
        try:
            # Check if the movie title and ID are not empty
            if not new_movie_title or not new_movie_id:
                raise ValueError('Movie title and ID cannot be empty')

            # Check if the movie ID is a valid integer
            try:
                int(new_movie_id)
            except ValueError:
                raise ValueError('Movie ID must be a valid integer')

            # Check if the movie already exists in the database
            if new_movie_title in movies['title'].values:
                raise ValueError('Movie already exists in the database')

            # Add the new movie to the database
            new_movie_data = pd.DataFrame({'title': [new_movie_title], 
                                           'movie_id': [int(new_movie_id)], 
                                           'genre': [new_movie_genre],
                                           'cast': [new_movie_cast],
                                           'overview': [new_movie_overview],
                                           'keywords': [new_movie_keywords],
                                           'poster_path': [new_movie_poster_path]})
            movies = pd.concat([movies, new_movie_data], ignore_index=True)
            pickle.dump(movies, open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\movie_list.pkl", 'wb'))
            st.success('New movie added successfully!')
        except ValueError as e:
            st.error(e)

# Function to delete movie
def delete_movie():
    global movies  # Declare movies as global
    movie_title = st.text_input('Enter movie title to delete:')

    if st.button('Delete Movie'):
        try:
            # Check if the movie title is not empty
            if not movie_title:
                raise ValueError('Movie title cannot be empty')

            # Check if the movie exists in the database
            if movie_title not in movies['title'].values:
                raise ValueError('Movie not found in the database')

            # Delete the movie from the database
            movies = movies[movies['title'] != movie_title]
            pickle.dump(movies, open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\movie_list.pkl", 'wb'))
            st.success('Movie deleted successfully!')
        except ValueError as e:
            st.error(e)
# Function to update movie details
def update_movie_details():
    global movies  # Declare movies as global
    movie_title = st.text_input('Enter movie title to update:')
    if st.button('Update Movie Details'):
        try:
            # Check if the movie title is not empty
            if not movie_title:
                raise ValueError('Movie title cannot be empty')

            # Check if the movie exists in the database
            if movie_title not in movies['title'].values:
                raise ValueError('Movie not found in the database')

            # Fetch the index of the movie
            movie_index = movies.loc[movies['title'] == movie_title].index[0]

            # Use st.form for input fields
            with st.form(key='update_movie_form'):
                # Get updated details
                new_movie_genre = st.text_input('Enter updated genre:', value=movies.at[movie_index, 'genre'])
                new_movie_cast = st.text_input('Enter updated cast:', value=movies.at[movie_index, 'cast'])
                new_movie_overview = st.text_area('Enter updated overview:', value=movies.at[movie_index, 'overview'])
                new_movie_keywords = st.text_input('Enter updated keywords:', value=movies.at[movie_index, 'keywords'])
                new_movie_poster_path = st.text_input('Enter updated poster path:', value=movies.at[movie_index, 'poster_path'])

                # Add a separate button for submission
                submitted = st.form_submit_button('Submit')

                # Update movie details if submitted
                if submitted:
                    # Update movie details in the dataset
                    movies.at[movie_index, 'genre'] = new_movie_genre
                    movies.at[movie_index, 'cast'] = new_movie_cast
                    movies.at[movie_index, 'overview'] = new_movie_overview
                    movies.at[movie_index, 'keywords'] = new_movie_keywords
                    movies.at[movie_index, 'poster_path'] = new_movie_poster_path

                    # Save the updated movie data
                    pickle.dump(movies, open(r"C:\Users\MEET PRAJAPATI\OneDrive\Desktop\movie_recommender_system-main\movie_list.pkl", 'wb'))
                    st.success('Movie details updated successfully!')
                    
                    # Update movie details in the external API
                    update_movie_in_api(new_movie_title, new_movie_genre, new_movie_cast, new_movie_overview, new_movie_keywords, new_movie_poster_path)

        except ValueError as e:
            st.error(e)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to update movie details in the external API
def update_movie_in_api(movie_title, new_genre, new_cast, new_overview, new_keywords, new_poster_path):
    try:
        # Fetch the movie ID from your dataset
        movie_id = movies.loc[movies['title'] == movie_title, 'movie_id'].iloc[0]
        
        # Construct the payload with updated movie details
        payload = {
            'genre': new_genre,
            'cast': new_cast,
            'overview': new_overview,
            'keywords': new_keywords,
            'poster_path': new_poster_path
        }
        
        # Send a PUT request to the API endpoint to update the movie details
        api_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.put(api_url, json=payload)
        
        if response.status_code == 200:
            logging.info('Movie details updated in the external API successfully!')
            st.success('Movie details updated in the external API successfully!')
        else:
            logging.error(f'Failed to update movie details in the external API. Status code: {response.status_code}')
            st.error('Failed to update movie details in the external API')
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        st.error('An error occurred while updating movie details in the external API')


# Main app
st.sidebar.header('Navigation')
selected_page = st.sidebar.selectbox('Select a page:', ['Home', 'Admin Panel (Login Required)', 'Admin Panel (No Login Required)', 'Sign Up / Log In'])

if selected_page == 'Home':
    if not st.session_state.get('logged_in'):
        st.warning("Please log in to view movie recommendations.")
        authenticate_user()
    else:
        movie_list = np.array(movies['title']).flatten()
        selected_movie = st.selectbox('Type or select a movie from the dropdown:', movie_list)
        if st.button('Show Recommendation'):
            recommended_movies_details = recommend(selected_movie)  # Fetch recommended movie details
            for movie in recommended_movies_details:
                st.image(movie['poster'], width=159)  # Display movie poster with width set to 159 pixels
                st.text(movie['name'])  # Display movie title
                st.text('Genre: ' + str(movie['genre']))  # Display movie genre
                st.text('Overview: ' + str(movie['overview']))  # Display movie overview
                st.markdown('---')  # Add a horizontal line to separate movie details
elif selected_page == 'Admin Panel (Login Required)':
    admin_panel_with_login()
elif selected_page == 'Admin Panel (No Login Required)':
    admin_panel_without_login()
elif selected_page == 'Sign Up / Log In':
    authenticate_user()
