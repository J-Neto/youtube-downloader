from unittest.mock import MagicMock, patch
import pytest
import yt_dlp
from src.exceptions import StreamExtractionError, VideoNotFoundError
from src.youtube_service import YoutubeService

@patch("src.youtube_service.yt_dlp.YoutubeDL")
def test_get_video_info_success(mock_youtube_dl: MagicMock) -> None:
  """Test successful extraction of video raw info using a mock."""
  # Mock data returned by yt-dlp
  mock_info = {"title": "Test Video", "formats": []}

  # Configure the mock instance
  mock_instance = MagicMock()
  mock_instance.extract_info.return_value = mock_info
  mock_youtube_dl.return_value.__enter__.return_value = mock_instance

  service = YoutubeService()
  result = service.get_video_info("https://www.youtube.com/watch?v=D91NbRl07OY&t=2s")

  assert result["title"] == "Test Video"
  mock_instance.extract_info.assert_called_once_with(
    "https://www.youtube.com/watch?v=D91NbRl07OY&t=2s", download=False
  )




@patch("src.youtube_service.yt_dlp.YoutubeDL")
def test_get_video_info_raises_video_not_found(mock_youtube_dl: MagicMock) -> None:
  """Test that VideoNotFoundError is raised when video is unavailable."""
  mock_instance = MagicMock()
  mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
    "ERROR: This video is unavailable"
  )
  mock_youtube_dl.return_value.__enter__.return_value = mock_instance

  service = YoutubeService()

  with pytest.raises(VideoNotFoundError):
    service.get_video_info("https://www.youtube.com/watch?v=D91NbRl07OY&t=2s")
 
 
      
@patch("src.youtube_service.yt_dlp.YoutubeDL")
def test_get_video_info_raises_stream_extraction_error(
  mock_youtube_dl: MagicMock,
) -> None:
  """Test that StreamExtractionError is raised on generic DownloadError."""
  mock_instance = MagicMock()
  mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
    "ERROR: Network connection failed"
  )
  mock_youtube_dl.return_value.__enter__.return_value = mock_instance

  service = YoutubeService()

  with pytest.raises(StreamExtractionError):
    service.get_video_info("https://www.youtube.com/watch?v=D91NbRl07OY&t=2s")
    
    
@patch("src.youtube_service.yt_dlp.YoutubeDL")
def test_get_available_streams_filters_empty_codecs(
  mock_youtube_dl: MagicMock,
) -> None:
  """Test that formats with neither video nor audio codec are filtered out."""
  mock_info = {
    "title": "Sample Video",
    "formats": [
      {
        "format_id": "137",
        "ext": "mp4",
        "resolution": "1080p",
        "vcodec": "avc1.640028",
        "acodec": "none",
      },
      {
        "format_id": "sb0",
        "ext": "mhtml",
        "resolution": "N/A",
        "vcodec": "none",
        "acodec": "none",  # Should be filtered out
      },
    ],
  }

  mock_instance = MagicMock()
  mock_instance.extract_info.return_value = mock_info
  mock_youtube_dl.return_value.__enter__.return_value = mock_instance

  service = YoutubeService()
  data = service.get_available_streams("https://www.youtube.com/watch?v=D91NbRl07OY&t=2s")

  assert data["title"] == "Sample Video"
  assert len(data["streams"]) == 1
  assert data["streams"][0]["format_id"] == "137"
  
  
@patch("src.youtube_service.yt_dlp.YoutubeDL")
def test_download_stream_success(mock_youtube_dl: MagicMock) -> None:
  """Test successful stream download using a mock."""
  mock_instance = MagicMock()
  mock_youtube_dl.return_value.__enter__.return_value = mock_instance
  
  service = YoutubeService()
  output_dir = service.download_stream("http://example.com", "18", output_dir="downloads")
  
  assert output_dir == "downloads"
  mock_instance.download.assert_called_once_with(["http://example.com"])


@patch("src.youtube_service.yt_dlp.YoutubeDL")
def test_download_stream_raises_stream_extraction_error(
  mock_youtube_dl: MagicMock,
) -> None:
  """Test that StreamExtractionError is raised if download fails."""
  mock_instance = MagicMock()
  mock_instance.download.side_effect = yt_dlp.utils.DownloadError("Download failed")
  mock_youtube_dl.return_value.__enter__.return_value = mock_instance
  
  service = YoutubeService()
  
  with pytest.raises(StreamExtractionError):
    service.download_stream("http://example.com", "18")


@pytest.fixture
def service() -> YoutubeService:
  """Fixture to supply a clean YoutubeService instance."""
  return YoutubeService()

def test_download_audio_success(service: YoutubeService) -> None:
  """Test successful audio download configuration and execution."""
  url = "https://www.youtube.com/watch?v=D91NbRl07OY&t=2s"
  with patch("yt_dlp.YoutubeDL") as mock_yt_dlp:
    mock_instance = MagicMock()
    mock_yt_dlp.return_value.__enter__.return_value = mock_instance
    
    output_dir = service.download_audio(url, output_dir="test_downloads")
    
    assert output_dir == "test_downloads"
    mock_yt_dlp.assert_called_once()
    
    # Verify that postprocessors for MP3 conversion were configured
    opts_passed = mock_yt_dlp.call_args[0][0]
    assert opts_passed["format"] == "bestaudio/best"
    assert opts_passed["postprocessors"][0]["key"] == "FFmpegExtractAudio"
    assert opts_passed["postprocessors"][0]["preferredcodec"] == "mp3"
    
    mock_instance.download.assert_called_once_with([url])
    
def test_download_audio_failure(service: YoutubeService) -> None:
  """Test exception raising when audio download fails."""
  url = "https://www.youtube.com/watch?v=D91NbRl07OY&t=2s"
  with patch("yt_dlp.YoutubeDL") as mock_yt_dlp:
    mock_instance = MagicMock()
    mock_instance.download.side_effect = yt_dlp.utils.DownloadError("Audio error")
    mock_yt_dlp.return_value.__enter__.return_value = mock_instance
    
    with pytest.raises(StreamExtractionError) as exc_info:
        service.download_audio(url)
        
    assert "Failed to download audio" in str(exc_info.value)

def test_get_available_streams_filtering(service: YoutubeService) -> None:
  """Test that stream filtering returns deduplicated resolutions and ignores audio-only formats."""
  url = "https://www.youtube.com/watch?v=D91NbRl07OY&t=2s"
  mock_raw_info = {
    "title": "Test Video",
    "formats": [
        {"format_id": "140", "vcodec": "none", "acodec": "mp4a.40.2", "height": None, "ext": "m4a"},  # Audio only
        {"format_id": "137", "vcodec": "avc1.640028", "acodec": "none", "height": 1080, "width": 1920, "ext": "mp4"},
        {"format_id": "248", "vcodec": "vp9", "acodec": "none", "height": 1080, "width": 1920, "ext": "webm"},
        {"format_id": "136", "vcodec": "avc1.4D401F", "acodec": "none", "height": 720, "width": 1280, "ext": "mp4"},
    ],
  }
  
  with patch.object(service, "get_video_info", return_value=mock_raw_info):
    result = service.get_available_streams(url)
    
    assert result["title"] == "Test Video"
    # Should return exactly 2 streams (1080p and 720p), excluding audio-only
    assert len(result["streams"]) == 2
    
    # 1080p should select MP4 (avc1) due to higher score over webm (vp9)
    assert result["streams"][0]["format_id"] == "137"
    assert result["streams"][0]["resolution"] == "1080p (1920x1080)"
    
    # 720p stream check
    assert result["streams"][1]["format_id"] == "136"
    assert result["streams"][1]["resolution"] == "720p (1280x720)"
    
def test_get_video_info_rejects_search_url(service: YoutubeService) -> None:
  """Test that search result URLs raise VideoNotFoundError immediately."""
  search_url = "https://www.youtube.com/results?search_query=supermassive+black+hole+muse"
  with pytest.raises(VideoNotFoundError) as exc_info:
      service.get_video_info(search_url)
  assert "Search or channel URLs are not supported" in str(exc_info.value)
