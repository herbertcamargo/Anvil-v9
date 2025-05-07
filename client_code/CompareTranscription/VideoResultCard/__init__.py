from ._anvil_designer import VideoResultCardTemplate
from anvil import *
import anvil.server
import anvil.users


class VideoResultCard(VideoResultCardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.item = None

  def set_item(self, item):
    try:
      self.item = item
      # Only set the thumbnail if it exists in the item
      if 'thumbnail' in item and item['thumbnail']:
        self.thumbnail_image.source = item['thumbnail']
      else:
        self.thumbnail_image.source = "https://via.placeholder.com/320x180"
        
      # Set the title if it exists
      if 'title' in item and item['title']:
        self.title_label.text = item['title']
      else:
        self.title_label.text = "No title available"
    except Exception as e:
      # Fall back to safe values if there's an error
      self.title_label.text = f"Error loading video data"
      self.thumbnail_image.source = "https://via.placeholder.com/320x180"

  def form_show(self, **event_args):
    """This method is called when the form is shown on the page"""
    pass

  def click(self, **event_args):
    try:
      if self.item and 'video_id' in self.item:
        open_form("CompareTranscription", video_id=self.item["video_id"])
      else:
        Notification("Cannot open video: missing video ID", timeout=3).show()
    except Exception as e:
      Notification(f"Error: {str(e)}", style="danger", timeout=3).show()
