import streamlit as st
import os
import speech_recognition as sr
from googleapiclient.discovery import build
import datetime
import isodate
import google.generativeai as genai 

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_youtube_videos(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=14)).isoformat("T") + "Z"
    req = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=20,
        publishedAfter=published_after,
        type="video"
    )
    return req.execute()

def filter_videos(data):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    video_ids = [item["id"]["videoId"] for item in data["items"]]
    details = youtube.videos().list(part="contentDetails,snippet", id=",".join(video_ids)).execute()
    filtered = []
    for vid in details["items"]:
        duration = isodate.parse_duration(vid["contentDetails"]["duration"]).total_seconds()
        if 240 <= duration <= 1200:
            filtered.append({
                "title": vid["snippet"]["title"],
                "videoId": vid["id"],
                "duration": duration
            })
    return filtered


def analyze_titles(videos, query):
    titles = [v['title'] for v in videos]
    formatted_titles = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))

    # Initialize Gemini client
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_instruction = """You are an expert YouTube analyst. Your task is to identify the most 
    relevant video title from a list based on a search query. Only return the number of the best 
    title and nothing else."""
    
    prompt = f"""You are an expert YouTube analyst. Your task is to identify the most 
    relevant video title from a list based on a search query. Only return the number of the best 
    title and nothing elseBased on the search query: "{query}", choose the most relevant video title from this list.
    Titles:
    {formatted_titles}
    Only return the number of the best title (e.g., "3").
    """
    
    chat = model.start_chat()
    
    response = chat.send_message(prompt, generation_config={"temperature": 0.2})
    
    try:
        match_number = int(response.text.strip()) - 1
        return titles[match_number], videos[match_number]
    except (ValueError, IndexError):
        return titles[0], videos[0]

def transcribe_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio, language='en-IN')
        except sr.UnknownValueError:
            return "Could not recognize speech"


st.title(" Choice 2: YouTube Video Analyzer")

# Text or Voice Input
query = st.text_input("Enter your search query (or leave blank for voice input)")

if not query:
    audio_button = st.button("Use Voice Input")
    if audio_button:
        query = transcribe_audio()
        st.success(f"Recognized: {query}")

if query:
    st.write("🔍 Searching YouTube...")
    raw_results = search_youtube_videos(query)
    filtered = filter_videos(raw_results)

    if not filtered:
        st.warning("No videos found in the desired range.")
    else:
        st.write(f" Found {len(filtered)} matching videos.")

        st.write(" Analyzing titles ...")
        best_title, best_video = analyze_titles(filtered, query)

        st.success(" Best Video Found:")
        st.markdown(f"**{best_title}**")
        st.video(f"https://www.youtube.com/watch?v={best_video['videoId']}")
