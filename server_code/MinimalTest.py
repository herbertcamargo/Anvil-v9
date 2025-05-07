import anvil.server
import sys

@anvil.server.callable
def minimal_test():
  """Diagnostic test function"""
  # Get Python version and platform info
  python_version = sys.version
  platform_info = sys.platform
  
  # Return diagnostic info
  return {
    "status": "ok",
    "python_version": python_version,
    "platform": platform_info
  }

@anvil.server.callable
def ping():
  """Most minimal possible function - just returns a string"""
  return "pong" 