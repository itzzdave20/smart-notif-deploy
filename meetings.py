import streamlit as st
import urllib.parse
from datetime import datetime

def sanitize_room_name(name: str) -> str:
    base = name.strip().replace(' ', '-')
    return ''.join(ch for ch in base if ch.isalnum() or ch in ['-', '_'])[:64] or 'SmartRoom'

def jitsi_url(room_name: str) -> str:
    room = sanitize_room_name(room_name)
    return f"https://meet.jit.si/{urllib.parse.quote(room)}"

def render_meeting(room_name: str, height: int = 720):
    url = jitsi_url(room_name)
    st.components.v1.iframe(src=url, height=height)

def suggest_room_for_user(username: str) -> str:
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"{sanitize_room_name(username)}-{timestamp}"

