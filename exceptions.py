class DownloaderError(Exception): 
  """Base exception for the YouTube Downloader application.""" 
  pass
class VideoNotFoundError(DownloaderError): 
  """Raised when a video URL is invalid, non-existent, or private.""" 
  pass
class StreamExtractionError(DownloaderError): 
  """Raised when metadata or stream extraction fails.""" 
  pass
