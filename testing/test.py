import tkinter as tk
from pytube import YouTube
import vlc

def play_youtube_video():
    url = entry.get()
    yt = YouTube(url)
    video_url = yt.streams.filter(progressive=True, file_extension='mp4').first().url
    player.set_mrl(video_url)
    player.play()

root = tk.Tk()
root.title("YouTube Video Player")

entry = tk.Entry(root, width=50)
entry.pack(pady=10)

play_button = tk.Button(root, text="Play", command=play_youtube_video)
play_button.pack(pady=5)

player = vlc.MediaPlayer()
player_container = tk.Frame(root)
player_container.pack(pady=10)
player.set_hwnd(player_container.winfo_id())

root.mainloop()