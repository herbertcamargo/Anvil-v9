/**
 * YouTubeGrid.js
 * JavaScript implementation for YouTube grid display and management
 */

/**
 * The YouTube Grid class
 * Manages the display and interaction of YouTube video thumbnails
 */
class YouTubeGrid {
  /**
   * Constructor
   * @param {Object} options - Configuration options
   * @param {string} options.containerSelector - CSS selector for the grid container
   * @param {string} options.defaultThumbnail - Default thumbnail URL or data URI
   * @param {number} options.maxVideos - Maximum number of videos to display
   * @param {number} options.columns - Number of columns in the grid
   * @param {Function} options.onThumbnailClick - Click handler for thumbnails
   */
  constructor(options) {
    this.options = {
      ...options,
      maxVideos: options.maxVideos || 12,
      columns: options.columns || 3
    };
    this.videos = [];
    this.container = null;
    
    // Initialize the grid
    this.initialize();
  }

  /**
   * Initialize the grid component
   */
  initialize() {
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
  applyGridStyling() {
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
   * @param {Array} videos - Array of video items to display
   */
  updateGrid(videos) {
    this.videos = videos.slice(0, this.options.maxVideos);
    this.render();
  }

  /**
   * Create HTML for a thumbnail
   * @param {Object} video - The video item
   * @param {number} index - The index in the videos array
   * @returns {string} HTML string for the thumbnail
   */
  createThumbnailHTML(video, index) {
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
   * @returns {string} HTML string for empty state
   */
  createEmptyStateHTML() {
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
  render() {
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
  setupClickHandlers() {
    if (!this.container) return;
    
    const thumbnails = this.container.querySelectorAll('.thumbnail-container');
    thumbnails.forEach((thumbnail) => {
      thumbnail.addEventListener('click', (e) => {
        const target = e.currentTarget;
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
   * @returns {Array} Array of current video items
   */
  getVideos() {
    return [...this.videos];
  }

  /**
   * Get video at specific index
   * @param {number} index - The index to retrieve
   * @returns {Object|null} The video item or null if not found
   */
  getVideoAt(index) {
    if (index >= 0 && index < this.videos.length) {
      return this.videos[index];
    }
    return null;
  }
}

// Export to global scope
window.YouTubeGrid = YouTubeGrid; 