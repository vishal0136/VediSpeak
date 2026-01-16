/**
 * Loading Manager - Centralized loading state management
 * Provides consistent loading indicators across the application
 */

class LoadingManager {
  /**
   * Show loading overlay on an element
   * @param {string|HTMLElement} element - Element ID or DOM element
   * @param {string} message - Loading message to display
   */
  static show(element, message = 'Loading...') {
    const el = typeof element === 'string' ? document.getElementById(element) : element;
    
    if (!el) {
      console.warn('LoadingManager: Element not found', element);
      return;
    }
    
    // Store original position if not already set
    const originalPosition = window.getComputedStyle(el).position;
    if (originalPosition === 'static') {
      el.style.position = 'relative';
      el.dataset.originalPosition = 'static';
    }
    
    // Disable interactions
    el.style.pointerEvents = 'none';
    el.dataset.loadingActive = 'true';
    
    // Create loading overlay
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p class="loading-text">${message}</p>
      </div>
    `;
    
    el.appendChild(overlay);
  }
  
  /**
   * Hide loading overlay from an element
   * @param {string|HTMLElement} element - Element ID or DOM element
   */
  static hide(element) {
    const el = typeof element === 'string' ? document.getElementById(element) : element;
    
    if (!el) {
      console.warn('LoadingManager: Element not found', element);
      return;
    }
    
    // Remove loading overlay
    const overlay = el.querySelector('.loading-overlay');
    if (overlay) {
      overlay.remove();
    }
    
    // Restore interactions
    el.style.pointerEvents = '';
    
    // Restore original position if it was static
    if (el.dataset.originalPosition === 'static') {
      el.style.position = '';
      delete el.dataset.originalPosition;
    }
    
    delete el.dataset.loadingActive;
  }
  
  /**
   * Show loading state on a button
   * @param {string|HTMLElement} button - Button ID or DOM element
   * @param {string} originalText - Original button text (optional, will be restored)
   */
  static showButton(button, originalText = null) {
    const btn = typeof button === 'string' ? document.getElementById(button) : button;
    
    if (!btn) {
      console.warn('LoadingManager: Button not found', button);
      return;
    }
    
    // Store original text if not provided
    if (!originalText) {
      btn.dataset.originalText = btn.innerHTML;
    } else {
      btn.dataset.originalText = originalText;
    }
    
    // Add loading class
    btn.classList.add('btn-loading');
    btn.disabled = true;
  }
  
  /**
   * Hide loading state from a button
   * @param {string|HTMLElement} button - Button ID or DOM element
   */
  static hideButton(button) {
    const btn = typeof button === 'string' ? document.getElementById(button) : button;
    
    if (!btn) {
      console.warn('LoadingManager: Button not found', button);
      return;
    }
    
    // Remove loading class
    btn.classList.remove('btn-loading');
    btn.disabled = false;
    
    // Restore original text
    if (btn.dataset.originalText) {
      btn.innerHTML = btn.dataset.originalText;
      delete btn.dataset.originalText;
    }
  }
  
  /**
   * Show a skeleton loader
   * @param {string|HTMLElement} container - Container ID or DOM element
   * @param {number} count - Number of skeleton items
   * @param {string} type - Type of skeleton (text, title, avatar, card)
   */
  static showSkeleton(container, count = 3, type = 'text') {
    const el = typeof container === 'string' ? document.getElementById(container) : container;
    
    if (!el) {
      console.warn('LoadingManager: Container not found', container);
      return;
    }
    
    // Store original content
    el.dataset.originalContent = el.innerHTML;
    
    // Generate skeleton items
    let skeletonHTML = '';
    for (let i = 0; i < count; i++) {
      switch (type) {
        case 'title':
          skeletonHTML += '<div class="skeleton skeleton-title"></div>';
          break;
        case 'avatar':
          skeletonHTML += '<div class="skeleton skeleton-avatar"></div>';
          break;
        case 'card':
          skeletonHTML += `
            <div class="glass p-4 rounded-lg mb-4">
              <div class="skeleton skeleton-title mb-3"></div>
              <div class="skeleton skeleton-text"></div>
              <div class="skeleton skeleton-text"></div>
              <div class="skeleton skeleton-text" style="width: 60%;"></div>
            </div>
          `;
          break;
        default: // text
          skeletonHTML += '<div class="skeleton skeleton-text"></div>';
      }
    }
    
    el.innerHTML = skeletonHTML;
  }
  
  /**
   * Hide skeleton loader and restore content
   * @param {string|HTMLElement} container - Container ID or DOM element
   * @param {string} newContent - New content to display (optional)
   */
  static hideSkeleton(container, newContent = null) {
    const el = typeof container === 'string' ? document.getElementById(container) : container;
    
    if (!el) {
      console.warn('LoadingManager: Container not found', container);
      return;
    }
    
    // Restore original content or set new content
    if (newContent) {
      el.innerHTML = newContent;
    } else if (el.dataset.originalContent) {
      el.innerHTML = el.dataset.originalContent;
      delete el.dataset.originalContent;
    }
  }
  
  /**
   * Show a global loading overlay (full screen)
   * @param {string} message - Loading message
   */
  static showGlobal(message = 'Loading...') {
    // Remove existing global loader if any
    this.hideGlobal();
    
    const overlay = document.createElement('div');
    overlay.id = 'globalLoadingOverlay';
    overlay.className = 'fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[9999]';
    overlay.innerHTML = `
      <div class="text-center">
        <div class="spinner spinner-lg mb-4"></div>
        <p class="text-white text-lg">${message}</p>
      </div>
    `;
    
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
  }
  
  /**
   * Hide global loading overlay
   */
  static hideGlobal() {
    const overlay = document.getElementById('globalLoadingOverlay');
    if (overlay) {
      overlay.remove();
      document.body.style.overflow = '';
    }
  }
  
  /**
   * Wrap an async function with loading state
   * @param {Function} asyncFn - Async function to wrap
   * @param {string|HTMLElement} element - Element to show loading on
   * @param {string} message - Loading message
   * @returns {Function} Wrapped function
   */
  static wrap(asyncFn, element, message = 'Loading...') {
    return async function(...args) {
      try {
        LoadingManager.show(element, message);
        const result = await asyncFn.apply(this, args);
        return result;
      } finally {
        LoadingManager.hide(element);
      }
    };
  }
  
  /**
   * Wrap a button click with loading state
   * @param {Function} asyncFn - Async function to execute
   * @param {string|HTMLElement} button - Button element
   * @returns {Function} Wrapped function
   */
  static wrapButton(asyncFn, button) {
    return async function(...args) {
      try {
        LoadingManager.showButton(button);
        const result = await asyncFn.apply(this, args);
        return result;
      } finally {
        LoadingManager.hideButton(button);
      }
    };
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LoadingManager;
}

// Make available globally
window.LoadingManager = LoadingManager;
