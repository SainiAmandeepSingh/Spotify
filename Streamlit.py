"""
Spotify Recommendation System
@author: Singh AmanDeep Saini
"""

# =============================================================================
                        # Spotify Recommendation System
# =============================================================================


# Import & Loading All Libraries

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
import base64
import requests
import re


# =============================================================================
# Spotify API Credentials
# =============================================================================


# My Confidential API Keys
CLIENT_ID = "ee935c77a0094a5b960115f622372f8b"
CLIENT_SECRET = "266656bf71cd4c89807d8a12c6ed50ba"


# Spotify API Authentication: Acquiring Access Token
def authenticate_spotify(client_id, client_secret):
    # Ensuring both Client ID and Client Secret are provided
    if not client_id or not client_secret:
        return None, "Client ID and Client Secret are required"
    # Encoding the credentials
    credentials = f"{client_id}:{client_secret}"
    credentials_base64 = base64.b64encode(credentials.encode())
    # Defining the token URL
    token_url = 'https://accounts.spotify.com/api/token'
    # Setting up headers for the request
    headers = {'Authorization': f'Basic {credentials_base64.decode()}'}
    # Data payload for the POST request
    data = {'grant_type': 'client_credentials'}
    # Making the request to obtain the access token
    response = requests.post(token_url, data=data, headers=headers)
    # Successful authentication
    if response.status_code == 200:
        return response.json()['access_token'], "Authentication successful"
    # Authentication failed
    else:
        return None, "Authentication failed"

# Setting up Spotify client for accessing the API
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# =============================================================================
# Spotify Recommendation Function
# =============================================================================


# Retrieve Album Cover URL by Song and Artist
def get_song_album_cover_url(song_name, artist_name):
    # Constructing a search query with song and artist names
    search_query = f"track:{song_name} artist:{artist_name}"
    # Executing search on Spotify
    results = sp.search(q=search_query, type="track")
    # Returning album cover URL if the song is found
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    # Default image URL if song isn't found
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

# Generate Music Recommendations Based on a Song
def recommend(song):
    # Finding song index in dataset for similarity comparison
    index = music[music['song'] == song].index[0]
    # Sorting similarity scores in descending order
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    # Collecting names and album covers of recommended songs
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:11]:  # Fetching top 10 recommendations
        artist = music.iloc[i[0]].artist
        song_title = music.iloc[i[0]].song
        recommended_music_posters.append(get_song_album_cover_url(song_title, artist))
        recommended_music_names.append(song_title)
    return recommended_music_names, recommended_music_posters

# Extract Song ID from Spotify URL
def get_song_id_from_url(song_url):
    # Defining pattern to extract song ID
    pattern = r'spotify:track:(\w+)|https://open\.spotify\.com/track/(\w+)'
    match = re.search(pattern, song_url)
    # Returning song ID if found
    if match:
        return match.group(1) or match.group(2)
    else:
        return None

# Get Spotify Recommendations Based on a Song URL
def get_spotify_recommendations(song_url, sp):
    song_id = get_song_id_from_url(song_url)
    if song_id:
        # Fetching recommendations from Spotify using the song ID
        recommended_tracks = sp.recommendations(seed_tracks=[song_id], limit=10)['tracks']
        # Collecting data for recommended songs
        recommended_music_names = [track['name'] for track in recommended_tracks]
        recommended_music_artists = [track['artists'][0]['name'] for track in recommended_tracks]
        recommended_music_posters = [track['album']['images'][0]['url'] for track in recommended_tracks]
        return recommended_music_names, recommended_music_artists, recommended_music_posters
    else:
        # Raising error if song URL is invalid
        raise ValueError("Invalid song URL.")

# Create Spotify Embed URL for a Song
def get_spotify_embed_url(song_id):
    # Constructing embed URL for a given song ID
    return f"https://open.spotify.com/embed/track/{song_id}"


# =============================================================================
    # Streamlit Application Interface
# =============================================================================


# Setting up the Streamlit app's title with centered CSS
st.markdown("<h1 style='text-align: center;'>Music Recommender System</h1>", unsafe_allow_html=True)


# =============================================================================
# Sidebar
# =============================================================================


# Creating an authentication section in the sidebar
st.sidebar.header("Spotify API Authentication")

# Providing instructions for obtaining Spotify API credentials via an expander
with st.sidebar.expander("How to get Spotify API Credentials"):
    st.markdown("""
1. Navigate to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log into your Spotify account, or sign up if you don't have one.
3. After logging in, click on your account name in the top right corner and select 'Dashboard'.
4. Click on 'Create an App'.
5. Fill out the form and submit it.
6. After the app is created, you will see your Client ID and Client Secret.

For a detailed guide visit the [Spotify Developer Documentation](https://developer.spotify.com/documentation/web-api/concepts/apps).
    """, unsafe_allow_html=True)

# Input fields for Client ID and Client Secret
client_id = st.sidebar.text_input("Client ID", "")
client_secret = st.sidebar.text_input("Client Secret", "")

# Authenticating with Spotify API and proceeding only if successful
access_token, auth_message = authenticate_spotify(client_id, client_secret)
if access_token:
    st.sidebar.success(auth_message)

    # Modifying the Spotify client initialization as per the new authentication method
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

else:
    st.sidebar.error(auth_message)


# =============================================================================
# Load Machine Learning Model
# =============================================================================


# Load precomputed music data and similarity matrix from my Python Machine Learning binary files using pickle
music = pickle.load(open('df','rb'))
similarity = pickle.load(open('similarity','rb'))

# Define a string containing custom CSS to modify the layout of tabs to center them
center_css = """
<style>
.css-1f0j5ro {
    justify-content: center;
}
</style>
"""

# Use Streamlit's markdown function to inject the custom CSS into the app's webpage.
# The 'unsafe_allow_html=True' parameter allows HTML tags within the markdown string to be interpreted as HTML.
st.markdown(center_css, unsafe_allow_html=True)


# =============================================================================
# Streamlit Tabs
# =============================================================================

# Define five tabs in a Streamlit application with custom titles and emojis
tab, tab1, tab2, tab3, tab4 = st.tabs(["Double Diamond 💎 ", "Double Diamond 💎💎 ","Radio Recommendation 🎺 ", "Radio Redesign 📻 ", "About Us 🫂"])


# =============================================================================
# Double Diamond 💎
# =============================================================================


# Specifying the context for the code to run within a previously defined tab
with tab:
    # Create a container for grouping related elements together for the first header
    with st.container():
        # Display a large header/title for the section
        st.header('Double Diamond I: Recommendation System')

        # Create a dropdown menu for selecting a song from the available database
        # The list of songs is retrieved from the 'music' DataFrame's 'song' column, ensuring no duplicates with `.unique()`
        selected_song = st.selectbox("Select a song from our local database to get recommendations:", music['song'].unique())

        # Place a button on the page; if clicked, it will trigger recommendation processing
        if st.button('Get Recommendations'):
            # Display a spinner animation with a message while processing the recommendations
            with st.spinner('Getting Recommendations...'):
                # Call a function `recommend` with the selected song to get recommendations
                recommended_music_names, recommended_music_posters = recommend(selected_song)

            # Once processing is done, store the results in Streamlit's session state
            # This is another call to `recommend` function; might be intended for comparison or reinforcing the recommendation
            our_recommended_music_names, our_recommended_music_posters = recommend(selected_song)
            st.session_state['our_recommended_music_names'] = our_recommended_music_names
            st.session_state['our_recommended_music_posters'] = our_recommended_music_posters

            # Display a success message indicating that the recommendations are ready
            st.success('Recommendations are ready! Proceed to the Recommendation page to view the top recommendations')
            # Further instruct the user to go to a specific page (Result page) to see the recommendations
            st.info('Go to the Result page to view the top recommendations')

            # Optionally rerun the app to automatically transition the user to the results page
            st.experimental_rerun()


    # Display a header/title for this section of the application
    st.header('Our ML Model Recommendations')

    # Check if the recommended music names and posters have been stored in the session state
    if 'our_recommended_music_names' in st.session_state and 'our_recommended_music_posters' in st.session_state:
        # If recommendations are available, display them in a grid layout

        # Loop to create two rows of recommendations
        for row in range(2):  # Looping for two rows
            # Each row consists of 5 columns to display recommendations
            cols = st.columns(5)
            # Calculate the starting index of recommendations for the current row
            start_index = row * 5

            # Loop over each column in the current row
            for i, col in enumerate(cols):
                # Calculate the overall index of the current recommendation
                index = start_index + i
                # Check if the current index is within the bounds of the recommendation list
                if index < len(st.session_state['our_recommended_music_names']):
                    # For each recommendation, display the song name
                    col.text(st.session_state['our_recommended_music_names'][index])
                    # And display the associated image (poster)
                    col.image(st.session_state['our_recommended_music_posters'][index])
    else:
        # If recommendations are not yet available, provide clear instructions for the user to follow
        st.error('Please go to the Double Diamond 💎 tab, select a song from the provided list, and click on Get Recommendations.')


# =============================================================================
# Double Diamond 💎💎
# =============================================================================


with tab1:
    # Container for organizing related elements under a second header
    with st.container():
        st.header('Double Diamond II: Recommendation System')

        # Use an expander to provide detailed instructions on how to find a Spotify Playlist URL
        with st.expander("🎵 How to Find Any Playlist URL in Spotify", expanded=True):
            st.markdown("""
            **Follow these steps to easily find and copy any Spotify Playlist URL:**

            1. **Search for the song** you're interested in on the Spotify app.
            2. **Right-click on the song** you'd like to share or explore.
            3. From the context menu, select **"Share"**.
            4. Click on **"Copy Song Link"** to copy the songs's URL to your clipboard.

            Now, you're ready to paste the URL below and explore!
            """)

            # Display an image with visual instructions or examples if needed
            st.image('Playlist.jpg')

        # Input field for the user to enter the Spotify song URL
        song_url = st.text_input('Enter your Spotify song URL here:')




        # Button to trigger the recommendation process
        if st.button('Get Recommendations Songs'):
            # Proceed only if the user is successfully authenticated with Spotify (access_token exists)
            if access_token:
                # Show a loading message while fetching recommendations
                with st.spinner('Getting Recommendations...'):
                    try:
                        # Attempt to extract the song ID from the provided Spotify song URL
                        song_id = get_song_id_from_url(song_url)
                        if song_id:  # Check if a valid song ID was extracted
                            # Embed the Spotify widget for the song in the app using an iframe
                            song_embed_url = get_spotify_embed_url(song_id)
                            st.markdown(f'<iframe src="{song_embed_url}" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius: 15px;"></iframe>', unsafe_allow_html=True)

                            # Fetch song recommendations based on the extracted song ID using Spotify's API
                            recommended_music_names, recommended_music_artists, recommended_music_posters = get_spotify_recommendations(song_url, sp)

                            # Store the fetched recommendations in Streamlit's session state for later access
                            st.session_state['spotify_recommended_music_names'] = recommended_music_names
                            st.session_state['spotify_recommended_music_artists'] = recommended_music_artists
                            st.session_state['spotify_recommended_music_posters'] = recommended_music_posters

                            # For playlist creation, store the URIs of recommended tracks separately in the session state
                            recommended_track_uris = [track['uri'] for track in sp.recommendations(seed_tracks=[song_id], limit=15)['tracks']]
                            st.session_state['spotify_recommended_track_uris'] = recommended_track_uris

                            # Display a success message along with clear next steps for the user after successfully generating recommendations
                            st.success('Your music recommendations are now ready for viewing! Please navigate to the "Radio Recommendations" section to explore your personalized music suggestions.')

                            # Handle different error scenarios with more specific guidance

                            # In case the Spotify URL provided is invalid
                        else:
                            st.error('The Spotify URL entered appears to be invalid. Ensure it’s correctly copied from Spotify and try submitting it again.')

                            # Catch and display errors related to value exceptions, such as issues with fetching data based on the URL
                    except ValueError as e:
                        st.error(f'Error encountered: {str(e)}. Please ensure the information is correct and try again.')

                            # Inform the user about the necessity of Spotify authentication before proceeding
            else:
                st.error('Authentication with Spotify is required to proceed. Please authenticate to unlock personalized music recommendations.')


# =============================================================================
# Radio Recommendation 🎺
# =============================================================================


with tab2:
    # Setting the header for the recommendations section
    st.header('Personalized Spotify Song Recommendations')

    # Check if there are any song recommendations stored in the session state
    if 'spotify_recommended_music_names' in st.session_state and 'spotify_recommended_music_posters' in st.session_state and 'spotify_recommended_track_uris' in st.session_state:
        # Iterate over each recommended song to display it
        for index in range(len(st.session_state['spotify_recommended_music_names'])):
            # Creating a layout with a single column to display the Spotify Web Playback Widget for each recommended song
            col = st.columns([1])[0]  # st.columns returns a list, but we only need the first column here

            # Extracting the URI for the current song to construct the embed URL for the Spotify widget
            track_uri = st.session_state['spotify_recommended_track_uris'][index]
            embed_url = f"https://open.spotify.com/embed/track/{track_uri.split(':')[2]}"

            # Embedding the Spotify Web Playback Widget using HTML iframe with rounded corners for aesthetics
            col.markdown(f"<iframe src='{embed_url}' width='100%' height='80' frameborder='0' allowtransparency='true' allow='encrypted-media' style='border-radius:15px;'></iframe>", unsafe_allow_html=True)
    else:
        # If there are no recommendations, instruct the user to start the recommendation process
        st.error('To view personalized song recommendations, please enter a Spotify song URL above and click to load the song.')


# =============================================================================
# Spotify Radio Redesign 📻
# =============================================================================


with tab3:
    st.header('Redesign Spotify Recommendation System')

    # Create a row of two columns for the Figma iframe and the text, without an explicit spacer
    col1, col2 = st.columns(2)

    # Embed the Figma design in the first column (col1)
    figma_embed_code = '''
    <iframe style="border: none; height: 690px; width: 100%; margin-right: 20px;
                  transform: scale(1) translate(0px, 0px); overflow: hidden;"
            src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Fproto%2FMUQ4LgVpNzi8hjL16qpw1C%2FMinor%3Fkind%3Dproto%26node-id%3D270-5411%26page-id%3D4%253A2%26scaling%3Dscale-down%26starting-point-node-id%3D270%253A5411%26t%3DAcEGxZXFjAyxLvZc-1%26type%3Ddesign%26mode%3Ddesign"
            allowfullscreen>
    </iframe>
    '''
    col1.markdown(figma_embed_code, unsafe_allow_html=True)

    # New introductory text with three paragraphs
    intro_text_part1 = "In this second design block, I have chosen the Spotify Radio as a UX Design project through the double-diamond design process. As stated in the assignment, we will go over each phase twice to find out how a data-data driven interactive product can be improved with the use of machine learning."
    intro_text_part2 = "In these four weeks, I have worked with my group on user/expert interviews, desk research, POV problem statements, the HMW questions, Persona’s, Empathy Map, Sketching and finally creating High-Fidelity Prototype of the redesign."
    intro_text_part3 = "We as a group are going to explain the goal of redesigning Spotify Radio Recommendation system to improve user satisfaction and engagement through personalized experiences and with the use of Machine Learning algorithms."

    # Display the introductory text in the column with padding at the top for spacing between paragraphs
    col2.markdown(f"<div style='padding-top: 0px;'>{intro_text_part1}</div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='padding-top: 20px;'>{intro_text_part2}</div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='padding-top: 20px;'>{intro_text_part3}</div>", unsafe_allow_html=True)

    # Original text parts and display code follows, with added padding at the top for the first part to ensure consistent spacing

    # First part of the original text
    text_part = "Restaurant owners want us to upgrade the Spotify Radio Recommendation System because their aim is to establish a unique brand identity so that they can provide an unforgettable and distinct dining experience. Therefore, we were tasked with redesigning the Spotify Radio Recommendation System for restaurant owners to help them attract more guests and be THE place to go"

    # Display the first part of the original text in the column with left padding and additional top padding for spacing from the introductory text
    col2.markdown(f"<div style='padding-left: 0px; padding-top: 20px;'>{text_part}.</div>", unsafe_allow_html=True)


# =============================================================================
# About Us 🫂
# =============================================================================

with tab4:
    st.header('Welcome to our Streamlit Application!')

    st.markdown('''
    This project is a collaboration between two enthusiastic students who share a passion for technology, design, and music. We are proud to present an application that combines our skills and interests, offering a unique experience to our users.
    ''')

    st.header('About Us')

    # Adjusting the layout for Singh AmanDeep Saini
    col1, col2 = st.columns([1, 2.8])  # To Adjust the ratio to give more space to the text
    with col1:
        st.image('Aman.png', width=175)  # To adjust the width as needed
    with col2:
        st.markdown('''
        **AmanDeep Singh**: is a final-year Data Scientist student at Fontys University of Applied Sciences. Currently pursuing a minor in Big Data & Design. Aman has a solid foundation in AI combined with an enthusiasm for exploring the vast potentials of data analysis and design. Taking on the challenge, A has played a pivotal role in developing the core functionality of a Streamlit application, showcasing his ability to navigate complex data landscapes and integrate innovative solutions into practical applications.
        ''')

    # Space or separator between the two sections
    st.markdown(' ')

    # Adjusting the layout for Giulia Vitali
    col3, col4 = st.columns([1, 2.8])  # To Adjust the ratio to give more space to the text
    with col3:
        st.image('Giulia.png', width=175)  # To adjust the width as needed
    with col4:
        st.markdown('''
        **Giulia Vitali**: is a third-year Creative Business student at HU University of Applied Sciences Utrecht. Her academic journey is distinguished by a focused engagement in the minor program of Big Data & Design. Combining her creative instincts with a strategic business approach, Giulia embarked on a mission to redesign a Spotify Radio Recommendation System using Figma. Her goal was to enhance the user experience by making the system more intuitive in both design and functionality.
        ''')

    # Collaboration Highlight

    st.header('Collaboration')

    st.markdown('''
    Working together on this project has been an enlightening experience. Despite coming from different academic backgrounds, our shared vision for the application led to a productive and harmonious collaboration. We are proud of what we have accomplished as a team and are excited to share it with the world.
    ''')

    st.header('Special Thanks')

    # Special Thanks
    st.markdown('''

    We owe a debt of gratitude to the GitHub community for the resources and inspiration that significantly contributed to our project:
    1. [Madhav Thaker's Spotify Recommendation System](https://github.com/madhavthaker/spotify-recommendation-system)
    2. [Anthony Li's Spotify Recommender Systems](https://github.com/anthonyli358/spotify-recommender-systems)
    3. [Abdelrhman Elruby's Spotify Recommendation System](https://github.com/abdelrhmanelruby/Spotify-Recommendation-System)

    These repositories were instrumental in guiding our development process and provided a solid foundation for our application.
    ''')

    st.success('''
    Thank you for visiting our application. We hope you enjoy exploring it as much as we enjoyed creating it.
    ''')
