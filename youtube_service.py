import yt_dlp

class YoutubeService:
  """Service class responsible for interacting with the yt-dlp library."""
  def __init__(self, ydl_opts: dict | None = None) -> None:
    
    # Default options to silence verbose logs and enable Node.js JS runtime
    default_opts = {
      "quiet": True,
      "no_warning": True,
      "js_runtimes": {"node": {}},
    }
    
    if ydl_opts:
      default_opts.update(ydl_opts)
      
    self.ydl_opts = default_opts
    
  def get_video_info(self, url: str) -> dict:
    """Extract video info without downloading"""
    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
      return ydl.extract_info(url, download=False)
    
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