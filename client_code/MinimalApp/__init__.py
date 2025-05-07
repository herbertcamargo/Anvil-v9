from ._anvil_designer import MinimalAppTemplate
from anvil import *
import anvil.js
from anvil.js.window import HTMLElement

class MinimalApp(MinimalAppTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Set all panels visible
    self.show_all_panels()
    
    # Enable global exception reporting for all JavaScript callbacks
    anvil.js.report_all_exceptions(True)
    
    # Add global placeholder image handler
    self.add_placeholder_image_handler()
    
    # Initialize video functionality
    self.setup_youtube_functionality()
    
    # Add debug button
    self.debug_panel = FlowPanel()
    self.debug_button = Button(text="Debug HTML", role="outlined-button")
    self.debug_button.set_event_handler('click', self.debug_html)
    self.debug_panel.add_component(self.debug_button)
    
    # Add test grid button
    self.test_grid_button = Button(text="Create Test Grid", role="primary-color")
    self.test_grid_button.set_event_handler('click', self.create_test_grid)
    self.debug_panel.add_component(self.test_grid_button)
    
    # Add test API button
    self.test_api_button = Button(text="Test YouTube API", role="danger")
    self.test_api_button.set_event_handler('click', self.test_youtube_api)
    self.debug_panel.add_component(self.test_api_button)
    
    # Add the debug panel to the search panel
    self.search_panel.add_component(self.debug_panel, index=1)
    
  def add_placeholder_image_handler(self):
    """Add a global handler to replace all placeholder.com images with data URIs"""
    # Create small avatar placeholder (40x40)
    avatar_placeholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='10' text-anchor='middle' fill='%23666666'%3E?%3C/text%3E%3C/svg%3E"
    
    # Create a global script to intercept ALL network requests to placeholder.com
    placeholder_script = anvil.js.window.document.createElement('script')
    placeholder_script.innerHTML = f"""
    (function() {{
      // Block ALL placeholder.com requests at the fetch/XHR level
      const originalFetch = window.fetch;
      window.fetch = function(url, options) {{
        if (url && url.toString().includes('placeholder.com')) {{
          console.log('Blocked fetch request to placeholder.com:', url);
          return Promise.resolve(new Response(
            new Blob([''], {{type: 'text/plain'}}),
            {{status: 200, statusText: 'Blocked by Anvil'}}
          ));
        }}
        return originalFetch.apply(this, arguments);
      }};
      
      // Block XMLHttpRequest as well
      const originalOpen = XMLHttpRequest.prototype.open;
      XMLHttpRequest.prototype.open = function(method, url, ...args) {{
        if (url && url.toString().includes('placeholder.com')) {{
          console.log('Blocked XHR request to placeholder.com:', url);
          this.abort();
          return;
        }}
        return originalOpen.apply(this, [method, url, ...args]);
      }};
      
      // Create data URIs for different image sizes
      const generatePlaceholder = (width, height) => {{
        if (width <= 40 && height <= 40) {{
          return "{avatar_placeholder}";
        }} else {{
          return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${{width}}' height='${{height}}' viewBox='0 0 ${{width}} ${{height}}'%3E%3Crect width='${{width}}' height='${{height}}' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='${{Math.max(12, Math.min(24, width/10))}}' text-anchor='middle' fill='%23666666'%3E${{width}}x${{height}}%3C/text%3E%3C/svg%3E`;
        }}
      }};
      
      // Block and replace image sources at the DOM level
      function replaceImgSrc(img) {{
        if (img.src && img.src.includes('placeholder.com')) {{
          // Extract dimensions from URL if possible
          const match = img.src.match(/placeholder\\.com\\/(\\d+)x(\\d+)/);
          const width = match ? parseInt(match[1]) : 40;
          const height = match ? parseInt(match[2]) : 40;
          
          // Replace with appropriate SVG
          img.src = generatePlaceholder(width, height);
          
          // Prevent further loading attempts
          img.setAttribute('data-original-src', 'blocked-placeholder');
        }}
      }}
      
      // Process all existing images
      document.querySelectorAll('img').forEach(replaceImgSrc);
      
      // Watch for dynamically added images
      const observer = new MutationObserver(mutations => {{
        mutations.forEach(mutation => {{
          if (mutation.addedNodes) {{
            mutation.addedNodes.forEach(node => {{
              // Process the node itself if it's an image
              if (node.nodeName === 'IMG') replaceImgSrc(node);
              
              // Process any images inside the node
              if (node.querySelectorAll) {{
                node.querySelectorAll('img').forEach(replaceImgSrc);
              }}
            }});
          }}
          
          // Also check for changed src attributes
          if (mutation.type === 'attributes' && 
              mutation.attributeName === 'src' && 
              mutation.target.nodeName === 'IMG') {{
            replaceImgSrc(mutation.target);
          }}
        }});
      }});
      
      // Observe the entire document for changes
      observer.observe(document.documentElement, {{ 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['src']
      }});
      
      // Block and prevent any access to placeholder.com at the lowest level
      // by defining a service worker that blocks those requests
      if ('serviceWorker' in navigator) {{
        navigator.serviceWorker.getRegistrations().then(registrations => {{
          for (let registration of registrations) {{
            if (registration.scope.includes(window.location.origin)) {{
              registration.unregister();
            }}
          }}
        }});
      }}
      
      console.log('Placeholder image blocking system initialized');
    }})();
    """
    
    # Add the script to the document head
    anvil.js.window.document.head.appendChild(placeholder_script)
    
  def create_test_grid(self, **event_args):
    """Create a test grid with simple colored boxes"""
    test_videos = []
    
    # Create 9 test videos with different colors
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'teal', 'pink', 'brown', 'gray']
    
    for i, color in enumerate(colors):
      test_videos.append({
        'id': f'test-{i}',
        'title': f'Test Video {i+1} ({color})',
        'thumbnail_url': f'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180" style="background:{color}"><text x="50%" y="50%" fill="white" font-size="20" text-anchor="middle">Test {i+1}</text></svg>'
      })
    
    # Update the grid with these test videos
    self.update_youtube_grid(test_videos)
    
    # Scroll to the grid container
    self.yt_grid_container.scroll_into_view()
    
  def debug_html(self, **event_args):
    """Debug HTML structure and components"""
    try:
      # Check if HTML components exist
      html_status = "HTML components:\n"
      html_status += f"Grid HTML exists: {hasattr(self, 'grid_html')}\n"
      html_status += f"Player HTML exists: {hasattr(self, 'player_html')}\n"
      
      # Check containers
      container_status = "Containers:\n"
      container_status += f"Grid container exists: {self.yt_grid_container is not None}\n"
      container_status += f"Player container exists: {self.yt_player_container is not None}\n"
      
      # Check DOM elements
      dom_status = "DOM elements:\n"
      grid_container = None
      player_container = None
      
      try:
        grid_container = anvil.js.get_dom_node(self.grid_html).querySelector('.yt-grid-container')
        dom_status += f"Grid container DOM element exists: {grid_container is not None}\n"
      except:
        dom_status += "Error accessing grid container DOM element\n"
        
      try:
        player_container = anvil.js.get_dom_node(self.player_html).querySelector('.youtube-player-container')
        dom_status += f"Player container DOM element exists: {player_container is not None}\n"
      except:
        dom_status += "Error accessing player container DOM element\n"
        
      # Show complete status
      alert(f"{html_status}\n{container_status}\n{dom_status}")
      
      # Try to add a test thumbnail
      if grid_container:
        grid_container.innerHTML = '<div style="background-color: red; color: white; padding: 20px; margin: 10px;">Test Thumbnail</div>'
        alert("Added test thumbnail - check if it's visible")
      
    except Exception as e:
      alert(f"Debug error: {str(e)}")
  
  def setup_youtube_functionality(self):
    """Set up YouTube functionality directly in the form"""
    self.videos = []
    
    # Create HTML components for grid and player
    self.yt_grid_container.clear()
    self.grid_html = HtmlPanel()
    self.yt_grid_container.add_component(self.grid_html)
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
    
    <div class="yt-grid-container">
      <!-- Video thumbnails will be inserted here dynamically -->
    </div>
    """
    
    # Set up player container
    self.yt_player_container.clear()
    self.player_html = HtmlPanel()
    self.yt_player_container.add_component(self.player_html)
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
      <div class="youtube-player-container">
        <!-- YouTube iframe will be inserted here dynamically -->
      </div>
    </div>
    """
    
    # Add headings to make the sections clearer
    self.yt_grid_container.add_component(Label(text="YouTube Video Results", role="heading"), index=0)
    self.yt_player_container.add_component(Label(text="Video Player", role="heading"), index=0)
    
  def update_youtube_grid(self, videos_data):
    """Update the grid with new video data"""
    self.videos = videos_data
    
    # Get the HTML container
    grid_container = anvil.js.get_dom_node(self.grid_html).querySelector('.yt-grid-container')
    if not grid_container:
      print("Error: Could not find grid container")
      alert("Could not find grid container")
      return
      
    # Clear existing content
    grid_container.innerHTML = ''
    
    # Check if we have videos to display
    if not videos_data:
      # Display a "no videos found" message in the grid
      grid_container.innerHTML = """
        <div style="text-align: center; padding: 40px; width: 100%;">
          <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 30px; background-color: #f8f9fa; display: inline-block; max-width: 600px;">
            <h3 style="color: #6c757d; margin-bottom: 15px;">No Videos Found</h3>
            <p style="color: #6c757d;">Enter a search term to display video results.</p>
            <p style="color: #6c757d; font-size: 0.9em; margin-top: 15px;">The application is currently in offline mode.</p>
          </div>
        </div>
      """
      return
    
    # Check if we're in offline mode
    is_offline_mode = any(video.get('offline_mode', False) for video in videos_data)
    
    # Otherwise, continue with normal video display (if we have videos)
    thumbnails_html = ""
    
    # Data URI for default thumbnail (gray background with text)
    default_thumbnail = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='180' viewBox='0 0 320 180'%3E%3Crect width='320' height='180' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='24' text-anchor='middle' fill='%23666666'%3ENo Thumbnail%3C/text%3E%3C/svg%3E"
    
    for i, video in enumerate(videos_data[:12]):
      video_id = video.get('id', '')
      title = video.get('title', 'Untitled video')
      # Use the provided thumbnail URL or the default if it's a placeholder or missing
      thumbnail_url = video.get('thumbnail_url', default_thumbnail)
      if "placeholder.com" in thumbnail_url:
        thumbnail_url = default_thumbnail
        
      # Get additional metadata for enhanced display
      is_demo = video.get('isDemo', False)
      formatted_views = video.get('formatted_views', '')
      duration = video.get('duration', '')
      time_ago = video.get('time_ago', '')
      channel_title = video.get('channel', {}).get('title', 'Unknown channel')
      
      # Create the thumbnail HTML with a data attribute for the index
      thumbnails_html += f"""
        <div class="thumbnail-container" data-index="{i}" data-video-id="{video_id}" onclick="handleThumbnailClick({i})">
          <div class="thumbnail-wrapper">
            <img src="{thumbnail_url}" alt="{title}" class="thumbnail-image" onerror="this.onerror=null; this.src='{default_thumbnail}'">
            {f'<span class="video-duration">{duration}</span>' if duration else ''}
            {f'<span class="demo-badge">DEMO</span>' if is_demo else ''}
          </div>
          <div class="video-info">
            <p class="video-title">{title}</p>
            <p class="channel-title">{channel_title}</p>
            <p class="video-metadata">
              {f'{formatted_views} views' if formatted_views else ''}
              {f' • {time_ago}' if time_ago else ''}
            </p>
          </div>
        </div>
      """
    
    # Add offline mode indicator if needed
    if is_offline_mode:
      offline_notice = """
        <div class="offline-notice">
          <div class="offline-badge">OFFLINE MODE</div>
          <p class="offline-text">YouTube API connection is not available. Showing demo videos.</p>
        </div>
      """
      thumbnails_html = offline_notice + thumbnails_html
    
    # Inject updated CSS for the enhanced thumbnails
    enhanced_css = """
    <style>
      .offline-notice {
        width: 100%;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 10px 15px;
        margin-bottom: 20px;
        border-radius: 4px;
        grid-column: 1 / -1;
      }
      
      .offline-badge {
        display: inline-block;
        background-color: #dc3545;
        color: white;
        font-size: 12px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 3px;
        margin-bottom: 5px;
      }
      
      .offline-text {
        margin: 0;
        font-size: 14px;
      }
      
      .thumbnail-wrapper {
        position: relative;
        width: 100%;
        aspect-ratio: 16/9;
      }
      
      .video-duration {
        position: absolute;
        bottom: 8px;
        right: 8px;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 1px 4px;
        border-radius: 2px;
        font-size: 12px;
        font-weight: 500;
      }
      
      .demo-badge {
        position: absolute;
        top: 8px;
        left: 8px;
        background-color: #f39c12;
        color: white;
        padding: 1px 4px;
        border-radius: 2px;
        font-size: 12px;
        font-weight: bold;
      }
      
      .video-info {
        padding: 10px;
      }
      
      .channel-title {
        font-size: 13px;
        color: #606060;
        margin: 4px 0;
      }
      
      .video-metadata {
        font-size: 12px;
        color: #606060;
        margin: 0;
      }
    </style>
    """
    
    # First, inject the click handler function into the page
    # Use a separate module-like IIFE (Immediately Invoked Function Expression) for better scoping
    click_handler_script = anvil.js.window.document.createElement('script')
    click_handler_script.innerHTML = """
      (function() {
        // Create a proper module-like scope for YouTube thumbnail handlers
        window.handleThumbnailClick = function(index) {
          var event = new CustomEvent('thumbnail-click', { 
            detail: { index: index },
            bubbles: true, 
            cancelable: true 
          });
          document.dispatchEvent(event);
        };
        
        // Export video player functionality to global scope
        window.YouTubePlayer = {
          loadVideo: function(videoId, title) {
            // This method could be called directly from JavaScript if needed
            return new Promise(function(resolve, reject) {
              try {
                // Implementation could be expanded later
                console.log("Loading video: " + videoId + " - " + title);
                resolve({videoId: videoId, title: title});
              } catch (error) {
                reject(error);
              }
            });
          }
        };
      })();
    """
    anvil.js.window.document.head.appendChild(click_handler_script)
    
    # Set all thumbnails at once
    grid_container.innerHTML = enhanced_css + thumbnails_html
    
    # Only add event listeners if we have videos
    if videos_data:
      # Add a document-level event listener for the custom event
      @anvil.js.report_exceptions
      def handle_thumbnail_event(e):
        index = e.detail.index
        self.thumbnail_click(dict(index=index))
      
      # Store the event listener function to be able to remove it later if needed
      self._thumbnail_handler = handle_thumbnail_event
      
      # Add the event listener to the document
      anvil.js.window.document.addEventListener('thumbnail-click', self._thumbnail_handler)
    
  def thumbnail_click(self, *args, **event_args):
    """Handle thumbnail click from HTML"""
    index = event_args.get('index', 0)
    alert(f"Thumbnail clicked: {index}")
    if 0 <= index < len(self.videos):
      self.play_video(self.videos[index])
    
  def play_video(self, video_data):
    """Play the specified video"""
    video_id = video_data.get('id')
    if not video_id:
      return
      
    title = video_data.get('title', 'Untitled video')
    is_demo = video_data.get('isDemo', False)
    channel_title = video_data.get('channel', {}).get('title', '')
      
    try:
      # Call our JavaScript player function and await the promise
      result = anvil.js.await_promise(
        anvil.js.window.YouTubePlayer.loadVideo(video_id, title)
      )
      
      # Check if this is a demo video
      if is_demo or video_id.startswith('demo-'):
        # For demo videos, show a placeholder instead of an actual YouTube embed
        player_container = anvil.js.get_dom_node(self.player_html).querySelector('.youtube-player-container')
        if player_container:
          # Create a placeholder with the video title
          thumbnail_url = video_data.get('thumbnail_url', '')
          
          player_container.innerHTML = f"""
            <div class="demo-player">
              <div class="demo-player-header">
                <div class="demo-badge">DEMO VIDEO</div>
                <div class="offline-badge">OFFLINE MODE</div>
              </div>
              <div class="demo-player-content">
                <img src="{thumbnail_url}" alt="{title}" class="demo-thumbnail">
                <div class="demo-play-button">▶</div>
                <div class="demo-player-message">
                  <h3>This is a demo video</h3>
                  <p>YouTube API connection is not available.</p>
                  <p>Showing placeholder content instead.</p>
                </div>
              </div>
            </div>
            <style>
              .demo-player {
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0;
                left: 0;
                background-color: #f8f9fa;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
              }
              
              .demo-player-header {
                padding: 10px;
                display: flex;
                gap: 10px;
              }
              
              .demo-player-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                position: relative;
              }
              
              .demo-thumbnail {
                width: 100%;
                height: 100%;
                object-fit: cover;
                position: absolute;
                top: 0;
                left: 0;
                filter: brightness(0.7);
              }
              
              .demo-play-button {
                background-color: rgba(255, 0, 0, 0.8);
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                position: absolute;
                cursor: pointer;
              }
              
              .demo-player-message {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-top: 20px;
                z-index: 1;
              }
              
              .demo-player-message h3 {
                margin-top: 0;
              }
            </style>
          """
      else:
        # For real YouTube videos, use the standard iframe embed
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
        
      # Update channel name if available  
      if channel_title and title_element:
        title_element.innerHTML = f"{title}<br><span style='font-size: 14px; color: #606060;'>{channel_title}</span>"
        
      # Scroll to player
      self.yt_player_container.scroll_into_view()
      
    except anvil.js.ExternalError as js_error:
      # Handle JavaScript errors properly   
      error_message = str(js_error.original_error) if hasattr(js_error, 'original_error') else str(js_error)
      alert(f"Error loading video: {error_message}")
      print(f"JavaScript error: {error_message}")
    
  def show_all_panels(self):
    """Show all panels"""
    self.welcome_panel.visible = True
    self.search_panel.visible = True
    self.compare_panel.visible = True
    
  def home_link_click(self, **event_args):
    """Handle click on Home link - scroll to top"""
    self.welcome_panel.scroll_into_view()
    
  def search_link_click(self, **event_args):
    """Handle click on Search link - scroll to search section"""
    self.search_panel.scroll_into_view()
    
  def comparison_link_click(self, **event_args):
    """Handle click on Comparison link - scroll to comparison section"""
    self.compare_panel.scroll_into_view()
    
  def welcome_search_button_click(self, **event_args):
    """Handle click on Start Searching button - scroll to search section"""
    self.search_panel.scroll_into_view()
    self.search_box.focus()
    
  def welcome_compare_button_click(self, **event_args):
    """Handle click on Practice Comparison button - scroll to comparison section"""
    self.compare_panel.scroll_into_view()
    self.text1_box.focus()
  
  def search_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    query = self.search_box.text
    if not query:
      alert("Please enter a search term")
      return
      
    # Show a loading indicator
    Notification("Searching for videos...", timeout=2).show()
    
    # First, test the YouTube API connection
    try:
      # This will now return offline mode notification
      api_status = anvil.server.call('test_youtube_api')
      
      is_offline_mode = api_status.get('offline_mode', False)
      
      if is_offline_mode:
        # Show offline mode notification (nicer than an error)
        Notification("Running in offline mode - showing demo videos", timeout=3).show()
    
      # Make the actual API call to search YouTube
      videos = anvil.server.call('search_youtube_videos', query)
      
      # Update the display with the search results
      self.results_panel.clear()
      
      # Add a header with offline mode indicator if needed
      if is_offline_mode:
        offline_header = ColumnPanel()
        offline_header.background = "#f8d7da"
        offline_header.border = "1px solid #f5c6cb"
        offline_header.padding = ("10px", "15px")
        offline_header.margin = ("0", "0", "15px", "0")
        offline_header.border_radius = "4px"
        
        offline_badge = Label(text="OFFLINE MODE")
        offline_badge.background = "#dc3545"
        offline_badge.foreground = "white"
        offline_badge.font_size = 12
        offline_badge.bold = True
        offline_badge.padding = ("2px", "6px")
        offline_badge.border_radius = "3px"
        
        offline_message = Label(text="YouTube API connection is unavailable. Showing demo videos instead.")
        offline_message.foreground = "#721c24"
        
        offline_header.add_component(offline_badge)
        offline_header.add_component(offline_message)
        
        self.results_panel.add_component(offline_header)
      
      # Add search results header
      results_title = Label(text=f"Search Results for: {query}", role="heading")
      self.results_panel.add_component(results_title)
      
      # Update the YouTube grid with the returned videos
      self.update_youtube_grid(videos)
      
      if not videos:
        # No videos found, show an informative message
        message_panel = ColumnPanel(spacing="medium")
        message_panel.border = "1px solid #ddd"
        message_panel.background = "#f8f9fa"
        message_panel.spacing = ("medium", "medium", "medium", "medium")
        
        title = Label(text="No Videos Found", role="heading")
        title.bold = True
        
        info = Label(text=f"No videos found for search term '{query}'.")
        
        message_panel.add_component(title)
        message_panel.add_component(info)
        
        self.results_panel.add_component(message_panel)
      else:
        # Show count of videos found
        video_count = len(videos)
        mode_text = " (Demo)" if is_offline_mode else ""
        Notification(f"Found {video_count} videos{mode_text} for '{query}'", timeout=3).show()
      
      # Scroll to show the results
      self.results_panel.scroll_into_view()
      
    except Exception as e:
      # Show error notification if search fails
      error_message = str(e)
      alert(f"Error during search: {error_message}")
      print(f"Search error: {error_message}")
      
      # Show error in UI
      self.results_panel.clear()
      self.results_panel.add_component(Label(text=f"Search Results for: {query}", role="heading"))
      
      message_panel = ColumnPanel(spacing="medium")
      message_panel.border = "1px solid #ddd"
      message_panel.background = "#f8f9fa"
      message_panel.spacing = ("medium", "medium", "medium", "medium")
      
      title = Label(text="Search Error", role="heading")
      title.bold = True
      title.foreground = "#dc3545"  # Red color for error
      
      info = Label(text=f"Error searching for '{query}': {error_message}")
      
      message_panel.add_component(title)
      message_panel.add_component(info)
      
      # Add a "Try offline mode" suggestion
      suggestion = Label(text="The application will now show demo videos instead.")
      suggestion.foreground = "#0056b3"
      message_panel.add_component(suggestion)
      
      self.results_panel.add_component(message_panel)
      
      # Try to get some fallback results
      try:
        # This directly calls the fallback function
        videos = anvil.server.call('get_fallback_videos', query)
        self.update_youtube_grid(videos)
      except:
        # If even that fails, show empty grid
        self.update_youtube_grid([])
      
      # Scroll to show the results
      self.results_panel.scroll_into_view()
    
  def compare_button_click(self, **event_args):
    """Compare texts without server calls"""
    text1 = self.text1_box.text
    text2 = self.text2_box.text
    
    if not text1 or not text2:
      alert("Please enter both texts to compare")
      return
      
    # Simple client-side comparison
    if text1 == text2:
      result = "Texts are identical"
      accuracy = 100
    else:
      result = "Texts differ"
      # Very simple difference calculation
      common_chars = sum(1 for a, b in zip(text1, text2) if a == b)
      max_len = max(len(text1), len(text2))
      accuracy = round((common_chars / max_len) * 100, 1) if max_len > 0 else 0
    
    # Show results
    self.result_label.text = f"{result} - Similarity: {accuracy}%"
    Notification("Comparison complete", timeout=3).show()
    
    # Scroll to see results
    self.result_label.scroll_into_view()

  def open_server_test(self, **event_args):
    """Open the server test form"""
    open_form('ServerTest') 
    
  def account_link_click(self, **event_args):
    """Open the account management form"""
    open_form('AccountManagement') 

  def test_youtube_api(self, **event_args):
    """Test the YouTube API connection"""
    try:
      Notification("Testing YouTube API connection...", timeout=2).show()
      
      # Call the server test function
      result = anvil.server.call('test_youtube_api')
      
      # Display results
      status = result.get('status', 'unknown')
      message = result.get('message', 'No message')
      is_offline_mode = result.get('offline_mode', False)
      
      if is_offline_mode:
        # Show offline mode explanation
        alert_output = """
Offline Mode Activated

The application is running in offline mode to avoid server crashes. 
YouTube API calls have been disabled.

All searches will return demo videos that are generated
based on your search terms. No actual YouTube data will be displayed.

This is a workaround for the "Server code exited unexpectedly" error.
"""
        alert(alert_output)
        
        # Add a clear visual indicator of offline mode at the top of the page
        self.add_offline_mode_banner()
      elif status == 'success':
        alert(f"YouTube API Test: SUCCESS\n{message}")
      else:
        error_details = ""
        if 'error_details' in result:
          details = result['error_details']
          if details:
            error_details = f"\n\nError code: {details.get('code', 'unknown')}"
            if 'errors' in details and details['errors']:
              error_details += f"\nReason: {details['errors'][0].get('reason', 'unknown')}"
              error_details += f"\nMessage: {details['errors'][0].get('message', 'No message')}"
          
        alert(f"YouTube API Test: {status.upper()}\n{message}{error_details}")
      
    except Exception as e:
      alert(f"Error testing YouTube API: {str(e)}")
      print(f"API test error: {str(e)}")
      
  def add_offline_mode_banner(self):
    """Add a permanent offline mode banner to the top of the page"""
    # Check if we already have an offline banner
    if hasattr(self, 'offline_banner') and self.offline_banner:
      return
      
    # Create a banner at the very top of the page
    self.offline_banner = ColumnPanel()
    self.offline_banner.background = "#dc3545"  # Bootstrap danger red
    self.offline_banner.foreground = "white"
    self.offline_banner.padding = ("10px", "15px")
    self.offline_banner.margin = ("0", "0", "15px", "0")
    
    offline_title = Label(text="OFFLINE MODE ACTIVE")
    offline_title.bold = True
    offline_title.align = "center"
    
    offline_description = Label(text="YouTube API is disabled. All searches will return demo videos.")
    offline_description.align = "center"
    
    self.offline_banner.add_component(offline_title)
    self.offline_banner.add_component(offline_description)
    
    # Add it to the top of the form
    self.add_component(self.offline_banner, index=0)