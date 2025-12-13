/**
 * VediSpeak ISL Learning Platform - Shared JavaScript Utilities
 */

// Reveal Animation on Scroll
function initRevealAnimation() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach(el => {
    observer.observe(el);
  });
}

// Tab Switching Utility
function showContent(section) {
  // Hide all content sections
  document.querySelectorAll('.content-section').forEach(el => {
    el.classList.add('hidden');
  });
  
  document.querySelectorAll('.week-content').forEach(el => {
    el.classList.add('hidden');
  });

  // Remove active state from all tabs
  document.querySelectorAll('[id$="Tab"]').forEach(tab => {
    tab.classList.remove('active', 'text-white', 'border-accent');
    tab.classList.add('text-slate-400', 'border-transparent');
  });

  // Show selected content section
  const contentEl = document.getElementById(section + 'Content');
  if (contentEl) {
    contentEl.classList.remove('hidden');
  }

  // Activate selected tab
  const tabEl = document.getElementById(section + 'Tab');
  if (tabEl) {
    tabEl.classList.remove('text-slate-400', 'border-transparent');
    tabEl.classList.add('active', 'text-white', 'border-accent');
  }
}

// Week Content Switching (for module learning)
function showWeekContent(section) {
  // Hide all week content sections
  document.querySelectorAll('.week-content').forEach(el => {
    el.classList.add('hidden');
  });

  // Remove active state from all week tabs
  document.querySelectorAll('.week-tab').forEach(tab => {
    tab.classList.remove('active', 'text-white');
    tab.classList.add('text-slate-400');
  });

  // Show selected week content
  const contentEl = document.getElementById(section + 'Content');
  if (contentEl) {
    contentEl.classList.remove('hidden');
  }

  // Activate selected tab
  const tabEl = document.getElementById(section + 'Tab');
  if (tabEl) {
    tabEl.classList.remove('text-slate-400');
    tabEl.classList.add('active', 'text-white');
  }
}

// Notification System
function showNotification(message, type = 'info', duration = 3000) {
  const notification = document.createElement('div');
  const bgColor = type === 'success' ? 'bg-emerald-600' : 
                  type === 'error' ? 'bg-red-600' : 
                  type === 'warning' ? 'bg-amber-600' : 'bg-blue-600';
  
  notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${bgColor} text-white transition-opacity duration-300`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Fade out and remove
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, duration);
}

// Progress Bar Animation
function animateProgressBar(element, targetWidth, duration = 1000) {
  if (!element) return;
  
  let startWidth = 0;
  const startTime = performance.now();
  
  function animate(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    const currentWidth = startWidth + (targetWidth - startWidth) * progress;
    element.style.width = currentWidth + '%';
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }
  
  requestAnimationFrame(animate);
}

// Module Preview Function
function previewModule(moduleId) {
  const moduleNames = {
    1: "ISL Alphabet & Fingerspelling",
    2: "Numbers & Mathematical Concepts", 
    3: "Family & Relationships",
    4: "Colors, Shapes & Objects",
    5: "Time & Calendar Concepts",
    6: "Basic Grammar & Sentence Structure",
    7: "Daily Activities & Routines",
    8: "Emotions & Feelings",
    9: "Places & Directions",
    10: "Food & Health",
    11: "Education & Work",
    12: "Advanced Grammar & Discourse"
  };
  
  const moduleName = moduleNames[moduleId] || 'Module ' + moduleId;
  
  showNotification(`Preview: ${moduleName}`, 'info', 5000);
  
  // Could be enhanced to show a proper modal instead of alert
  console.log('Module preview requested for:', moduleId, moduleName);
}

// Certification Info Function
function showCertificationInfo() {
  const certInfo = `ISLRTC Certification Program

📜 Foundation Level (Modules 1-6):
• 40-60 hours of study
• Basic ISL proficiency
• Government recognized certificate

🏆 Intermediate Level (Modules 7-12):
• 50-70 hours of study
• Advanced communication skills
• Professional qualification

👨‍🏫 Instructor Qualification:
• Additional training program
• Teaching methodology
• Certification to teach ISL

All certificates are issued by ISLRTC and recognized by Government of India institutions.`;

  // For now using alert, could be enhanced with a proper modal
  alert(certInfo);
}

// Utility function to format time
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Utility function to debounce function calls
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Initialize all common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize reveal animations
  initRevealAnimation();
  
  // Add click handlers for common elements
  document.addEventListener('click', function(e) {
    // Handle tab clicks
    if (e.target.matches('[data-tab]')) {
      const section = e.target.getAttribute('data-tab');
      showContent(section);
    }
    
    // Handle week tab clicks
    if (e.target.matches('[data-week-tab]')) {
      const section = e.target.getAttribute('data-week-tab');
      showWeekContent(section);
    }
  });
});

// Export functions for use in other scripts
window.LearningUtils = {
  showContent,
  showWeekContent,
  showNotification,
  animateProgressBar,
  previewModule,
  showCertificationInfo,
  formatTime,
  debounce
};