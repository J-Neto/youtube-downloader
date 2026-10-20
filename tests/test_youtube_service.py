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
