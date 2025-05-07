from ._anvil_designer import html_top_barTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.js

# Register this as a Custom Component
if not hasattr(anvil, 'html_top_bar'):
  anvil.html_top_bar = html_top_barTemplate

class html_top_bar(html_top_barTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Get HTML elements
    self.setup_js_handlers()

    # Any code you write here will run before the form opens.

  def setup_js_handlers(self):
    """Set up JavaScript event handlers for navigation links"""
    # Get the HTML elements
    home_link = anvil.js.get_dom_node(self).querySelector('#home-link')
    search_link = anvil.js.get_dom_node(self).querySelector('#search-link')
    compare_link = anvil.js.get_dom_node(self).querySelector('#compare-link')
    account_link = anvil.js.get_dom_node(self).querySelector('#account-link')
    menu_button = anvil.js.get_dom_node(self).querySelector('#menu-button')
    nav_links = anvil.js.get_dom_node(self).querySelector('.nav-links')
    
    # Add click event handlers
    if home_link:
      home_link.addEventListener('click', lambda event: self.navigate('home'))
    if search_link:
      search_link.addEventListener('click', lambda event: self.navigate('search'))
    if compare_link:
      compare_link.addEventListener('click', lambda event: self.navigate('compare'))
    if account_link:
      account_link.addEventListener('click', lambda event: self.navigate('account'))
    
    # Mobile menu toggle
    if menu_button and nav_links:
      menu_button.addEventListener('click', lambda event: self.toggle_mobile_menu(nav_links))
      
  def navigate(self, section):
    """Handle navigation to different sections"""
    current_form = get_open_form()
    
    if hasattr(current_form, f"{section}_link_click"):
      # Call the method on the current form if it exists
      getattr(current_form, f"{section}_link_click")()
    elif section == 'home':
      # Default to opening the home page
      open_form('MinimalApp')
    elif section == 'account':
      # Open account management page
      open_form('AccountManagement')
      
  def toggle_mobile_menu(self, nav_links):
    """Toggle the mobile menu visibility"""
    current_display = nav_links.style.display
    if current_display == 'none' or not current_display:
      nav_links.style.display = 'flex'
      nav_links.style.position = 'absolute'
      nav_links.style.top = '60px'
      nav_links.style.right = '0'
      nav_links.style.flexDirection = 'column'
      nav_links.style.backgroundColor = '#2c3e50'
      nav_links.style.padding = '1rem'
      nav_links.style.width = '200px'
    else:
      nav_links.style.display = 'none'
