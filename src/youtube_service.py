import yt_dlp
from src.exceptions import StreamExtractionError, VideoNotFoundError

class YoutubeService:
  """Service class responsible for interacting with the yt-dlp library."""
  def __init__(self, ydl_opts: dict | None = None) -> None:
    
    # Default options to silence verbose logs and enable Node.js JS runtime
    default_opts = {
      "quiet": True,
      "no_warnings": True,
      "noplaylist": True,
      "socket_timeout": 10,
      "js_runtimes": {"node": {}},
    }
    
    if ydl_opts:
      default_opts.update(ydl_opts)
      
    self.ydl_opts = default_opts
    
  def get_video_info(self, url: str) -> dict:
    """Extract video info without downloading"""
    try:
      with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)
    
    except yt_dlp.utils.DownloadError as err:  
      error_msg = str(err).lower()
      
      invalid_url_keywords = [ 
        "is not a valid url",
        "incomplete youtube id",
        "video is unavailable",
        "video unavailable",
        "private video",
        "has been removed",
      ]
      
      if any(keyword in error_msg for keyword in invalid_url_keywords):
        raise VideoNotFoundError(
          f"The provided URL is invalid or video does not exist: {url}"
        ) from err 
        
      raise StreamExtractionError(
        f"Failed to extract video information: {err}"
      ) from err
      
    except Exception as err:
      raise StreamExtractionError(
        f"An unexpected error occurred during extraction: {err}"
      ) from err
            
  def get_available_streams(self, url: str) -> dict:
    """Fetch video metadata and return a deduplicated, clean list of video streams by resolution."""
    info = self.get_video_info(url)
    formats = info.get("formats", [])
    best_streams_by_res = {}
    
    for fmt in formats:
      vcodec = fmt.get("vcodec")
      acodec = fmt.get("acodec")
      height = fmt.get("height")
      format_id = fmt.get("format_id")
      ext = fmt.get("ext")
      
      # Ignore explicitly audio-only streams (vcodec is "none" and acodec is present)
      if not vcodec or vcodec == "none":
        continue
        
      # Try to derive height if missing from resolution string (e.g., "640x360" -> 360)
      if not height and fmt.get("resolution"):
        res_str = str(fmt.get("resolution"))
        if "x" in res_str:
          try:
            height = int(res_str.split("x")[1])
          except ValueError:
            pass
        
      # Determine resolution label and dictionary key
      if height:
        resolution_label = (
          f"{height}p ({fmt.get('width', '')}x{height})"
          if fmt.get("width")
          else f"{height}p"
        )
        res_key = height
      else:
        resolution_label = str(
          fmt.get("resolution") or fmt.get("format_note") or "N/A"
        )
        res_key = resolution_label
      
      # Scoring criteria to prioritize MP4 container and AVC1/H264 codec
      score = 0
      if ext == "mp4":
          score += 10
      if vcodec and "avc1" in vcodec:
          score += 20
  
      # Select only the best format per resolution
      if (
        res_key not in best_streams_by_res
        or score > best_streams_by_res[res_key]["score"]
      ):
        best_streams_by_res[res_key] = {
          "score": score,
          "stream": {
            "format_id": format_id,
            "ext": ext,
            "resolution": resolution_label,
            "vcodec": vcodec or "N/A",
            "acodec": fmt.get("acodec") or "none",
          },
        }
        
     # Sort resolutions: numeric heights descending first, then non-numeric keys
    sorted_keys = sorted(
      best_streams_by_res.keys(),
      key=lambda k: (isinstance(k, int), k),
      reverse=True,
    )

    clean_streams = [best_streams_by_res[k]["stream"] for k in sorted_keys]
    
    return {
      "title": info.get("title", "Unknown Title"),
      "streams": clean_streams,
    }
    
  def _execute_download(self, url: str, download_opts: dict, error_prefix: str) -> None:
    """Helper method to run yt_dlp download with standardized exception handling."""
    try:
      with yt_dlp.YoutubeDL(download_opts) as ydl:
          ydl.download([url])
    except yt_dlp.utils.DownloadError as err:
      raise StreamExtractionError(f"{error_prefix}: {err}") from err
    except Exception as err:
      raise StreamExtractionError(
        f"An unexpected error occurred during {error_prefix.lower()}: {err}"
      ) from err

  def download_stream(self, url: str, format_id: str, output_dir: str = "downloads") -> str:
    """Download a specific stream format to the specified directory."""
    download_opts = {
      **self.ydl_opts,
      "format": f"{format_id}+bestaudio[ext=m4a]/bestaudio/best",
      "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
    }
    
    self._execute_download(url, download_opts, f"Failed to download format '{format_id}'")
    return output_dir

  def download_audio(self, url: str, output_dir: str = "downloads") -> str:
    """Download best audio stream and convert it to MP3."""
    download_opts = {
      **self.ydl_opts,
      "format": "bestaudio/best",
      "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
      "postprocessors": [
        {
          "key": "FFmpegExtractAudio",
          "preferredcodec": "mp3",
          "preferredquality": "192",
        }
      ],
    }
    
    self._execute_download(url, download_opts, "Failed to download audio")
    return output_dir
