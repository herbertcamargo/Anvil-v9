from ._anvil_designer import TranscriptionPracticeTemplate
from anvil import *
import anvil.server
import anvil.users

class TranscriptionPractice(TranscriptionPracticeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def form_show(self, **event_args):
    """This method is called when the form is shown on the screen"""
    pass
    
  def compare_button_click(self, **event_args):
    """This method is called when the compare button is clicked"""
    from ..CompareTranscription import CompareTranscription
    open_form('CompareTranscription') 