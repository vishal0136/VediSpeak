/**
 * Module Learning JavaScript
 * Handles module-specific functionality including tab switching, video player controls, 
 * quiz logic, YouTube API integration, and real-time progress tracking.
 */

// Global variables
let currentProgress = 0;
let startTime = Date.now();
let timeSpent = 0;
let currentQuestionIndex = 0;
let quizAnswers = [];
let quizTimer = null;
let sessionTimer = null;

// YouTube and NPTEL integration
let youtubePlayer = null;
let currentVideoIndex = 0;
let playbackSpeed = 1;
let captionsEnabled = false;
let detectionActive = false;

// ISLRTC YouTube video IDs (sample - replace with actual video IDs)
const moduleVideos = {
  1: ['dQw4w9WgXcQ', 'dQw4w9WgXcQ', 'dQw4w9WgXcQ', 'dQw4w9WgXcQ'], // Module 1 videos
  2: ['dQw4w9WgXcQ', 'dQw4w9WgXcQ', 'dQw4w9WgXcQ', 'dQw4w9WgXcQ'], // Module 2 videos
  // Add more modules as needed
};

const videoTitles = [
  'Introduction & Overview',
  'Basic Hand Shapes', 
  'Movement Patterns',
  'Practice Examples'
];

// Socket.IO connection (if available)
let socket = null;
if (typeof io !== 'undefined') {
  socket = io();
}

// Initialize module when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeModule();
  startSessionTimer();
  loadModuleNavigation();
  
  // Socket events (if socket is available)
  if (socket) {
    socket.on('connect', () => {
      socket.emit('join_learning_room');
      socket.emit('start_module_session', {
        module_id: window.moduleData?.id,
        course_id: window.moduleData?.course_id
      });
    });
    
    socket.on('progress_updated', (data) => {
      updateProgressDisplay(data.progress);
    });
  }
});

/**
 * Initialize the module with appropriate content type
 */
function initializeModule() {
  // Get data from window globals set by template
  const moduleData = window.moduleData || {};
  const progressData = window.progressData || {};
  
  currentProgress = progressData.progress_percentage || 0;
  timeSpent = progressData.time_spent_minutes || 0;
  
  // Initialize based on content type
  if (moduleData.content_type === 'interactive') {
    loadInteractiveContent();
  } else if (moduleData.content_type === 'quiz' && window.quizData) {
    loadQuizContent();
  } else if (moduleData.content_type === 'practice') {
    loadPracticeContent();
  }
  
  updateProgressCircle(currentProgress);
  initializeYouTubeAPI();
  
  // Set up event listeners
  setupEventListeners();
}

/**
 * Set up event listeners for module interactions
 */
function setupEventListeners() {
  // Action buttons
  const markCompleteBtn = document.getElementById('markComplete');
  const saveProgressBtn = document.getElementById('saveProgress');
  
  if (markCompleteBtn) {
    markCompleteBtn.addEventListener('click', () => {
      updateProgress(100);
    });
  }
  
  if (saveProgressBtn) {
    saveProgressBtn.addEventListener('click', () => {
      updateProgress(currentProgress);
    });
  }
}

/**
 * Tab switching functionality
 */
function showWeekContent(section) {
  // Hide all content sections
  document.querySelectorAll('.content-section, .week-content').forEach(el => {
    el.classList.add('hidden');
  });
  
  // Remove active state from all tabs
  document.querySelectorAll('.week-tab').forEach(tab => {
    tab.classList.remove('active', 'text-white');
    tab.classList.add('text-slate-400');
  });
  
  // Show selected content section
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

/**
 * YouTube API Integration
 */
function initializeYouTubeAPI() {
  // Load YouTube IFrame API if not already loaded
  if (!window.YT) {
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  }
}

function onYouTubeIframeAPIReady() {
  // This function is called by YouTube API when ready
  console.log('YouTube API Ready');
}

function loadYouTubeVideo(videoIndex) {
  const moduleData = window.moduleData || {};
  const videosData = window.videosData || [];
  
  // Use provided videos data or fallback to sample videos
  let videoId;
  if (videosData.length > 0 && videosData[videoIndex]) {
    videoId = videosData[videoIndex].id;
  } else {
    const moduleId = moduleData.id || 1;
    const videos = moduleVideos[moduleId] || moduleVideos[1];
    videoId = videos[videoIndex] || videos[0];
  }
  
  currentVideoIndex = videoIndex;
  
  const playerContainer = document.getElementById('youtubePlayer');
  if (playerContainer) {
    playerContainer.innerHTML = `
      <iframe 
        width="100%" 
        height="100%" 
        src="https://www.youtube.com/embed/${videoId}?enablejsapi=1&rel=0&modestbranding=1" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
      </iframe>
    `;
  }
  
  // Update video title
  const titleEl = document.getElementById('currentVideoTitle');
  if (titleEl) {
    if (videosData.length > 0 && videosData[videoIndex]) {
      titleEl.textContent = videosData[videoIndex].title;
    } else {
      titleEl.textContent = videoTitles[videoIndex] || `Video ${videoIndex + 1}`;
    }
  }
  
  // Update playlist UI
  updatePlaylistUI(videoIndex);
  
  // Track video start
  trackVideoProgress(videoIndex);
}

function updatePlaylistUI(activeIndex) {
  document.querySelectorAll('.video-item').forEach((item, index) => {
    item.classList.remove('bg-red-500/10', 'border-red-500/20');
    item.classList.add('glass');
    
    const icon = item.querySelector('i.fab');
    const lockIcon = item.querySelector('i.fas.fa-lock');
    const playIcon = item.querySelector('i.fas.fa-play-circle');
    
    if (index === activeIndex) {
      item.classList.remove('glass');
      item.classList.add('bg-red-500/10', 'border-red-500/20');
      if (icon) {
        icon.classList.remove('text-slate-400');
        icon.classList.add('text-red-400');
      }
      if (playIcon) {
        playIcon.classList.remove('text-slate-500');
        playIcon.classList.add('text-red-400');
      }
    } else if (index <= currentProgress / 25) { // Unlock based on progress
      if (lockIcon) {
        lockIcon.classList.remove('fa-lock');
        lockIcon.classList.add('fa-check-circle', 'text-emerald-400');
      }
    }
  });
}

function selectVideo(videoIndex) {
  loadYouTubeVideo(videoIndex);
}

function previousVideo() {
  if (currentVideoIndex > 0) {
    loadYouTubeVideo(currentVideoIndex - 1);
  }
}

function nextVideo() {
  const videosData = window.videosData || [];
  const maxVideos = videosData.length > 0 ? videosData.length : videoTitles.length;
  
  if (currentVideoIndex < maxVideos - 1) {
    loadYouTubeVideo(currentVideoIndex + 1);
    updateProgress(Math.min(100, currentProgress + 25)); // 25% per video
  }
}

function toggleCaptions() {
  captionsEnabled = !captionsEnabled;
  showNotification(captionsEnabled ? 'Captions enabled' : 'Captions disabled', 'info');
}

function toggleSpeed() {
  const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];
  const currentIndex = speeds.indexOf(playbackSpeed);
  playbackSpeed = speeds[(currentIndex + 1) % speeds.length];
  
  const speedTextEl = document.getElementById('speedText');
  if (speedTextEl) {
    speedTextEl.textContent = playbackSpeed + 'x';
  }
  
  showNotification(`Playback speed: ${playbackSpeed}x`, 'info');
}

function toggleLike() {
  const likeBtn = document.querySelector('.fa-thumbs-up');
  if (likeBtn) {
    likeBtn.classList.toggle('text-slate-400');
    likeBtn.classList.toggle('text-blue-400');
    showNotification('Video liked!', 'success');
  }
}

function toggleBookmark() {
  const bookmarkBtn = document.querySelector('.fa-bookmark');
  if (bookmarkBtn) {
    bookmarkBtn.classList.toggle('text-slate-400');
    bookmarkBtn.classList.toggle('text-amber-400');
    showNotification('Video bookmarked!', 'success');
  }
}

function trackVideoProgress(videoIndex) {
  // Simulate video progress tracking
  let progress = 0;
  const interval = setInterval(() => {
    progress += 1;
    
    const progressEl = document.getElementById('videoProgress');
    if (progressEl) {
      progressEl.style.width = progress + '%';
    }
    
    const currentTimeEl = document.getElementById('currentTime');
    if (currentTimeEl) {
      const minutes = Math.floor(progress * 5.3 / 60); // Assuming 5.3 min video
      const seconds = Math.floor((progress * 5.3) % 60);
      currentTimeEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    
    if (progress >= 100) {
      clearInterval(interval);
      // Auto-advance to next video
      setTimeout(() => {
        const videosData = window.videosData || [];
        const maxVideos = videosData.length > 0 ? videosData.length : videoTitles.length;
        if (currentVideoIndex < maxVideos - 1) {
          nextVideo();
        }
      }, 2000);
    }
  }, 3000); // Update every 3 seconds for demo
}

/**
 * Live AI Detection Functions
 */
function startLiveDetection() {
  if (detectionActive) {
    stopLiveDetection();
    return;
  }
  
  detectionActive = true;
  const button = document.querySelector('button[onclick="startLiveDetection()"]');
  if (button) {
    button.innerHTML = '<i class="fas fa-stop mr-2"></i>Stop Detection';
    button.classList.remove('bg-emerald-600', 'hover:bg-emerald-500');
    button.classList.add('bg-red-600', 'hover:bg-red-500');
  }
  
  // Show detection results
  const resultsEl = document.getElementById('detectionResults');
  if (resultsEl) {
    resultsEl.classList.remove('hidden');
  }
  
  // Simulate live detection
  simulateLiveDetection();
  
  showNotification('Live detection started! Practice signs now.', 'success');
}

function stopLiveDetection() {
  detectionActive = false;
  const button = document.querySelector('button[onclick="startLiveDetection()"]');
  if (button) {
    button.innerHTML = '<i class="fas fa-camera mr-2"></i>Start Detection';
    button.classList.remove('bg-red-600', 'hover:bg-red-500');
    button.classList.add('bg-emerald-600', 'hover:bg-emerald-500');
  }
  
  showNotification('Detection stopped.', 'info');
}

function simulateLiveDetection() {
  if (!detectionActive) return;
  
  // Simulate changing accuracy and detection results
  const accuracy = Math.floor(Math.random() * 20) + 75; // 75-95%
  const signsDetected = Math.floor(Math.random() * 5) + 10; // 10-15
  
  const accuracyEl = document.getElementById('detectionAccuracy');
  const signsEl = document.getElementById('signsDetected');
  
  if (accuracyEl) accuracyEl.textContent = accuracy + '%';
  if (signsEl) signsEl.textContent = signsDetected + '/15';
  
  setTimeout(simulateLiveDetection, 2000); // Update every 2 seconds
}

/**
 * Quiz Functions
 */
function startQuiz(type) {
  if (type === 'weekly') {
    const assessmentStart = document.getElementById('assessmentStart');
    const quizInterface = document.getElementById('quizInterface');
    
    if (assessmentStart) assessmentStart.classList.add('hidden');
    if (quizInterface) quizInterface.classList.remove('hidden');
    
    startQuizTimer();
  }
}

function startQuizAssessment() {
  startQuiz('weekly');
}

function startQuizTimer() {
  const quizData = window.quizData || {};
  let timeLeft = (quizData.time_limit || 15) * 60; // Default 15 minutes
  
  quizTimer = setInterval(() => {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    
    const timerEl = document.getElementById('quizTimer');
    if (timerEl) {
      timerEl.textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    if (timeLeft <= 0) {
      clearInterval(quizTimer);
      submitQuizAssessment();
    }
    timeLeft--;
  }, 1000);
}

function selectQuizOption(optionIndex) {
  // Clear previous selections
  document.querySelectorAll('.quiz-option').forEach(option => {
    option.classList.remove('border-emerald-400', 'selected');
    option.classList.add('border-slate-600');
    const dot = option.querySelector('.option-dot');
    if (dot) dot.classList.add('hidden');
  });
  
  // Select new option
  const selectedOption = document.querySelectorAll('.quiz-option')[optionIndex];
  if (selectedOption) {
    selectedOption.classList.remove('border-slate-600');
    selectedOption.classList.add('border-emerald-400', 'selected');
    const dot = selectedOption.querySelector('.option-dot');
    if (dot) dot.classList.remove('hidden');
  }
  
  // Enable next button
  const nextBtn = document.getElementById('nextQuestionBtn');
  if (nextBtn) nextBtn.disabled = false;
  
  // Update question navigator
  const currentQ = document.querySelector('.grid.grid-cols-10 .bg-emerald-500');
  if (currentQ) {
    currentQ.classList.remove('bg-emerald-500');
    currentQ.classList.add('bg-blue-500'); // Mark as answered
  }
  
  // Store answer
  quizAnswers[currentQuestionIndex] = optionIndex;
}

function goToQuestion(questionIndex) {
  currentQuestionIndex = questionIndex;
  loadQuizQuestion(questionIndex);
}

function submitQuizAssessment() {
  if (quizTimer) {
    clearInterval(quizTimer);
  }
  
  // Calculate score (simulate)
  const score = Math.floor(Math.random() * 30) + 70; // 70-100%
  const passed = score >= 70;
  
  // Show results
  const quizInterface = document.getElementById('quizInterface');
  if (quizInterface) {
    quizInterface.innerHTML = `
      <div class="text-center py-12">
        <div class="text-6xl mb-6">${passed ? '🎉' : '📚'}</div>
        <h3 class="text-2xl font-bold text-white mb-4">${passed ? 'Excellent Work!' : 'Keep Practicing!'}</h3>
        <p class="text-slate-300 mb-6">${passed ? 'You passed the NPTEL assessment!' : 'You can retake the quiz after reviewing the material.'}</p>
        
        <div class="grid grid-cols-3 gap-6 max-w-md mx-auto mb-8">
          <div class="glass p-4 rounded-lg">
            <div class="text-2xl font-bold text-emerald-400">${score}%</div>
            <div class="text-sm text-slate-400">Your Score</div>
          </div>
          <div class="glass p-4 rounded-lg">
            <div class="text-2xl font-bold text-blue-400">70%</div>
            <div class="text-sm text-slate-400">Pass Mark</div>
          </div>
          <div class="glass p-4 rounded-lg">
            <div class="text-2xl font-bold text-purple-400">${passed ? 'A' : 'B'}</div>
            <div class="text-sm text-slate-400">Grade</div>
          </div>
        </div>
        
        <div class="flex gap-4 justify-center">
          ${passed ? 
            '<button onclick="proceedToNextModule()" class="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition"><i class="fas fa-arrow-right mr-2"></i>Next Module</button>' :
            '<button onclick="retakeAssessment()" class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition"><i class="fas fa-redo mr-2"></i>Retake Quiz</button>'
          }
          <button onclick="viewDetailedResults()" class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition">
            <i class="fas fa-chart-bar mr-2"></i>View Results
          </button>
        </div>
      </div>
    `;
  }
  
  if (passed) {
    updateProgress(100, score);
  }
  
  const currentScoreEl = document.getElementById('currentScore');
  if (currentScoreEl) {
    currentScoreEl.textContent = score + '%';
  }
}

function retakeAssessment() {
  const quizInterface = document.getElementById('quizInterface');
  const assessmentStart = document.getElementById('assessmentStart');
  
  if (quizInterface) quizInterface.classList.add('hidden');
  if (assessmentStart) assessmentStart.classList.remove('hidden');
  
  // Reset quiz state
  currentQuestionIndex = 0;
  quizAnswers = [];
}

function proceedToNextModule() {
  const moduleData = window.moduleData || {};
  const nextModuleId = (moduleData.id || 1) + 1;
  window.location.href = `/learn/module/${nextModuleId}`;
}

function viewDetailedResults() {
  showNotification('Detailed results will be available in your dashboard.', 'info');
}

function reviewQuiz() {
  showNotification('Quiz review functionality coming soon!', 'info');
}

function startPracticalTest() {
  showNotification('Practical test will start your camera for sign recognition.', 'info');
}

function practiceMode() {
  showNotification('Practice mode activated! Use the AI detection feature.', 'success');
}

/**
 * Progress and Session Management
 */
function startSessionTimer() {
  sessionTimer = setInterval(() => {
    timeSpent++;
    
    const timeSpentEl = document.getElementById('timeSpent');
    if (timeSpentEl) {
      const minutes = Math.floor(timeSpent);
      timeSpentEl.textContent = minutes + 'min';
    }
    
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const mins = Math.floor(elapsed / 60);
    const secs = elapsed % 60;
    
    const timerEl = document.getElementById('timer');
    if (timerEl) {
      timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
  }, 60000); // Update every minute
}

function updateProgress(newProgress, quizScore = null) {
  currentProgress = newProgress;
  
  // Update UI
  updateProgressCircle(newProgress);
  
  const moduleProgressEl = document.getElementById('moduleProgress');
  const moduleProgressSidebarEl = document.getElementById('moduleProgressSidebar');
  
  if (moduleProgressEl) moduleProgressEl.textContent = newProgress + '%';
  if (moduleProgressSidebarEl) moduleProgressSidebarEl.textContent = newProgress + '%';
  
  // Send to server
  const moduleData = window.moduleData || {};
  if (moduleData.id) {
    fetch(`/api/progress/module/${moduleData.id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        progress_percentage: newProgress,
        time_spent_minutes: timeSpent,
        quiz_score: quizScore
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        showNotification('Progress saved! Keep it up! 💾', 'success');
      }
    })
    .catch(error => {
      console.error('Error saving progress:', error);
      showNotification('Oops! Couldn\'t save. Try again?', 'error');
    });
  }
  
  // Emit real-time update (if socket available)
  if (socket) {
    socket.emit('update_session_progress', {
      module_id: moduleData.id,
      progress: newProgress,
      time_spent: timeSpent
    });
  }
}

function updateProgressCircle(progress) {
  const circle = document.getElementById('progressCircle');
  const percent = document.getElementById('progressPercent');
  
  if (circle) {
    const circumference = 2 * Math.PI * 28; // radius = 28
    const offset = circumference - (progress / 100) * circumference;
    circle.style.strokeDashoffset = offset;
  }
  
  if (percent) {
    percent.textContent = Math.round(progress) + '%';
  }
}

function updateProgressDisplay(progressData) {
  if (progressData) {
    updateProgress(progressData.progress_percentage || 0, progressData.quiz_score);
  }
}

/**
 * Content Loading Functions
 */
function loadInteractiveContent() {
  // Implementation for interactive content
  console.log('Loading interactive content...');
}

function loadQuizContent() {
  const quizData = window.quizData;
  if (!quizData || !quizData.questions) return;
  
  const totalQuestionsEl = document.getElementById('totalQuestions');
  if (totalQuestionsEl) {
    totalQuestionsEl.textContent = quizData.questions.length;
  }
  
  loadQuizQuestion(0);
  
  // Start quiz timer if applicable
  if (quizData.time_limit_minutes) {
    startQuizTimer(quizData.time_limit_minutes * 60);
  }
}

function loadQuizQuestion(index) {
  const quizData = window.quizData;
  if (!quizData || !quizData.questions || !quizData.questions[index]) return;
  
  const question = quizData.questions[index];
  const questionTextEl = document.getElementById('questionText');
  const optionsContainer = document.getElementById('optionsContainer');
  
  if (questionTextEl) {
    questionTextEl.textContent = question.text;
  }
  
  if (optionsContainer) {
    optionsContainer.innerHTML = question.options.map((option, i) => `
      <div class="quiz-option p-4 rounded-lg border border-slate-600 hover:border-emerald-400 transition cursor-pointer" 
           onclick="selectQuizOption(${i})" data-option="${i}">
        <div class="flex items-center gap-3">
          <div class="w-6 h-6 rounded-full border-2 border-slate-400 flex items-center justify-center">
            <div class="w-3 h-3 rounded-full bg-emerald-400 hidden option-dot"></div>
          </div>
          <span class="text-white">${option}</span>
        </div>
      </div>
    `).join('');
  }
  
  // Update question counter
  const currentQuestionEl = document.getElementById('currentQuestion');
  if (currentQuestionEl) {
    currentQuestionEl.textContent = index + 1;
  }
  
  // Update progress bar
  const quizProgressEl = document.getElementById('quizProgress');
  if (quizProgressEl) {
    const progress = ((index + 1) / quizData.questions.length) * 100;
    quizProgressEl.style.width = progress + '%';
  }
  
  // Update navigation buttons
  const prevBtn = document.getElementById('prevQuestionBtn');
  const nextBtn = document.getElementById('nextQuestionBtn');
  
  if (prevBtn) prevBtn.disabled = index === 0;
  if (nextBtn) {
    nextBtn.style.display = index === quizData.questions.length - 1 ? 'none' : 'block';
  }
  
  // Restore previous answer if exists
  if (quizAnswers[index] !== undefined) {
    selectQuizOption(quizAnswers[index]);
  }
}

function loadPracticeContent() {
  // Implementation for practice content
  console.log('Loading practice content...');
}

function loadModuleNavigation() {
  // This would load other modules in the course for navigation
  // Implementation depends on course structure
  console.log('Loading module navigation...');
}

/**
 * Utility Functions
 */
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
    type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
  } text-white`;
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (sessionTimer) clearInterval(sessionTimer);
  if (quizTimer) clearInterval(quizTimer);
});

// Export functions for global access
window.showWeekContent = showWeekContent;
window.loadYouTubeVideo = loadYouTubeVideo;
window.selectVideo = selectVideo;
window.previousVideo = previousVideo;
window.nextVideo = nextVideo;
window.toggleCaptions = toggleCaptions;
window.toggleSpeed = toggleSpeed;
window.toggleLike = toggleLike;
window.toggleBookmark = toggleBookmark;
window.startLiveDetection = startLiveDetection;
window.stopLiveDetection = stopLiveDetection;
window.startQuiz = startQuiz;
window.startQuizAssessment = startQuizAssessment;
window.selectQuizOption = selectQuizOption;
window.goToQuestion = goToQuestion;
window.submitQuizAssessment = submitQuizAssessment;
window.retakeAssessment = retakeAssessment;
window.proceedToNextModule = proceedToNextModule;
window.viewDetailedResults = viewDetailedResults;
window.reviewQuiz = reviewQuiz;
window.startPracticalTest = startPracticalTest;
window.practiceMode = practiceMode;