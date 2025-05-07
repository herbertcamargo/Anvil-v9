from ._anvil_designer import ServerTestTemplate
from anvil import *
import anvil.server
import anvil.js
from anvil.js.window import HTMLElement
import sys

# Import our TypeScript-enhanced YouTube module
sys.path.append('client_code')
import YouTubeModule

class ServerTest(ServerTestTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Enable global exception reporting for all JavaScript callbacks
    anvil.js.report_all_exceptions(True)
    
    # Add global placeholder image handler
    self.add_placeholder_image_handler()
    
    # Set up YouTube functionality with our TypeScript-enhanced module
    self.setup_typescript_youtube()
    
    # Add debug functions
    self.debug_panel = FlowPanel()
    self.debug_button = Button(text="Debug HTML", role="outlined-button")
    self.debug_button.set_event_handler('click', self.debug_html)
    self.debug_panel.add_component(self.debug_button)
    
    # Add test grid button
    self.test_grid_button = Button(text="Create Test Grid", role="primary-color")
    self.test_grid_button.set_event_handler('click', self.create_test_grid)
    self.debug_panel.add_component(self.test_grid_button)
    
    # Add the debug panel 
    self.add_component(self.debug_panel, index=4)  # Place it after the search section heading
    
    # Try to call server functions to see if they work
    try:
      # Try to call test function
      self.result_label.text = "Testing server functions..."
      result = anvil.server.call('hello')
      self.result_label.text = f"Server Response: {result}"
      self.status_label.text = "Server functions are working!"
      self.status_label.foreground = "#4CAF50"  # Green color
    except Exception as e:
      # Show error if server functions don't work
      self.result_label.text = f"Error: {str(e)}"
      self.status_label.text = "Server functions are NOT working!"
      self.status_label.foreground = "#F44336"  # Red color
      
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
    self.youtube_integration.update_videos(test_videos)
    
    # Scroll to the grid container
    self.yt_grid_container.scroll_into_view()
    
  def debug_html(self, **event_args):
    """Debug HTML structure and components"""
    try:
      # Check if HTML components exist
      html_status = "HTML components:\n"
      html_status += f"YouTube Integration exists: {hasattr(self, 'youtube_integration')}\n"
      
      # Check containers
      container_status = "Containers:\n"
      container_status += f"Grid container exists: {self.yt_grid_container is not None}\n"
      container_status += f"Player container exists: {self.yt_player_container is not None}\n"
      
      # Show complete status
      alert(f"{html_status}\n{container_status}")
      
    except Exception as e:
      alert(f"Debug error: {str(e)}")
      
  def setup_typescript_youtube(self):
    """Set up YouTube functionality using TypeScript-based module"""
    # Initialize the YouTube integration with our containers
    self.youtube_integration = YouTubeModule.YouTubeIntegration(
        form=self,
        grid_container=self.yt_grid_container,
        player_container=self.yt_player_container
    )
    
    # Store videos in the integration
    self.videos = []
    
  def search_button_click(self, **event_args):
    """Handle YouTube search with server function fallback"""
    query = self.search_box.text
    if not query:
      alert("Please enter a search term")
      return
      
    self.search_status.text = "Searching..."
    self.search_status.foreground = "#2196F3"  # Blue color
    
    try:
      # Try to call server function for search
      self.search_status.text = "Trying server search..."
      
      try:
        # Attempt to call the real YouTube API through server function
        videos = anvil.server.call('search_youtube', query)
        
        if videos and len(videos) > 0:
          self.search_status.text = f"Found {len(videos)} videos via YouTube API!"
          self.search_status.foreground = "#4CAF50"  # Green color
          
          # Create a separate notification showing we're updating thumbnails
          Notification("Loading thumbnails from YouTube API...", timeout=2).show()
          
          # Update the YouTube grid with API results using our TypeScript-enhanced module
          self.youtube_integration.update_videos(videos)
          
          # Show a notification of success
          Notification(f"Successfully added {len(videos)} videos to grid", timeout=3).show()
        else:
          # No videos found from the API
          self.search_status.text = f"No videos found for '{query}' via YouTube API"
          self.search_status.foreground = "#FF9800"  # Orange color
          
          # Update with empty grid
          self.youtube_integration.update_videos([])
          
          # Show notification
          Notification("No videos found for your search", timeout=3).show()
          
      except Exception as server_error:
        # API call failed - show the error but don't use dummy data
        self.search_status.text = f"YouTube API error: {str(server_error)}"
        self.search_status.foreground = "#FF9800"  # Orange color
        
        # Update with empty grid
        self.youtube_integration.update_videos([])
        
        # Show notification about API requirement
        Notification("YouTube API connection required - no dummy data will be shown", timeout=4).show()
      
      # Scroll to see results
      self.yt_grid_container.scroll_into_view()
      
    except Exception as e:
      # Show error notification if search completely fails
      self.search_status.text = f"Search failed: {str(e)}"
      self.search_status.foreground = "#F44336"  # Red color
      alert(f"Error during search: {str(e)}")
      print(f"Search error: {str(e)}")
    
  def back_home_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    # Clean up our TypeScript resources
    if hasattr(self, 'youtube_integration'):
      self.youtube_integration.cleanup()
      
    open_form('MinimalApp')

  def test_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    try:
      self.result_label.text = "Testing server connection..."
      result = anvil.server.call('minimal_test')
      
      # Format the result nicely
      if isinstance(result, dict):
        result_text = f"Status: {result.get('status', 'unknown')}\n"
        for key, value in result.items():
          if key != 'status':
            result_text += f"{key}: {value}\n"
        self.result_label.text = result_text
      else:
        self.result_label.text = f"Server test result: {result}"
        
      self.result_label.foreground = "#00aa00"  # Green for success
    except Exception as e:
      self.result_label.text = f"Error: {str(e)}"
      self.result_label.foreground = "#aa0000"  # Red for error
      
  def advanced_test_button_click(self, **event_args):
    """This method is called when the advanced test button is clicked"""
    try:
      self.result_label.text = "Pinging server..."
      # Try the simplest possible server call without any imports
      ping_result = anvil.server.call('ping')
      self.result_label.text = f"Ping result: {ping_result}"
      self.result_label.foreground = "#00aa00"  # Green for success
    except Exception as e:
      self.result_label.text = f"Ping error: {str(e)}"
      self.result_label.foreground = "#aa0000"  # Red for error 

  def return_to_main_app(self, **event_args):
    """Return to the main application"""
    try:
      self.result_label.text = "Opening minimal app..."
      
      # Clean up our TypeScript resources
      if hasattr(self, 'youtube_integration'):
        self.youtube_integration.cleanup()
        
      open_form('MinimalApp')
    except Exception as e:
      self.result_label.text = f"Error opening minimal app: {str(e)}"
      self.result_label.foreground = "#aa0000"  # Red for error 