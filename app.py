import yt_dlp

url = 'https://www.youtube.com/watch?v=D91NbRl07OY'

ydl_opts = {}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
  
  # Extract info without downloading
  info = ydl.extract_info(url, download=False)
  
  # Video title
  print(f"Vídeo: {info.get('title')}")
  
  # Formatting data view
  print(f"{'ID':<10} {'Extension':<10} {'Resolution':<15} {'Codec Video':<15} {'Codec Audio':<15}")
  print("-" * 70)
  
  # Getting list of video stream formats
  for stream in info.get('formats', []):
    format_id = stream.get('format_id', 'N/A')
    ext = stream.get('ext', 'N/A')
    resolution = stream.get('resolution', stream.get('format_note', 'N/A'))
    vcodec = stream.get('vcodec', 'N/A')
    acodec = stream.get('acodec', 'N/A')
    print(f"{format_id:<10} {ext:<10} {str(resolution):<15} {vcodec:<15} {acodec:<15}")
