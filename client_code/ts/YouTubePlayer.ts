/**
 * YouTubePlayer.ts
 * TypeScript implementation of YouTube player functionality for Anvil
 */

// Define interfaces for type safety
interface VideoData {
  id: string;
  title: string;
  thumbnail_url?: string;
}

interface ThumbnailClickEvent extends CustomEvent {
  detail: {
    index: number;
    videoId?: string;
  };
}

interface YouTubePlayerInterface {
  loadVideo(videoId: string, title: string): Promise<{videoId: string, title: string}>;
  setupThumbnailHandlers(): void;
  handleThumbnailClick(index: number): void;
}

/**
 * YouTubePlayer implementation
 * Handles video loading and thumbnail interaction
 */
class YouTubePlayerImpl implements YouTubePlayerInterface {
  /**
   * Load a YouTube video by ID and update the player
   * @param videoId - The YouTube video ID
   * @param title - The video title
   * @returns Promise resolving to video info
   */
  loadVideo(videoId: string, title: string): Promise<{videoId: string, title: string}> {
    return new Promise((resolve, reject) => {
      try {
        console.log(`Loading video: ${videoId} - ${title}`);
        // Additional implementation could go here
        resolve({videoId, title});
      } catch (error) {
        console.error(`Error loading video: ${error}`);
        reject(error);
      }
    });
  }

  /**
   * Set up thumbnail click handlers
   */
  setupThumbnailHandlers(): void {
    // This will be called to initialize the thumbnail handlers
    console.log("Setting up YouTube thumbnail handlers");
    
    // The global handler function - needs to be accessible from HTML
    (window as any).handleThumbnailClick = (index: number): void => {
      this.handleThumbnailClick(index);
    };
  }

  /**
   * Handle thumbnail click events
   * @param index - The index of the clicked thumbnail
   */
  handleThumbnailClick(index: number): void {
    const event: ThumbnailClickEvent = new CustomEvent('thumbnail-click', { 
      detail: { index },
      bubbles: true, 
      cancelable: true 
    }) as ThumbnailClickEvent;
    
    document.dispatchEvent(event);
  }
}

/**
 * Create and export the YouTube Player instance
 */
(window as any).YouTubePlayer = new YouTubePlayerImpl(); 