/**
 * index.js
 * Main JavaScript file for YouTube functionality in Anvil
 */

// AnvilYouTube namespace
const AnvilYouTube = {
  /**
   * Initialize the YouTube functionality
   * @param {Object} options - Configuration options
   * @param {string} options.gridSelector - CSS selector for grid container
   * @param {string} options.playerSelector - CSS selector for player container
   * @param {string} options.defaultThumbnail - Default thumbnail URL or data URI
   */
  initialize: function(options) {
    console.log('Initializing AnvilYouTube with JavaScript');
    
    // Setup handlers
    this.setupCommunicationBridge();
  },

  /**
   * Set up communication bridge between JavaScript and Python
   */
  setupCommunicationBridge: function() {
    // Define a global object for Python to call into
    window.AnvilYouTube = {
      // Methods exposed to Python
      onVideoSearch: function(videos) {
        console.log('Received video search results:', videos);
        // Dispatch custom event for video search
        const event = new CustomEvent('anvil-youtube-search', {
          detail: { videos },
          bubbles: true,
          cancelable: true
        });
        document.dispatchEvent(event);
        return true;
      },
      
      onError: function(error) {
        console.error('YouTube error:', error);
        // Dispatch error event
        const event = new CustomEvent('anvil-youtube-error', {
          detail: { error },
          bubbles: true,
          cancelable: true
        });
        document.dispatchEvent(event);
        return true;
      }
    };
    
    console.log('Communication bridge set up between JavaScript and Python');
  }
};

// Make the namespace available globally
window.AnvilYouTube = AnvilYouTube;

// Notify that JavaScript is loaded
console.log('YouTube JavaScript module loaded'); 