/**
 * index.ts
 * Main TypeScript file for YouTube functionality in Anvil
 */

// Re-export all the components to ensure they're available
import './PlaceholderHandler';
import './YouTubePlayer';
import './YouTubeGrid';

/**
 * Create a namespace for our Anvil TypeScript functionality
 */
namespace AnvilYouTube {
  export interface AnvilYouTubeOptions {
    gridSelector: string;
    playerSelector: string;
    defaultThumbnail: string;
  }

  /**
   * Initialize the YouTube functionality
   * @param options Configuration options
   */
  export function initialize(options: AnvilYouTubeOptions): void {
    console.log('Initializing AnvilYouTube with TypeScript');
    
    // Setup handlers
    setupCommunicationBridge();
  }

  /**
   * Set up communication bridge between TypeScript and Python
   */
  function setupCommunicationBridge(): void {
    // Define a global object for Python to call into
    (window as any).AnvilYouTube = {
      // Methods exposed to Python
      onVideoSearch: (videos: any[]) => {
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
      
      onError: (error: string) => {
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
    
    console.log('Communication bridge set up between TypeScript and Python');
  }
}

// Make the namespace available globally
(window as any).AnvilYouTube = AnvilYouTube;

// Notify that TypeScript is loaded
console.log('YouTube TypeScript module loaded'); 