import os
import shutil
import glob
import pathlib
import yt_dlp
from pydub import AudioSegment

# ------------------------------------------------------------------
# File Paths & Directories Configuration
# ------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, "downloads")

# Automatically create required directories
for folder in ["downloads", "cache", "transcripts", "outputs", "temp"]:
    os.makedirs(os.path.join(PROJECT_ROOT, folder), exist_ok=True)

# ------------------------------------------------------------------
# FFmpeg Dynamic Locator
# ------------------------------------------------------------------
def find_ffmpeg() -> str:
    """
    Locates ffmpeg.exe dynamically on the system.
    Checks PATH, Winget, Scoop, Chocolatey, and common installation folders.
    Returns the path to the ffmpeg executable, or None if not found.
    """
    # 1. Check PATH
    path_ffmpeg = shutil.which("ffmpeg")
    if path_ffmpeg:
        return path_ffmpeg

    # 2. Check LOCALAPPDATA (Winget)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_pattern = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages", "**", "ffmpeg.exe")
        winget_paths = glob.glob(winget_pattern, recursive=True)
        if winget_paths:
            # Prefer full builds if multiple are found
            for p in winget_paths:
                if "full_build" in p:
                    return p
            return winget_paths[0]

    # 3. Check USERPROFILE (Scoop)
    user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    if user_profile:
        scoop_path = os.path.join(user_profile, "scoop", "shims", "ffmpeg.exe")
        if os.path.exists(scoop_path):
            return scoop_path

    # 4. Check Chocolatey
    choco_path = r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
    if os.path.exists(choco_path):
        return choco_path

    # 5. Check common installation directories
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p

    # 6. Check project root
    local_proj_ffmpeg = os.path.join(PROJECT_ROOT, "ffmpeg.exe")
    if os.path.exists(local_proj_ffmpeg):
        return local_proj_ffmpeg

    return None

# Configure ffmpeg for pydub and environment PATH
FFMPEG_EXE = find_ffmpeg()
if FFMPEG_EXE:
    FFMPEG_DIR = os.path.dirname(FFMPEG_EXE)
    AudioSegment.converter = FFMPEG_EXE
    # Add containing folder to PATH so subprocesses (like yt-dlp) can find it
    if FFMPEG_DIR not in os.environ.get("PATH", ""):
        os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
else:
    print("Warning: FFmpeg executable could not be found. Please ensure FFmpeg is installed.")

def download_youtube_audio(url: str) -> str:
    """Download audio from YouTube and return the generated WAV path."""
    if not FFMPEG_EXE:
        raise RuntimeError(
            "Couldn't find ffmpeg. Please install FFmpeg (e.g. run 'winget install Gyan.FFmpeg') "
            "and ensure it is in your system PATH or installed via Winget."
        )

    output_tmpl = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_tmpl,
        "ffmpeg_location": os.path.dirname(FFMPEG_EXE),
        "restrictfilenames": True, # Ensure safe Windows paths with ASCII characters
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }

    print(f"Downloading YouTube audio from URL: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as e:
            raise RuntimeError(f"Failed to download YouTube audio. The video might be private, age-restricted, or unavailable. Error: {e}")
            
        if 'requested_downloads' in info and len(info['requested_downloads']) > 0:
            filename = info['requested_downloads'][0]['filepath']
        else:
            filename = ydl.prepare_filename(info)
            root, ext = os.path.splitext(filename)
            filename = root + ".wav"

    if not os.path.exists(filename):
        raise FileNotFoundError(f"YouTube download output file not found: {filename}")
        
    if os.path.getsize(filename) == 0:
        raise ValueError(f"YouTube download succeeded but produced an empty file: {filename}")

    return filename

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to 16 kHz mono WAV format."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file for conversion does not exist: {input_path}")

    if not FFMPEG_EXE:
        raise RuntimeError(
            "Couldn't find ffmpeg. Please install FFmpeg (e.g. run 'winget install Gyan.FFmpeg') "
            "and ensure it is in your system PATH or installed via Winget."
        )

    # Put converted WAV in the downloads folder
    base_name = os.path.basename(input_path)
    clean_base = os.path.splitext(base_name)[0]
    # Replace spaces and special characters for Windows compatibility
    clean_base = "".join(c if c.isalnum() or c in "._-" else "_" for c in clean_base)
    output_path = os.path.join(DOWNLOAD_DIR, f"{clean_base}_converted.wav")

    print(f"Converting file {input_path} to 16kHz mono WAV...")
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio.export(output_path, format="wav")
    except Exception as e:
        raise RuntimeError(f"Failed to convert file {input_path} to WAV. Error: {e}")

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Converted file was not generated: {output_path}")

    if os.path.getsize(output_path) == 0:
        raise ValueError(f"Audio conversion resulted in an empty file: {output_path}")

    return output_path

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Chunk the WAV audio file into smaller pieces to stay within Whisper/Sarvam API limits."""
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Audio chunking source file does not exist: {wav_path}")

    if not FFMPEG_EXE:
        raise RuntimeError(
            "Couldn't find ffmpeg. Please install FFmpeg (e.g. run 'winget install Gyan.FFmpeg') "
            "and ensure it is in your system PATH or installed via Winget."
        )

    print(f"Loading {wav_path} for chunking...")
    try:
        audio = AudioSegment.from_wav(wav_path)
    except Exception as e:
        # Fallback to general from_file if from_wav fails
        try:
            audio = AudioSegment.from_file(wav_path)
        except Exception:
            raise RuntimeError(f"Failed to read WAV file for chunking: {e}")

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        
        if not os.path.exists(chunk_path) or os.path.getsize(chunk_path) == 0:
            raise FileNotFoundError(f"Failed to export chunk file: {chunk_path}")
            
        chunks.append(chunk_path)

    return chunks

def process_input(source: str) -> list:
    """Main pipeline entry for audio/video input sources."""
    # Trim and normalize file path strings
    source = source.strip().strip('"').strip("'")
    
    if source.startswith(("http://", "https://")):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        # Resolve path absolutely relative to CWD if relative, otherwise keep absolute
        source_path = os.path.abspath(source)
        print(f"Detected local file path: {source_path}. Converting to WAV...")
        wav_path = convert_to_wav(source_path)

    print(f"Converting/Validating output WAV file to 16 kHz mono WAV format...")
    # Force 16 kHz mono conversion on download_youtube_audio output too, just in case
    if not wav_path.endswith("_converted.wav"):
        wav_path = convert_to_wav(wav_path)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks