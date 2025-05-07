from ._anvil_designer import CompareTranscriptionTemplate
from anvil import *
import anvil.server
import anvil.users


class CompareTranscription(CompareTranscriptionTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Initialize language dropdown     a
    self.language_dropdown.items = [
      ('English', 'en'),
      ('Spanish', 'es'),
      ('French', 'fr'),
      ('German', 'de'),
      ('Portuguese', 'pt')
    ]
    self.language_dropdown.selected_value = 'en'
    
    # Initialize the video_id parameter if passed
    video_id = properties.get('video_id')
    if video_id:
      # Handle the video_id if needed
      self.load_video(video_id)
      
    # Test the server connection on load
    try:
      test_result = anvil.server.call('test_server_function')
      print(f"Server connection test: {test_result['message']}")
    except Exception as e:
      print(f"Server connection test failed: {str(e)}")

  def load_video(self, video_id):
    # This would be used to load a specific video by ID
    # For now, just show a notification
    Notification(f"Loading video with ID: {video_id}", timeout=3).show()

  def search_link_click(self, **event_args):
    """Show search section"""
    # No need to navigate, just scroll to search
    self.search_box.focus()
    
  def comparison_link_click(self, **event_args):
    """Show comparison section"""
    # No need to navigate, just scroll to comparison
    self.user_input_box.focus()

  def compare_button_click(self, **event_args):
    user_text = self.user_input_box.text
    official_text = self.official_input_box.text
    selected_lang = self.language_dropdown.selected_value or 'en'

    if not user_text or not official_text:
      alert("Please fill in both fields.")
      return

    try:
      # Attempt server comparison first
      try:
        Notification("Attempting server comparison...", timeout=1).show()
        # Set a short timeout to fail quickly if server has issues
        result = anvil.server.call("compare_transcriptions", user_text, official_text, _timeout=2)
        
        if result and 'html' in result and 'stats' in result:
          # If we got a valid result, display it
          self.comparison_output.content = result["html"]
          self.accuracy_label.text = (
            f"Accuracy: {result['stats']['accuracy']}% — "
            f"{result['stats']['correct']} correct, "
            f"{result['stats']['incorrect']} wrong, "
            f"{result['stats']['missing']} missing"
          )
          Notification("Server comparison complete", timeout=2).show()
          return
      except Exception as e:
        # Just silently fall back to client-side
        print(f"Server comparison error (expected): {str(e)}")
      
      # Fall back to client-side comparison
      self._client_side_comparison(user_text, official_text)
      
    except Exception as e:
      # Handle any unexpected errors
      alert(f"Error during comparison: {str(e)}")
      # Still try to show something
      try:
        self._client_side_comparison(user_text, official_text)
      except:
        # Last resort
        self.comparison_output.content = "Error performing comparison"
        self.accuracy_label.text = "Could not calculate accuracy"

  def search_button_click(self, **event_args):
    query = self.search_box.text
    if not query:
      alert("Please enter a search term.")
      return
      
    try:
      # Attempt server search but be ready to fall back quickly
      try:
        Notification("Attempting server search...", timeout=1).show()
        # Set a short timeout to fail quickly if server has issues
        results = anvil.server.call("search_youtube_videos", query, _timeout=2)
        if results:
          # If we got results, process them
          self.results_repeater.items = results
          Notification(f"Found {len(results)} results", timeout=2).show()
          return
      except Exception as e:
        # Silently fail and fall back to client-side
        print(f"Server error (expected): {str(e)}")
      
      # If we're here, server search failed - use client-side search
      Notification("Using client-side search", timeout=2).show()
      self._client_side_search(query)
      
    except Exception as e:
      # Handle any other errors
      alert(f"Error during search: {str(e)}")
      # Still try to show something
      self._client_side_search(query)
      
  def _client_side_search(self, query):
    """Fallback client-side search when server is unavailable"""
    # Create mock results without calling the server
    # Don't try to manipulate the repeater panel directly
    
    # Just clear the parent panel that contains the repeater
    parent_panel = self.content_panel
    parent_panel.clear()
    
    # Re-add the search components
    parent_panel.add_component(self.language_dropdown)
    parent_panel.add_component(self.search_box)
    parent_panel.add_component(self.search_button)
    
    # Create a results panel for mock results
    results_panel = ColumnPanel()
    results_panel.spacing_above = "large"
    
    # Add a heading
    results_panel.add_component(Label(text=f"Results for: {query} (Client-side mock)", role="heading"))
    
    # Add some mock results
    for i in range(3):
      # Create a card for each mock result
      card = ColumnPanel()
      card.spacing_above = "medium"
      card.spacing_below = "medium"
      card.border = "1px solid #ddd"
      
      # Add mock title and info
      title = Label(text=f"Mock result {i+1} for {query}", role="heading")
      title.bold = True
      info = Label(text="This is a client-side only mock result (no server call)")
      
      card.add_component(title)
      card.add_component(info)
      
      results_panel.add_component(card)
    
    # Add the results panel to the content panel
    parent_panel.add_component(results_panel)
    
    # Re-add the comparison components
    parent_panel.add_component(self.user_input_box)
    parent_panel.add_component(self.compare_button)
    parent_panel.add_component(self.comparison_output)
    parent_panel.add_component(self.accuracy_label)
    parent_panel.add_component(self.official_input_box)
    
    # Show a notification
    Notification("Found 3 mock results (client-side only)", timeout=3).show()
    
  def _client_side_comparison(self, text1, text2):
    """Fallback client-side comparison when server is unavailable"""
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
    self.comparison_output.content = f"<span style='color:blue'>CLIENT-SIDE COMPARISON:</span><br>{result}"
    self.accuracy_label.text = f"Similarity: {accuracy}% (client-side calculation)"
    Notification("Completed client-side comparison", timeout=3).show()

  def user_input_box_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    pass

  def language_dropdown_change(self, **event_args):
    """Called when the language is changed"""
    selected = self.language_dropdown.selected_value
    Notification(f"Language set to: {selected}", timeout=2).show()
