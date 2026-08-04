# generate_videos.py
# İngilizce TTS + altyazı (offline) içeren video jeneratörü
# Gereksinimler:
# - FFmpeg PATH'te olmalı
# - Python 3.9+
# - pip install moviepy pillow numpy pyttsx3 scipy

import os
import re
import random
import argparse
import time
import tempfile
from pathlib import Path
from moviepy.editor import (
    VideoClip, ImageClip, CompositeVideoClip, AudioFileClip, TextClip
)
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageDraw
import numpy as np
import pyttsx3

# --- Konfigürasyon ---
WIDTH, HEIGHT = 1080, 1920  # 9:16
FPS = 30
BG_COLORS = ["#0f172a", "#042f66", "#061e3a", "#7c3aed", "#06b6d4"]

TEMPLATES = [
    ("Car racing", "Basketball"),
    ("Motorcycle racing", "Running"),
    ("Rally", "Tennis"),
    ("Formula 1", "Swimming"),
    ("Drag race", "Athletics (100m)"),
    ("MotoGP", "Gymnastics"),
    ("Enduro (motor)", "Mountain biking"),
    ("Karting", "Weight training"),
    ("Endurance motor", "Triathlon"),
    ("Drift", "Football")
]

# --- Yardımcı fonksiyonlar ---

def ensure_dirs(root):
    Path(root).mkdir(parents=True, exist_ok=True)
    Path(root, "assets").mkdir(parents=True, exist_ok=True)
    Path(root, "outputs").mkdir(parents=True, exist_ok=True)


def choose_english_voice(engine):
    voices = engine.getProperty('voices')
    # Try to find one with 'en' or 'English' in attributes
    for v in voices:
        name = (v.name or '').lower()
        id_ = (v.id or '').lower()
        langs = ''
        try:
            langs = ''.join([str(x).lower() for x in getattr(v, 'languages', [])])
        except Exception:
            langs = ''
        if 'en' in name or 'english' in name or 'en' in id_ or 'en' in langs:
            return v.id
    # fallback to first
    if voices:
        return voices[0].id
    return None


def make_tts_sentences(sentences, out_dir):
    # returns list of (path, duration)
    paths = []
    for idx, sent in enumerate(sentences):
        out_wav = os.path.join(out_dir, f"tts_{idx+1}.wav")
        engine = pyttsx3.init()
        # pick english voice if available
        v = choose_english_voice(engine)
        if v:
            try:
                engine.setProperty('voice', v)
            except Exception:
                pass
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.save_to_file(sent, out_wav)
        engine.runAndWait()
        engine.stop()
        # compute duration via moviepy AudioFileClip
        try:
            clip = AudioFileClip(out_wav)
            duration = clip.duration
            clip.close()
        except Exception:
            duration = max(0.5, len(sent.split())/2.5)
        paths.append((out_wav, duration))
    return paths


def synth_simple_music(duration, fps=44100, freq=220.0):
    t = np.linspace(0, duration, int(fps*duration), endpoint=False)
    wave = 0.4*np.sin(2*np.pi*freq*t) + 0.2*np.sin(2*np.pi*(freq*2)*t)
    fade = np.linspace(0,1,len(wave))
    fade_out = np.linspace(1,0,len(wave))
    env = np.minimum(fade, fade_out)
    wave = wave * env
    return (wave).astype(np.float32)


def pil_draw_vehicle(kind="car", size=(200,100), color="#ff0000"):
    w,h = size
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    if kind == "car":
        draw.rounded_rectangle([0, h*0.25, w, h*0.75], radius=20, fill=color)
        wheel_r = int(h*0.18)
        draw.ellipse([w*0.12-wheel_r, h*0.75-wheel_r, w*0.12+wheel_r, h*0.75+wheel_r], fill="black")
        draw.ellipse([w*0.88-wheel_r, h*0.75-wheel_r, w*0.88+wheel_r, h*0.75+wheel_r], fill="black")
    elif kind == "bike":
        draw.line([(0,h*0.6),(w*0.4,h*0.3),(w*0.7,h*0.5),(w,h*0.4)], fill=color, width=8)
        wheel_r = int(h*0.2)
        draw.ellipse([0, h*0.6, wheel_r*2, h*0.6+wheel_r*2], fill="black")
        draw.ellipse([w-wheel_r*2, h*0.5, w, h*0.5+wheel_r*2], fill="black")
    elif kind == "runner":
        draw.ellipse([w*0.4,0,w*0.6,w*0.2], fill=color)
        draw.line([(w*0.5,w*0.2),(w*0.5,w*0.55)], fill=color, width=8)
        draw.line([(w*0.5,w*0.3),(w*0.7,w*0.45)], fill=color, width=8)
        draw.line([(w*0.5,w*0.55),(w*0.65,w*0.95)], fill=color, width=8)
    return img


def create_video_for_pair(pair_title, out_path, length=30):
    left, right = pair_title
    tmpdir = tempfile.mkdtemp(prefix="genvid_")

    # narration: split into sentences for timing + subtitles
    intro = f"This is a comparison between {left} and {right}."
    bullets = [
        f"{left} often emphasize speed and engine power.",
        f"{right} rely more on agility, technique, and human skill.",
        "Which sport is more exciting depends on personal preference.",
        "If time is short, speed has the edge; if technique matters, skill wins."
    ]
    narration_sentences = [intro] + bullets

    # TTS per sentence -> get per-sentence durations
    tts_data = make_tts_sentences(narration_sentences, tmpdir)

    # build audio clips with start times
    audio_clips = []
    subs = []
    current = 0.0
    for (wav_path, dur), sent in zip(tts_data, narration_sentences):
        try:
            aclip = AudioFileClip(wav_path).set_start(current)
            audio_clips.append(aclip)
        except Exception:
            pass
        start = current
        end = current + dur
        subs.append(((start, end), sent))
        current = end

    # optional background music generated (if scipy / write not available, skip)
    music_clip = None
    try:
        from scipy.io.wavfile import write
        music_wav = os.path.join(tmpdir, "music.wav")
        samples = synth_simple_music(length, freq=160.0)
        arr = np.int16(samples/np.max(np.abs(samples)) * 32767)
        write(music_wav, 44100, arr)
        music_clip = AudioFileClip(music_wav).volumex(0.18).set_start(0)
        audio_clips.append(music_clip)
    except Exception:
        pass

    if audio_clips:
        composite_audio = CompositeAudioClip(audio_clips).set_duration(length)
    else:
        composite_audio = None

    # Visual assets
    car_img = pil_draw_vehicle("car", size=(280,140), color="#ff4d4d")
    bike_img = pil_draw_vehicle("bike", size=(240,120), color="#4dd0ff")
    runner_img = pil_draw_vehicle("runner", size=(160,320), color="#ffd24d")
    car_path = os.path.join(tmpdir, "car.png"); car_img.save(car_path)
    bike_path = os.path.join(tmpdir, "bike.png"); bike_img.save(bike_path)
    run_path = os.path.join(tmpdir, "run.png"); runner_img.save(run_path)

    bg_color = random.choice(BG_COLORS)

    def make_bg_frame(t):
        arr = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        hexc = bg_color.lstrip('#')
        r = int(hexc[0:2],16); g = int(hexc[2:4],16); b = int(hexc[4:6],16)
        arr[:,:,:] = [r,g,b]
        return arr

    bg_clip = VideoClip(make_bg_frame, duration=length).set_fps(FPS)

    car_clip = ImageClip(car_path).set_duration(length).resize(height=200)
    bike_clip = ImageClip(bike_path).set_duration(length).resize(height=160)
    run_clip = ImageClip(run_path).set_duration(length).resize(height=420)

    def pos_car(t):
        x = int(WIDTH - (WIDTH + car_clip.w) * (t/length))
        y = int(HEIGHT*0.55)
        return (x,y)
    def pos_bike(t):
        x = int(WIDTH - (WIDTH + bike_clip.w) * ((t/length)*0.9 + 0.05))
        y = int(HEIGHT*0.35)
        return (x,y)
    def pos_runner(t):
        x = int(WIDTH - (WIDTH + run_clip.w) * ((t/length)*0.6 + 0.2))
        y = int(HEIGHT*0.7)
        return (x,y)

    car_clip = car_clip.set_pos(pos_car)
    bike_clip = bike_clip.set_pos(pos_bike)
    run_clip = run_clip.set_pos(pos_runner)

    title_txt = f"{left} vs {right}"
    title = TextClip(title_txt, fontsize=90, color='white', font='Arial-Bold').set_position(('center', 80)).set_duration(length)

    # subtitles: use SubtitlesClip with generated timings
    def txt_generator(txt):
        return TextClip(txt, fontsize=56, color='white', font='Arial', method='caption', size=(int(WIDTH*0.9), None))

    try:
        subclip = SubtitlesClip(subs, txt_generator).set_position(('center', HEIGHT-260)).set_duration(length)
    except Exception:
        # fallback: single big caption
        subclip = TextClip(" ".join([s for s in narration_sentences]), fontsize=48, color='white', font='Arial', method='caption', size=(int(WIDTH*0.9), None)).set_position(('center', HEIGHT-260)).set_duration(length)

    clips = [bg_clip, car_clip, bike_clip, run_clip, title, subclip]
    final = CompositeVideoClip(clips, size=(WIDTH, HEIGHT)).set_duration(length)
    if composite_audio:
        final = final.set_audio(composite_audio)

    # export (note: may be slow)
    final.write_videofile(out_path, fps=FPS, codec='libx264', audio_codec='aac', threads=4, preset='medium', ffmpeg_params=['-profile:v','baseline','-level','3.0'])
    print("Saved:", out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10, help="How many videos to create")
    parser.add_argument("--length", type=int, default=30, help="Video length in seconds")
    parser.add_argument("--outdir", type=str, default="outputs", help="Output directory")
    args = parser.parse_args()

    root = os.getcwd()
    ensure_dirs(root)
    outdir = Path(root) / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    for i in range(args.count):
        pair = TEMPLATES[i % len(TEMPLATES)]
        timestamp = int(time.time())
        safe_left = pair[0].replace(' ', '_')
        safe_right = pair[1].replace(' ', '_')
        fname = f"short_{i+1}_{safe_left}_vs_{safe_right}_{timestamp}.mp4"
        out_path = str(outdir / fname)
        print(f"[{i+1}/{args.count}] Generating: {pair[0]} vs {pair[1]} -> {out_path}")
        try:
            create_video_for_pair(pair, out_path, length=args.length)
        except Exception as e:
            print("Error while generating:", e)

if __name__ == "__main__":
    main()
