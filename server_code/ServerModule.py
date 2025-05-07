import anvil.server
from anvil.tables import app_tables
import anvil.http
import json
import urllib.parse
import time

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyAhj_M7HmHGlsEU8WK-NmOAKbGbhxs_ua8"

# Add request throttling to prevent quota issues
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 1  # seconds between requests

def throttle_api_requests():
  """Throttle API requests to avoid quota issues"""
  global LAST_REQUEST_TIME
  current_time = time.time()
  time_since_last = current_time - LAST_REQUEST_TIME
  
  if time_since_last < MIN_REQUEST_INTERVAL:
    # Wait until we can make another request
    sleep_time = MIN_REQUEST_INTERVAL - time_since_last
    time.sleep(sleep_time)
    
  # Update the last request time
  LAST_REQUEST_TIME = time.time()

@anvil.server.callable
def hello():
  return "Hello from the Anvil server!"

@anvil.server.callable
def search_youtube(query):
  """Search YouTube for videos matching the query
  
  This uses the YouTube Data API v3 to search for videos.
  
  Args:
      query: Search terms
      
  Returns:
      List of video data dictionaries with id, title, thumbnail_url
  """
  try:
    # Validate inputs
    if not query or not isinstance(query, str):
      print(f"Invalid query parameter: {query}")
      return []
      
    # Use the YouTube API key
    api_key = "AIzaSyAhj_M7HmHGlsEU8WK-NmOAKbGbhxs_ua8"
    
    if not api_key:
      print("Missing YouTube API key")
      return []
    
    # URL encode the query parameter
    try:
      encoded_query = urllib.parse.quote(query)
    except Exception as encode_err:
      print(f"Error encoding query: {str(encode_err)}")
      # Fall back to a simple encoding by replacing spaces
      encoded_query = query.replace(' ', '+')
    
    # Throttle API requests to avoid quota issues
    throttle_api_requests()
    
    # Build the YouTube API URL with safer string formatting
    try:
      url = "https://www.googleapis.com/youtube/v3/search"
      params = {
        "part": "snippet",
        "q": encoded_query,
        "type": "video",
        "maxResults": "5",  # Reduce to 5 to save quota
        "key": api_key
      }
      
      # Make the request to YouTube API with debugging
      print(f"Making YouTube API request for query: {query}")
      
      # Use the safer params approach to build the URL
      response = anvil.http.request(url, json=True, params=params)
      
    except Exception as http_err:
      print(f"HTTP request error: {str(http_err)}")
      return []
    
    # Check if response contains error information
    if 'error' in response:
      error_info = response.get('error', {})
      error_message = error_info.get('message', 'Unknown API error')
      error_code = error_info.get('code', 'unknown')
      print(f"YouTube API error: {error_code} - {error_message}")
      
      # Handle quota exceeded error specifically
      if error_code == 403 and "quota" in error_message.lower():
        print("YouTube API quota exceeded. Try again later.")
        return []
        
      return []
    
    # Process the response data
    videos = []
    if 'items' in response:
      for item in response['items']:
        try:
          if item['id']['kind'] == 'youtube#video':
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            # Get the best available thumbnail
            thumbnail_url = None
            if 'thumbnails' in snippet:
              thumbnails = snippet['thumbnails']
              # Try to get the highest quality thumbnail available
              for quality in ['high', 'medium', 'default']:
                if quality in thumbnails and 'url' in thumbnails[quality]:
                  thumbnail_url = thumbnails[quality]['url']
                  break
            
            # Create video data dictionary with simpler structure
            videos.append({
              'id': video_id,
              'title': snippet.get('title', 'Untitled Video'),
              'thumbnail_url': thumbnail_url,
              'description': snippet.get('description', '')[:100],  # Limit description length
              'channel': {
                'title': snippet.get('channelTitle', '')
              }
            })
        except KeyError as key_err:
          print(f"Error processing video item: {str(key_err)}")
          continue
          
    print(f"Successfully found {len(videos)} videos")
    return videos
    
  except Exception as e:
    print(f"YouTube API error: {str(e)}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    # Return an empty list if there's an error
    return []

@anvil.server.callable
def get_video_details(video_id):
  """Get detailed information about a specific YouTube video
  
  Args:
      video_id: YouTube video ID
      
  Returns:
      Dictionary with video details
  """
  try:
    if not video_id:
      print("Missing video_id parameter")
      return None
    
    # Use the YouTube API key
    api_key = "AIzaSyAhj_M7HmHGlsEU8WK-NmOAKbGbhxs_ua8"
    
    if not api_key:
      print("Missing YouTube API key")
      return None
    
    # Throttle API requests to avoid quota issues
    throttle_api_requests()
    
    # Build the YouTube API URL for video details with safer params approach
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
      "part": "snippet,statistics,contentDetails",
      "id": video_id,
      "key": api_key
    }
    
    # Make the request
    try:
      response = anvil.http.request(url, json=True, params=params, timeout=10)
    except Exception as http_err:
      print(f"HTTP request error for video details: {str(http_err)}")
      return None
    
    # Check for API errors
    if 'error' in response:
      error_info = response.get('error', {})
      error_message = error_info.get('message', 'Unknown API error')
      error_code = error_info.get('code', 'unknown')
      print(f"YouTube API error: {error_code} - {error_message}")
      return None
    
    # Process the response
    if 'items' in response and len(response['items']) > 0:
      item = response['items'][0]
      snippet = item.get('snippet', {})
      statistics = item.get('statistics', {})
      content_details = item.get('contentDetails', {})
      
      # Get the best available thumbnail
      thumbnail_url = None
      if 'thumbnails' in snippet:
        thumbnails = snippet['thumbnails']
        for quality in ['maxres', 'high', 'medium', 'default']:
          if quality in thumbnails and 'url' in thumbnails[quality]:
            thumbnail_url = thumbnails[quality]['url']
            break
      
      # Create simplified result with only essential data
      return {
        'id': video_id,
        'title': snippet.get('title', 'Untitled Video'),
        'thumbnail_url': thumbnail_url,
        'channel': {
          'title': snippet.get('channelTitle', '')
        },
        'statistics': {
          'views': statistics.get('viewCount', '0')
        }
      }
    else:
      return None
      
  except Exception as e:
    print(f"YouTube API error when getting video details: {str(e)}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    return None

@anvil.server.callable
def test_youtube_api():
  """Simple test to verify the YouTube API key is working
  
  Returns:
      Dictionary with status and message
  """
  try:
    api_key = "AIzaSyAhj_M7HmHGlsEU8WK-NmOAKbGbhxs_ua8"
    
    if not api_key:
      return {"status": "error", "message": "YouTube API key is missing"}
    
    # Throttle API requests to avoid quota issues
    throttle_api_requests()
      
    # Make a simple request to the YouTube API with safer params approach
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
      "part": "snippet",
      "q": "test",
      "maxResults": "1",
      "key": api_key
    }
    
    try:
      print("Testing YouTube API connection...")
      response = anvil.http.request(url, json=True, params=params, timeout=10)
      
      if 'error' in response:
        error_info = response.get('error', {})
        error_message = error_info.get('message', 'Unknown API error')
        error_code = error_info.get('code', 'unknown')
        
        # Handle quota exceeded error specifically
        if error_code == 403 and "quota" in error_message.lower():
          return {
            "status": "error",
            "message": "YouTube API quota exceeded. Try again later or use a different API key.",
            "error_details": error_info
          }
          
        return {
          "status": "error", 
          "message": f"YouTube API error: {error_code} - {error_message}",
          "error_details": error_info
        }
      
      if 'items' in response and len(response['items']) > 0:
        return {"status": "success", "message": "YouTube API key is working correctly"}
      else:
        return {"status": "warning", "message": "YouTube API key seems valid but no results returned"}
        
    except anvil.http.HttpError as http_err:
      return {"status": "error", "message": f"HTTP error ({http_err.status}): {http_err.content}"}
    except Exception as http_err:
      return {"status": "error", "message": f"Request error: {str(http_err)}"}
      
  except Exception as e:
    import traceback
    return {
      "status": "error", 
      "message": f"Error testing YouTube API: {str(e)}",
      "traceback": traceback.format_exc()
    } 