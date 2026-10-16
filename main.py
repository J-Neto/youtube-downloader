import sys
from exceptions import DownloaderError, StreamExtractionError, VideoNotFoundError
from youtube_service import YoutubeService

def format_stream_table(streams: list[dict]) -> str:
  """Format stream list into an aligned table string for terminal output."""
  header = f"{'ID':<10} {'Extension':<10} {'Resolution':<15} {'Video Codec':<15} {'Audio Codec':<15}"
  divider = "-" * 70
  lines = [header, divider]
  
  for stream in streams:
    line = (
      f"{stream['format_id']:<10} "
      f"{stream['ext']:<10} "
      f"{str(stream['resolution']):<15} "
      f"{stream['vcodec']:<15} "
      f"{stream['acodec']:<15}"
    )
    lines.append(line)
  return "\n".join(lines)

def main() -> None:
  url = 'https://www.youtube.com/watch?v=D9sdassd1NbRl07OYsss'
  
  service = YoutubeService()
  
  try:
    print("Fetching video information...")
    data = service.get_available_streams(url)
    
    print(f"\nVideo: {data['title']}\n")
    print(format_stream_table(data['streams']))
  
  except VideoNotFoundError as err: 
    print(f"\n[Error] Invalid or unreachable video: {err}", file=sys.stderr) 
    sys.exit(1)
  
  except StreamExtractionError as err: 
    print(f"\n[Error] Could not extract video streams: {err}", file=sys.stderr)
    sys.exit(1)
  
  except DownloaderError as err: 
    print(f"\n[Error] Downloader application error: {err}", file=sys.stderr) 
    sys.exit(1)
  
  except Exception as err:
    print(f"\n[Unexpected Error] An unhandled issue occurred: {err}", file=sys.stderr) 
    sys.exit(1)
    
if __name__ == "__main__":
  main()