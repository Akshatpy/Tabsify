import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import librosa
import numpy as np
from bs4 import BeautifulSoup
import yt_dlp
import os
from selenium import webdriver
GUITAR_TABS = {
    'E2': '6/0', 'F2': '6/1', 'F#2': '6/2', 'G2': '6/3', 'G#2': '6/4',
    'A2': '5/0', 'A#2': '5/1', 'B2': '5/2', 'C3': '5/3', 'C#3': '5/4',
    'D3': '4/0', 'D#3': '4/1', 'E3': '4/2', 'F3': '4/3', 'F#3': '4/4',
    'G3': '3/0', 'G#3': '3/1', 'A3': '3/2', 'A#3': '3/3', 'B3': '2/0',
    'C4': '2/1', 'C#4': '2/2', 'D4': '2/3', 'D#4': '2/4', 'E4': '1/0',
    'F4': '1/1', 'F#4': '1/2', 'G4': '1/3'
}
def search_youtube(query):
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get('https://www.youtube.com/results?search_query={}'.format(query))
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, 'html.parser')
    video_urls = soup.findAll('a', id='video-title')
    if not video_urls:
        return None
    video_url = 'https://www.youtube.com{}'.format(video_urls[0].get('href'))
    return video_url

def download_as_mp3(youtube_url, output_filename, ffmpeg_path=r'C:\ffmpeg-7.0.2-essentials_build\bin'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_filename}.mp3',
        'postprocessor_args': ['-ar', '44100'],
        'prefer_ffmpeg': True,
        'nocheckcertificate': True,
    }

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    notes = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            note = get_note_name(pitch)
            if note in GUITAR_TABS:
                notes.append(GUITAR_TABS[note])
    return notes
def get_note_name(frequency):
    A4 = 440.0
    half_steps = int(round(12 * np.log2(frequency / A4)))
    note_index = (half_steps + 9) % 12
    note_names = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    octave = (half_steps + 9) // 12 + 4
    return f"{note_names[note_index]}{octave}"

def generate_tab_string(tabs):
    strings = ['E', 'B', 'G', 'D', 'A', 'E']
    tab_lines = {s: ['-'] * 30 for s in strings}

    for tab in tabs:
        string, fret = map(int, tab.split('/'))
        string_idx = 6 - string
        tab_lines[strings[string_idx]][fret] = str(fret)
    tab_display = []
    for s in strings:
        tab_display.append(s + '|' + ''.join(tab_lines[s]))

    return "\n".join(tab_display)

def display_tabs(tabs):
    tab_string = generate_tab_string(tabs)
    messagebox.showinfo("Guitar Tabs", tab_string if tabs else "No recognizable guitar tabs detected.")
def view_dir():
    files = [file for file in os.listdir('./') if file.endswith('.mp3')]
    if files:
        file_text = "\n".join(files)
    else:
        file_text = "No songs found."
    messagebox.showinfo("Available Songs", file_text)
def del_song():
    view_dir()
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        if os.path.exists(file_path):
            os.remove(file_path)
            messagebox.showinfo("Delete Song", "Deleted successfully.")
        else:
            messagebox.showwarning("Delete Song", "SONG NOT IN DIRECTORY")

def view_tabs_of_existing_song():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        print("Analyzing")
        notes = analyze_audio(file_path)
        display_tabs(notes)
def view_downloaded_songs():
    view_dir()
def search_for_new_song():
    song_name = simpledialog.askstring("Input", "Enter the name of the song:")
    if song_name:
        search_query = f"{song_name} piano instrumental"
        youtube_url = search_youtube(search_query)
        if youtube_url:
            download_as_mp3(youtube_url, song_name)
            messagebox.showinfo("Download", f"Download completed: {song_name}.mp3")
            inp2 = messagebox.askquestion("Guitar Tabs", f"Do you want to view tabs for {song_name}?")
            if inp2 == 'yes':
                notes = analyze_audio(song_name + ".mp3"+".mp3")
                display_tabs(notes)
        else:
            messagebox.showwarning("Download", "Instrumental version not found. Try another song.")

def delete_song():
    del_song()

def quit_app():
    root.quit()
root = tk.Tk()
root.title("Tabify")
root.geometry("300x250")
button1 = tk.Button(root, text="View Downloaded Songs", command=view_downloaded_songs)
button1.pack(pady=10)
button2 = tk.Button(root, text="Search for New Song", command=search_for_new_song)
button2.pack(pady=10)
button3 = tk.Button(root, text="Delete a Song", command=delete_song)
button3.pack(pady=10)
button4 = tk.Button(root, text="View Tabs of Existing Song", command=view_tabs_of_existing_song)
button4.pack(pady=10)
button5 = tk.Button(root, text="Quit", command=quit_app)
button5.pack(pady=10)
root.mainloop()
