/**
 * YouTubeGrid.ts
 * TypeScript implementation for YouTube grid display and management
 */

/**
 * Represent a YouTube video item
 */
interface VideoItem {
  id: string;
  title: string;
  thumbnail_url?: string;
  description?: string;
  published?: string;
  channel?: {
    id?: string;
    title?: string;
  };
}

/**
 * Configuration options for the YouTube grid
 */
interface GridOptions {
  containerSelector: string;
  defaultThumbnail: string;
  maxVideos?: number;
  columns?: number;
  onThumbnailClick?: (index: number, videoId: string) => void;
}

/**
 * The YouTube Grid class
 * Manages the display and interaction of YouTube video thumbnails
 */
class YouTubeGrid {
  private options: GridOptions;
  private videos: VideoItem[] = [];
  private container: HTMLElement | null = null;

  /**
   * Constructor
   * @param options - Configuration options
   */
  constructor(options: GridOptions) {
    this.options = {
      ...options,
      maxVideos: options.maxVideos || 12,
      columns: options.columns || 3
    };
    
    // Initialize the grid
    this.initialize();
  }

  /**
   * Initialize the grid component
   */
  private initialize(): void {
    // Find container element
    this.container = document.querySelector(this.options.containerSelector);
    if (!this.container) {
      console.error(`YouTubeGrid: Container element not found with selector ${this.options.containerSelector}`);
      return;
    }
    
    // Apply grid styling if needed
    this.applyGridStyling();
  }

  /**
   * Apply CSS Grid styles to the container
   */
  private applyGridStyling(): void {
    if (!this.container) return;
    
    // Apply grid layout
    this.container.style.display = 'grid';
    this.container.style.gridTemplateColumns = `repeat(auto-fill, minmax(240px, 1fr))`;
    this.container.style.gap = '20px';
    this.container.style.padding = '20px';
    this.container.style.width = '100%';
  }

  /**
   * Update the grid with new video data
   * @param videos - Array of video items to display
   */
  updateGrid(videos: VideoItem[]): void {
    this.videos = videos.slice(0, this.options.maxVideos);
    this.render();
  }

  /**
   * Create HTML for a thumbnail
   * @param video - The video item
   * @param index - The index in the videos array
   * @returns HTML string for the thumbnail
   */
  private createThumbnailHTML(video: VideoItem, index: number): string {
    const id = video.id || '';
    const title = video.title || 'Untitled video';
    const thumbnail = video.thumbnail_url || this.options.defaultThumbnail;
    
    return `
      <div class="thumbnail-container" data-index="${index}" data-video-id="${id}" onclick="handleThumbnailClick(${index})">
        <img src="${thumbnail}" alt="${title}" class="thumbnail-image" 
          onerror="this.onerror=null; this.src='${this.options.defaultThumbnail}'">
        <p class="video-title">${title}</p>
      </div>
    `;
  }

  /**
   * Create the empty state HTML
   * @returns HTML string for empty state
   */
  private createEmptyStateHTML(): string {
    return `
      <div style="text-align: center; padding: 40px; width: 100%;">
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 30px; background-color: #f8f9fa; display: inline-block; max-width: 600px;">
          <h3 style="color: #6c757d; margin-bottom: 15px;">No Videos Found</h3>
          <p style="color: #6c757d;">Enter a search term and connect to the YouTube API to display real video results.</p>
          <p style="color: #6c757d; font-size: 0.9em; margin-top: 15px;">This application does not display pre-loaded dummy videos.</p>
        </div>
      </div>
    `;
  }

  /**
   * Render the grid with current videos
   */
  private render(): void {
    if (!this.container) return;
    
    // Clear existing content
    this.container.innerHTML = '';
    
    // Show empty state if no videos
    if (this.videos.length === 0) {
      this.container.innerHTML = this.createEmptyStateHTML();
      return;
    }
    
    // Build thumbnails HTML
    let thumbnailsHTML = '';
    this.videos.forEach((video, index) => {
      thumbnailsHTML += this.createThumbnailHTML(video, index);
    });
    
    // Set all thumbnails at once
    this.container.innerHTML = thumbnailsHTML;
    
    // Add click handling if provided
    if (this.options.onThumbnailClick) {
      this.setupClickHandlers();
    }
  }

  /**
   * Set up click handlers for thumbnails
   */
  private setupClickHandlers(): void {
    if (!this.container) return;
    
    const thumbnails = this.container.querySelectorAll('.thumbnail-container');
    thumbnails.forEach((thumbnail) => {
      thumbnail.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const index = parseInt(target.getAttribute('data-index') || '0');
        const videoId = target.getAttribute('data-video-id') || '';
        
        if (this.options.onThumbnailClick) {
          this.options.onThumbnailClick(index, videoId);
        }
      });
    });
  }

  /**
   * Get current videos
   * @returns Array of current video items
   */
  getVideos(): VideoItem[] {
    return [...this.videos];
  }

  /**
   * Get video at specific index
   * @param index - The index to retrieve
   * @returns The video item or null if not found
   */
  getVideoAt(index: number): VideoItem | null {
    if (index >= 0 && index < this.videos.length) {
      return this.videos[index];
    }
    return null;
  }
}

// Export to global scope
(window as any).YouTubeGrid = YouTubeGrid; 