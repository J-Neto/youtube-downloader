import yt_dlp
from exceptions import StreamExtractionError, VideoNotFoundError

class YoutubeService:
  """Service class responsible for interacting with the yt-dlp library."""
  def __init__(self, ydl_opts: dict | None = None) -> None:
    
    # Default options to silence verbose logs and enable Node.js JS runtime
    default_opts = {
      "quiet": True,
      "no_warnings": True,
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
    """Extract title and a processed list of streams ready for CLI/GUI consumption."""
    info = self.get_video_info(url)
    
    # Video title
    title = info.get("title", "Untitled")
    
    # Video formats
    raw_formats = info.get("formats", [])
    
    # Video available streams
    processed_streams = []
    for stream in raw_formats:
      vcodec = stream.get("vcodec", "N/A")
      acodec = stream.get("acodec", "N/A")
      
      if (vcodec == "none" and acodec == "none"):
        continue
      
      # Ignore storyboards and formats that doesn't have neither audio or video
      processed_streams.append(
        {
          "format_id": stream.get("format_id", "N/A"),
          "ext": stream.get("ext", "N/A"),
          "resolution": stream.get("resolution") or stream.get("format_note") or "N/A",
          "vcodec": vcodec,
          "acodec": acodec,
        }
      )
    
    return {
      "title": title,
      "streams": processed_streams
    }