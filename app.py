import streamlit as st
import openai
import os
import scipy.io.wavfile
from transformers import pipeline
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

open_AI_key = os.environ.get('OPENAI_API_KEY')
spotify_client = os.environ.get('spotify_client')
spotify_secret = os.environ.get('spotify_secret')

# Function to extract mood from text using OpenAI
def extract_mood(user_input):
    openai.api_key = open_AI_key

    try:
        # Adjust the prompt to suggest a mood keyword based on user input
        prompt = (
            "Based on the following user input, suggest a single mood keyword for a Spotify song. "
            "If the input suggests a negative or tired mood, suggest a mood that's uplifting or energizing. "
            "If the input is positive, suggest a mood that maintains the positivity:\n\n"
            f"{user_input}"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=5
        )
        mood = response.choices[0].text.strip().lower()
        return mood
    except Exception as e:
        st.error("Error in OpenAI API call for mood extraction: " + str(e))
        return 'neutral'  # Default mood if there's an error

# Function to get Spotify song suggestion
def get_spotify_song(mood):
    spotify_client_id = spotify_client
    spotify_client_secret = spotify_secret
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q=mood, limit=1, type='track')
    track = results['tracks']['items'][0] if results['tracks']['items'] else None

    if track:
        track_url = track['external_urls']['spotify']
        track_name = track['name']
        st.write(f"Suggested Song: [{track_name}]({track_url})")
        st.markdown(f"<iframe src='https://open.spotify.com/embed/track/{track['id']}' width='300' height='380' frameborder='0' allowtransparency='true' allow='encrypted-media'></iframe>", unsafe_allow_html=True)

        # Add like and dislike buttons
        if st.button("Like"):
            st.write(f"You liked the song: {track_name}")
        if st.button("Dislike"):
            st.write(f"You disliked the song: {track_name}")

    else:
        st.write("No song found for the given mood")

# Function to generate a new song
def generate_new_song(user_input):
    openai.api_key = open_AI_key

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=(
                "Generate a text based on what this person's activity shows. "
                "If it has a negative implication, suggest a positive statement "
                "to help and encourage them to recover from the negative situation"
                f"Response: {user_input}"
            ),
            max_tokens=50
        )
        result_text = response.choices[0].text.strip()
    except Exception as e:
        st.error("Error in OpenAI API call: " + str(e))
        return

    synthesiser = pipeline("text-to-audio", "facebook/musicgen-small")

    try:
        music = synthesiser(result_text, forward_params={"do_sample": True, "max_length": 100, "min_length": 50})
        scipy.io.wavfile.write("musicgen_out.wav", rate=music["sampling_rate"], data=music["audio"])
        st.audio("musicgen_out.wav", format='audio/wav')

        # Add like and dislike buttons
        if st.button("Like"):
            st.write("You liked the generated song!")
        if st.button("Dislike"):
            st.write("You disliked the generated song!")

    except Exception as e:
        st.error("Error in audio generation: " + str(e))

# Streamlit App main function
def main():
    st.title("Bruce Almighty - Fitness Activity Audio Generator")

    # User Inputs
    # ... activity input fields ...

    st.subheader("Activity Information")
    activity_date = st.text_input("Activity Date", value='2023-10-29')
    start_time = st.text_input("Start Time", value='12:00:00')
    end_time = st.text_input("End Time", value='12:10:00')
    activity_type = st.text_input("Type", value='Walking')
    duration = st.text_input("Duration (seconds)", value='600')
    distance = st.text_input("Distance (meters)", value='300')
    calories_burned = st.text_input("Calories Burned", value='20')
    avg_heart_rate = st.text_input("Average Heart Rate", value='80')
    peak_heart_rate = st.text_input("Peak Heart Rate", value='90')
    steps = st.text_input("Steps", value='400')
    notes = st.text_area("Notes", value='I feel tired and unmotivated.')

    choice = st.selectbox("Choose an option", ["Generate a New Song", "Get a Song Suggestion from Spotify"])

    if st.button("Proceed"):
        user_input = f"""
        Activity Date: {activity_date}
        Start Time: {start_time}
        End Time: {end_time}
        Type: {activity_type}
        Duration: {duration}
        Distance: {distance}
        Calories Burned: {calories_burned}
        Average Heart Rate: {avg_heart_rate}
        Peak Heart Rate: {peak_heart_rate}
        Steps: {steps}
        Notes: {notes}
        """ 

        if choice == "Generate a New Song":
            generate_new_song(user_input)
        elif choice == "Get a Song Suggestion from Spotify":
            mood = extract_mood(user_input)  # Extract mood from the user input
            get_spotify_song(mood)

if __name__ == "__main__":
    main()
