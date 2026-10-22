import sys
from src.exceptions import DownloaderError, StreamExtractionError, VideoNotFoundError
from src.youtube_service import YoutubeService

def format_stream_table(streams: list[dict]) -> str:
  """Format stream list into an aligned table string for terminal output."""
  header = f"{'ID':<10} {'Extension':<10} {'Resolution':<20} {'Video Codec':<15} {'Audio Codec':<15}"
  divider = "-" * 70
  lines = [header, divider]
  
  for stream in streams:
    line = (
      f"{stream['format_id']:<10} "
      f"{stream['ext']:<10} "
      f"{str(stream['resolution']):<20} "
      f"{stream['vcodec']:<15} "
      f"{stream['acodec']:<15}"
    )
    lines.append(line)
  return "\n".join(lines)

def main() -> None:
  url = input("Enter YouTube video URL: ").strip()
  
  if not url:
    print('[Error] URL cannot be empty.', file=sys.stderr)
    sys.exit(1)
  
  service = YoutubeService()
  
  try:
    print("\nFetching video information...")
    data = service.get_available_streams(url)
    
    print(f"\nVideo: {data['title']}\n")
    
    print("Select download option:")
    print("1. Audio only (MP3 - 192 kbps)")
    print("2. Video (Select resolution / Format ID)")
    
    while True:
      option = input("\nEnter option (1 or 2, or press Enter to cancel): ")
      if not option:
        confirm = (
          input("Are you sure you want to cancel and exit? (Y/n): ")
          .strip()
          .lower()
        )
        if confirm in ["", "y", "yes"]:
          print("Download cancelled by user.")
          return
        continue
      
      if option not in ["1", "2"]:
        print("\n[Warning] Invalid option. Please select 1 or 2.")
        continue
      break
    
    if option == "1":
      print("\nDownloading audio as MP3...")
      output_dir = service.download_audio(url)
      print(f"\n✅ Audio download completed successfully! Saved in directory: '{output_dir}'")
      
    elif option == "2":
      print("\nAvailable Video Formats:\n")
      print(format_stream_table(data['streams']))
    
      available_ids = [stream["format_id"] for stream in data["streams"]]
    
      while True:
        format_id = input("\nEnter the Format ID you want to download (or press Enter to cancel): ").strip()
      
        if not format_id:
          confirm = (
            input("Are you sure you want to cancel and exit? (Y/n): ")
            .strip()
            .lower()
          )
          if confirm in ["", "y", "yes"]:
            print("Download cancelled by user.")
            return
          continue

        if format_id not in available_ids:
          print(f"\n[Warning] Format ID '{format_id}' is not valid. Please select an ID from the table above." )
          continue
          
        break
        
      print(f"Downloading format '{format_id}'...")
      output_dir = service.download_stream(url, format_id)
      print(f"\n✅ Download completed successfully! Saved in directory: '{output_dir}'")
  
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