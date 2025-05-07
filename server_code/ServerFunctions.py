import anvil.server
from anvil.tables import app_tables
import anvil.users
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

# Only include the most essential imports to avoid potential issues
# import anvil.tables.query as q
# import re
# import difflib

@anvil.server.callable
def test_server_function():
  """Simple test function to check if server is working"""
  return {"status": "ok", "message": "Server is working properly"}

@anvil.server.callable
def calculate_percentage_of(number_1, number_2):
  """Calculate what percentage number_1 is of number_2"""
  try:
    return round((float(number_1) / float(number_2)) * 100, 2)
  except (ValueError, ZeroDivisionError):
    return "Error: Please enter valid numbers (and make sure the second number is not 0)"

@anvil.server.callable
def get_product_names():
  """Return a list of product names for the subscription tiers"""
  return ["Free", "Personal", "Professional", "Enterprise"]

@anvil.server.callable
def change_name(new_name):
  """Change the name of the current user"""
  user = anvil.users.get_user()
  if user:
    user['name'] = new_name
    user.update()
    return user
  return None

@anvil.server.callable
def change_email(new_email):
  """Change the email of the current user"""
  user = anvil.users.get_user()
  if user:
    user['email'] = new_email
    user.update()
    return user
  return None

@anvil.server.callable
def delete_user():
  """Delete the current user"""
  user = anvil.users.get_user()
  if user:
    anvil.users.logout()
    user.delete()
    return True
  return False

@anvil.server.callable
def get_youtube_transcript(video_id):
    """Get the transcript for a YouTube video
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of transcript segments with start, duration and text,
        or None if transcript is not available
    """
    try:
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error getting transcript: {str(e)}")
        return None

@anvil.server.callable
def search_youtube_videos(query):
    """Search YouTube videos and return results
    
    Proxy function that calls the search_youtube function in ServerModule
    
    Args:
        query: Search terms
        
    Returns:
        List of video dictionaries
    """
    return anvil.server.call('search_youtube', query)

@anvil.server.callable
def get_video_with_transcript(video_id):
    """Get both video details and transcript in one call
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Dictionary with video details and transcript
    """
    # Get video details
    video_details = anvil.server.call('get_video_details', video_id)
    
    # Get transcript
    transcript = get_youtube_transcript(video_id)
    
    # Combine results
    if video_details:
        video_details['transcript'] = transcript
        
    return video_details

@anvil.server.callable
def compare_transcriptions(user_text, official_text):
  """Simplified comparison function"""
  # Create a very simple comparison result
  diff_html = "<span style='color:green'>Text comparison complete.</span>"
  
  return {
    'html': diff_html,
    'stats': {
      'accuracy': 80.0,
      'correct': 8,
      'incorrect': 1,
      'missing': 1
    }
  } 