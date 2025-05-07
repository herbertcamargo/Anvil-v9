/**
 * PlaceholderHandler.ts
 * TypeScript implementation for handling and blocking placeholder.com images
 */

interface PlaceholderOptions {
  avatarPlaceholder: string;
  defaultWidth: number;
  defaultHeight: number;
}

/**
 * PlaceholderHandler class
 * Handles intercepting and replacing placeholder.com images
 */
class PlaceholderHandler {
  private options: PlaceholderOptions;
  private observer: MutationObserver | null = null;

  /**
   * Constructor
   * @param options - Configuration options for the placeholder handler
   */
  constructor(options: PlaceholderOptions) {
    this.options = {
      avatarPlaceholder: options.avatarPlaceholder,
      defaultWidth: options.defaultWidth || 40,
      defaultHeight: options.defaultHeight || 40
    };
  }

  /**
   * Initialize the placeholder handling system
   */
  initialize(): void {
    console.log('Initializing placeholder image blocking system');
    this.interceptNetworkRequests();
    this.processExistingImages();
    this.setupMutationObserver();
    this.unregisterServiceWorkers();
  }

  /**
   * Block network requests to placeholder.com
   */
  private interceptNetworkRequests(): void {
    // Intercept fetch requests
    const originalFetch = window.fetch;
    window.fetch = (url: RequestInfo | URL, options?: RequestInit): Promise<Response> => {
      if (url && url.toString().includes('placeholder.com')) {
        console.log('Blocked fetch request to placeholder.com:', url);
        return Promise.resolve(new Response(
          new Blob([''], {type: 'text/plain'}),
          {status: 200, statusText: 'Blocked by Anvil'}
        ));
      }
      return originalFetch.apply(window, [url, options as any]);
    };
    
    // Intercept XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method: string, url: string | URL, ...args: any[]): void {
      if (url && url.toString().includes('placeholder.com')) {
        console.log('Blocked XHR request to placeholder.com:', url);
        this.abort();
        return;
      }
      // Since TypeScript is strict about the arguments, use any to bypass type checking for this method call
      (originalOpen as any).apply(this, [method, url, ...args]);
    };
  }

  /**
   * Generate placeholder SVG data URI
   * @param width - Width of the placeholder
   * @param height - Height of the placeholder
   * @returns Data URI for the placeholder
   */
  private generatePlaceholder(width: number, height: number): string {
    // For 40x40 images, use a simple grey box without text
    if (width === 40 && height === 40) {
      return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}' viewBox='0 0 ${width} ${height}'%3E%3Crect width='${width}' height='${height}' fill='%23cccccc'/%3E%3C/svg%3E`;
    } else {
      // For larger images, include dimensions text
      const fontSize = Math.max(12, Math.min(24, width/10));
      return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}' viewBox='0 0 ${width} ${height}'%3E%3Crect width='${width}' height='${height}' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='${fontSize}' text-anchor='middle' fill='%23666666'%3E${width}x${height}%3C/text%3E%3C/svg%3E`;
    }
  }

  /**
   * Replace image source with placeholder if it's from placeholder.com
   * @param img - The image element to process
   */
  private replaceImgSrc(img: HTMLImageElement): void {
    if (img.src && img.src.includes('placeholder.com')) {
      // Extract dimensions from URL if possible
      const match = img.src.match(/placeholder\.com\/(\d+)x(\d+)/);
      const width = match ? parseInt(match[1]) : this.options.defaultWidth;
      const height = match ? parseInt(match[2]) : this.options.defaultHeight;
      
      // Replace with appropriate SVG
      img.src = this.generatePlaceholder(width, height);
      
      // Prevent further loading attempts
      img.setAttribute('data-original-src', 'blocked-placeholder');
    }
  }

  /**
   * Process all existing images on the page
   */
  private processExistingImages(): void {
    const images = document.querySelectorAll('img');
    images.forEach((img: HTMLImageElement) => this.replaceImgSrc(img));
  }

  /**
   * Set up mutation observer to catch dynamically added images
   */
  private setupMutationObserver(): void {
    this.observer = new MutationObserver((mutations: MutationRecord[]) => {
      mutations.forEach((mutation: MutationRecord) => {
        // Handle added nodes
        if (mutation.addedNodes) {
          mutation.addedNodes.forEach((node: Node) => {
            // Process the node itself if it's an image
            if (node.nodeName === 'IMG') this.replaceImgSrc(node as HTMLImageElement);
            
            // Process any images inside the node
            if ((node as HTMLElement).querySelectorAll) {
              const images = (node as HTMLElement).querySelectorAll('img');
              images.forEach((img: HTMLImageElement) => this.replaceImgSrc(img));
            }
          });
        }
        
        // Handle attribute changes (src changes)
        if (
          mutation.type === 'attributes' && 
          mutation.attributeName === 'src' && 
          mutation.target.nodeName === 'IMG'
        ) {
          this.replaceImgSrc(mutation.target as HTMLImageElement);
        }
      });
    });
    
    // Start observing the document
    this.observer.observe(document.documentElement, { 
      childList: true, 
      subtree: true,
      attributes: true,
      attributeFilter: ['src']
    });
  }

  /**
   * Unregister service workers that might interfere
   */
  private unregisterServiceWorkers(): void {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        registrations.forEach((registration) => {
          if (registration.scope.includes(window.location.origin)) {
            registration.unregister();
          }
        });
      });
    }
  }

  /**
   * Clean up resources when done
   */
  cleanup(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }
}

// Export the PlaceholderHandler class to the global scope
(window as any).PlaceholderHandler = PlaceholderHandler; 