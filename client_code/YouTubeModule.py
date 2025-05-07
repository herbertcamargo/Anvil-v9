"""
YouTubeModule.py
Python module to integrate TypeScript-generated JavaScript into Anvil forms
"""

import anvil
import anvil.js
from anvil import *

class YouTubeIntegration:
    """
    Class to handle integration of TypeScript-based YouTube functionality into Anvil forms
    """
    
    def __init__(self, 
                 form,
                 grid_container, 
                 player_container, 
                 default_thumbnail=None):
        """
        Initialize YouTube integration
        
        Args:
            form: The Anvil form this integration is attached to
            grid_container: The container for the YouTube grid
            player_container: The container for the YouTube player 
            default_thumbnail: Data URI for default thumbnail
        """
        self.form = form
        self.grid_container = grid_container
        self.player_container = player_container
        
        # Default thumbnail as a gray box with text
        if not default_thumbnail:
            self.default_thumbnail = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='180' viewBox='0 0 320 180'%3E%3Crect width='320' height='180' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='24' text-anchor='middle' fill='%23666666'%3ENo Thumbnail%3C/text%3E%3C/svg%3E"
        else:
            self.default_thumbnail = default_thumbnail
        
        # Set up JavaScript components on this form
        self._setup_javascript()
        
        # Initialize grid and player components
        self._init_components()
        
        # Setup event listeners
        self._setup_event_listeners()
        
        # Current videos
        self.videos = []
    
    def _setup_javascript(self):
        """Load TypeScript-generated JavaScript files"""
        # Create script elements to load our JavaScript files
        for script_name in ['PlaceholderHandler', 'YouTubePlayer', 'YouTubeGrid', 'index']:
            script_path = f"/_/theme/js/{script_name}.js"  # Path to script in theme folder
            
            # Create script element
            script = anvil.js.window.document.createElement('script')
            script.src = script_path
            script.async = False
            
            # Add to document
            anvil.js.window.document.head.appendChild(script)
    
    def _init_components(self):
        """Initialize grid and player components"""
        # Set up the grid container
        self.grid_container.clear()
        self.grid_html = HtmlPanel()
        self.grid_container.add_component(self.grid_html)
        self.grid_html.html = """
        <style>
          .yt-grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 20px;
            padding: 20px;
            width: 100%;
          }
          
          .thumbnail-container {
            display: flex;
            flex-direction: column;
            cursor: pointer;
            transition: transform 0.2s;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            background-color: white;
          }
          
          .thumbnail-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
          }
          
          .thumbnail-image {
            width: 100%;
            aspect-ratio: 16/9;
            object-fit: cover;
          }
          
          .video-title {
            padding: 10px;
            margin: 0;
            font-size: 14px;
            font-weight: 500;
            height: 3em;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
          }
        </style>
        
        <div class="yt-grid-container" id="youtube-grid">
          <!-- Video thumbnails will be inserted here dynamically -->
        </div>
        """
        
        # Set up player container
        self.player_container.clear()
        self.player_html = HtmlPanel()
        self.player_container.add_component(self.player_html)
        self.player_html.html = """
        <style>
          .youtube-player-wrapper {
            display: flex;
            flex-direction: column;
            width: 100%;
          }
          
          .video-title-display {
            font-size: 18px;
            font-weight: 600;
            margin: 10px 0;
            padding: 0 10px;
          }
          
          .youtube-player-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            height: 0;
            overflow: hidden;
            border-radius: 8px;
          }
          
          .youtube-iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 8px;
          }
        </style>
        
        <div class="youtube-player-wrapper">
          <h2 class="video-title-display">Select a video to play</h2>
          <div class="youtube-player-container" id="youtube-player">
            <!-- YouTube iframe will be inserted here dynamically -->
          </div>
        </div>
        """
        
        # Add headings to make the sections clearer
        self.grid_container.add_component(Label(text="YouTube Video Results", role="heading"), index=0)
        self.player_container.add_component(Label(text="Video Player", role="heading"), index=0)
    
    def _setup_event_listeners(self):
        """Set up event listeners for JavaScript callbacks"""
        # Create a thumbnail click handler
        @anvil.js.report_exceptions
        def handle_thumbnail_event(e):
            index = e.detail.index
            self.thumbnail_click(dict(index=index))
        
        # Store the handler so it can be removed later if needed
        self._thumbnail_handler = handle_thumbnail_event
        
        # Add the event listener to the document
        anvil.js.window.document.addEventListener('thumbnail-click', self._thumbnail_handler)
    
    def thumbnail_click(self, *args, **event_args):
        """
        Handle thumbnail click from JavaScript
        
        Args:
            event_args: Dictionary containing the index of the clicked thumbnail
        """
        index = event_args.get('index', 0)
        
        if 0 <= index < len(self.videos):
            self.play_video(self.videos[index])
    
    def play_video(self, video_data):
        """
        Play the specified video
        
        Args:
            video_data: Dictionary with video information
        """
        video_id = video_data.get('id')
        if not video_id:
            return
            
        title = video_data.get('title', 'Untitled video')
            
        try:
            # Call our JavaScript player function and await the promise
            result = anvil.js.await_promise(
                anvil.js.window.YouTubePlayer.loadVideo(video_id, title)
            )
            
            # Now update the iframe src with the new video ID
            player_container = anvil.js.get_dom_node(self.player_html).querySelector('.youtube-player-container')
            if player_container:
                player_container.innerHTML = f"""
                <iframe 
                    src="https://www.youtube.com/embed/{video_id}?autoplay=1" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen
                    class="youtube-iframe">
                </iframe>
                """
                
            # Update video title if available
            title_element = anvil.js.get_dom_node(self.player_html).querySelector('.video-title-display')
            if title_element and title:
                title_element.textContent = title
                
            # Scroll to player
            self.player_container.scroll_into_view()
            
        except anvil.js.ExternalError as js_error:
            # Handle JavaScript errors properly
            error_message = str(js_error.original_error) if hasattr(js_error, 'original_error') else str(js_error)
            alert(f"Error loading video: {error_message}")
            print(f"JavaScript error: {error_message}")
    
    def update_videos(self, videos_data):
        """
        Update the grid with new video data
        
        Args:
            videos_data: List of video dictionaries
        """
        self.videos = videos_data
        
        # Get the HTML container
        grid_container = anvil.js.get_dom_node(self.grid_html).querySelector('.yt-grid-container')
        if not grid_container:
            print("Error: Could not find grid container")
            alert("Could not find grid container")
            return
            
        # Create a new YouTubeGrid instance with our grid container
        grid = anvil.js.window.YouTubeGrid({
            'containerSelector': '#youtube-grid',
            'defaultThumbnail': self.default_thumbnail,
            'maxVideos': 12
        })
        
        # Update the grid with our videos
        grid.updateGrid(videos_data)
    
    def add_placeholder_handler(self):
        """Add global handler to replace placeholder.com images with data URIs"""
        # Create small avatar placeholder (40x40) - plain grey box
        avatar_placeholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' fill='%23cccccc'/%3E%3C/svg%3E"
        
        # Create a placeholder handler with our configuration
        placeholder_handler = anvil.js.window.PlaceholderHandler({
            'avatarPlaceholder': avatar_placeholder,
            'defaultWidth': 40,
            'defaultHeight': 40
        })
        
        # Initialize the handler
        placeholder_handler.initialize()
        
        # Return the handler in case it's needed later
        return placeholder_handler
    
    def cleanup(self):
        """Clean up resources when done"""
        # Remove event listeners to prevent memory leaks
        if hasattr(self, '_thumbnail_handler'):
            anvil.js.window.document.removeEventListener('thumbnail-click', self._thumbnail_handler) 