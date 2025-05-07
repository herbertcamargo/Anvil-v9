import anvil.server
from anvil.tables import app_tables
import anvil.http
import json

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyAhj_M7HmHGlsEU8WK-NmOAKbGbhxs_ua8"

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
    # Use the YouTube API key
    api_key = YOUTUBE_API_KEY
    
    # Build the YouTube API URL
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=12&key={api_key}"
    
    # Make the request to YouTube API
    response = anvil.http.request(url, json=True)
    
    # Process the response data
    videos = []
    if 'items' in response:
      for item in response['items']:
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
          
          # Create video data dictionary
          videos.append({
            'id': video_id,
            'title': snippet.get('title', 'Untitled Video'),
            'thumbnail_url': thumbnail_url,
            'description': snippet.get('description', ''),
            'published': snippet.get('publishedAt', ''),
            'channel': {
              'id': snippet.get('channelId', ''),
              'title': snippet.get('channelTitle', '')
            }
          })
          
    return videos
    
  except Exception as e:
    print(f"YouTube API error: {str(e)}")
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
    # Use the YouTube API key
    api_key = YOUTUBE_API_KEY
    
    # Build the YouTube API URL for video details
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}&key={api_key}"
    
    # Make the request
    response = anvil.http.request(url, json=True)
    
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
      
      return {
        'id': video_id,
        'title': snippet.get('title', 'Untitled Video'),
        'description': snippet.get('description', ''),
        'thumbnail_url': thumbnail_url,
        'published': snippet.get('publishedAt', ''),
        'channel': {
          'id': snippet.get('channelId', ''),
          'title': snippet.get('channelTitle', '')
        },
        'statistics': {
          'views': statistics.get('viewCount', '0'),
          'likes': statistics.get('likeCount', '0'),
          'comments': statistics.get('commentCount', '0')
        },
        'duration': content_details.get('duration', '')
      }
    else:
      return None
      
  except Exception as e:
    print(f"YouTube API error when getting video details: {str(e)}")
    return None 