# importing packages
from pytube import YouTube
import os

def grab_mp3(url):
    
    yt = YouTube(url)
    video = yt.streams.get_audio_only()
    
    if video is None:
        return "Error: No video found."
    else:
        out_file = video.download(output_path='.', max_retries=3)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
    
        try:
            os.rename(out_file, new_file)
        except FileExistsError:
            os.remove(new_file)
            os.rename(out_file, new_file)
        finally:
            return new_file

