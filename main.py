import sys
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
  url = 'https://www.youtube.com/watch?v=D91NbRl07OY'
  
  service = YoutubeService()
  
  try:
    print("Fetching video information...")
    data = service.get_available_streams(url)
    
    print(f"\nVideo: {data['title']}\n")
    print(format_stream_table(data['streams']))
  
  except Exception as err:
    print(f"Error processing video: {err}", file=sys.stderr)
    
if __name__ == "__main__":
  main()