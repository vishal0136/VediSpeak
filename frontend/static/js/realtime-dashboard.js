/**
 * Real-time Dashboard JavaScript
 * Handles live activity tracking, progress updates, and statistics display
 */

class RealtimeDashboard {
    constructor() {
        this.socket = null;
        this.updateInterval = null;
        this.sessionId = null;
        this.isSessionActive = false;
        
        this.init();
    }
    
    init() {
        // Initialize SocketIO if available
        if (typeof io !== 'undefined') {
            this.socket = io();
            this.setupSocketEvents();
        }
        
        // Initialize dashboard
        this.loadDashboardStats();
        this.setupEventListeners();
        this.startPeriodicUpdates();
        
        // Initialize user tracking
        this.initializeUserTracking();
    }
    
    setupSocketEvents() {
        if (!this.socket) return;
        
        this.socket.on('connect', () => {
            console.log('Connected to real-time dashboard');
            this.socket.emit('join_activity_room');
        });
        
        this.socket.on('activity_update', (data) => {
            this.handleActivityUpdate(data);
        });
        
        this.socket.on('progress_update', (data) => {
            this.handleProgressUpdate(data);
        });
        
        this.socket.on('live_stats_update', (data) => {
            this.updateDashboardDisplay(data);
        });
    }
    
    setupEventListeners() {
        // Module progress tracking
        document.addEventListener('moduleProgressUpdate', (event) => {
            this.updateModuleProgress(event.detail);
        });
        
        // Activity logging
        document.addEventListener('userActivity', (event) => {
            this.logActivity(event.detail);
        });
        
        // Session management
        document.addEventListener('sessionStart', (event) => {
            this.startSession(event.detail);
        });
        
        document.addEventListener('sessionEnd', (event) => {
            this.endSession();
        });
        
        // Page visibility for session management
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isSessionActive) {
                this.pauseSession();
            } else if (!document.hidden && this.isSessionActive) {
                this.resumeSession();
            }
        });
    }
    
    async initializeUserTracking() {
        try {
            const response = await fetch('/api/activity/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log('User tracking initialized');
            }
        } catch (error) {
            console.error('Error initializing user tracking:', error);
        }
    }
    
    async loadDashboardStats() {
        try {
            const response = await fetch('/api/activity/dashboard-stats');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateDashboardDisplay(data.data);
                this.updateActivityFeed();
                this.updateWeeklyChart();
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }
    
    updateDashboardDisplay(stats) {
        // Update basic stats
        const basicStats = stats.basic_stats || {};
        this.updateElement('total-study-hours', basicStats.total_study_hours || 0);
        this.updateElement('modules-completed', basicStats.modules_completed || 0);
        this.updateElement('total-xp-points', basicStats.total_xp_points || 0);
        this.updateElement('skill-level', basicStats.skill_level || 'Beginner');
        this.updateElement('current-streak', basicStats.current_streak || 0);
        this.updateElement('longest-streak', basicStats.longest_streak || 0);
        
        // Update today's stats
        const todayStats = stats.today_stats || {};
        this.updateElement('today-study-hours', todayStats.study_hours || 0);
        this.updateElement('today-xp-earned', todayStats.xp_earned || 0);
        this.updateElement('today-activities', todayStats.activities_count || 0);
        
        // Update weekly progress
        const weeklyProgress = stats.weekly_progress || {};
        this.updateProgressBar('weekly-study-progress', 
            weeklyProgress.study_minutes || 0, 
            weeklyProgress.study_goal || 300);
        this.updateProgressBar('weekly-modules-progress', 
            weeklyProgress.modules_completed || 0, 
            weeklyProgress.modules_goal || 2);
        this.updateProgressBar('weekly-practice-progress', 
            weeklyProgress.practice_sessions || 0, 
            weeklyProgress.practice_goal || 10);
        
        // Update skills
        if (stats.skills) {
            this.updateSkillsDisplay(stats.skills);
        }
        
        // Update active modules
        if (stats.active_modules) {
            this.updateActiveModules(stats.active_modules);
        }
        
        // Update streak info
        if (stats.streak_info) {
            this.updateStreakDisplay(stats.streak_info);
        }
    }
    
    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            if (typeof value === 'number' && value % 1 !== 0) {
                element.textContent = value.toFixed(1);
            } else {
                element.textContent = value;
            }
        }
    }
    
    updateProgressBar(elementId, current, goal) {
        const progressBar = document.getElementById(elementId);
        if (progressBar) {
            const percentage = goal > 0 ? Math.min((current / goal) * 100, 100) : 0;
            progressBar.style.width = percentage + '%';
            
            // Update text if there's a text element
            const textElement = document.getElementById(elementId + '-text');
            if (textElement) {
                textElement.textContent = `${current}/${goal}`;
            }
        }
    }
    
    updateSkillsDisplay(skills) {
        const skillsContainer = document.getElementById('skills-container');
        if (!skillsContainer) return;
        
        skillsContainer.innerHTML = '';
        
        skills.forEach(skill => {
            const skillElement = document.createElement('div');
            skillElement.className = 'skill-item glass p-4 rounded-lg';
            
            const progressPercentage = skill.xp_points % 100;
            
            skillElement.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="font-semibold text-white capitalize">${skill.skill_category}</span>
                    <span class="text-sm text-accent">Level ${skill.skill_level}</span>
                </div>
                <div class="progress-bar mb-2">
                    <div class="progress-fill bg-accent" style="width: ${progressPercentage}%"></div>
                </div>
                <div class="text-xs text-slate-400">${skill.xp_points} XP</div>
            `;
            
            skillsContainer.appendChild(skillElement);
        });
    }
    
    updateActiveModules(modules) {
        const modulesContainer = document.getElementById('active-modules-container');
        if (!modulesContainer) return;
        
        modulesContainer.innerHTML = '';
        
        modules.forEach(module => {
            const moduleElement = document.createElement('div');
            moduleElement.className = 'module-item glass p-3 rounded-lg hover:bg-white/5 transition cursor-pointer';
            moduleElement.onclick = () => window.location.href = `/learn/module/${module.module_id}`;
            
            moduleElement.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-white text-sm">${module.module_name}</span>
                    <span class="text-xs text-accent">${module.progress_percentage}%</span>
                </div>
                <div class="progress-bar thin">
                    <div class="progress-fill bg-accent" style="width: ${module.progress_percentage}%"></div>
                </div>
                <div class="text-xs text-slate-400 mt-1">${module.time_spent_minutes} min studied</div>
            `;
            
            modulesContainer.appendChild(moduleElement);
        });
    }
    
    updateStreakDisplay(streakInfo) {
        const streakContainer = document.getElementById('streak-container');
        if (!streakContainer) return;
        
        streakContainer.innerHTML = `
            <div class="text-center">
                <div class="text-3xl font-bold text-emerald-400 mb-1">${streakInfo.current_streak}</div>
                <div class="text-sm text-slate-400">Day Streak</div>
                <div class="mt-2 text-xs text-slate-500">Best: ${streakInfo.longest_streak} days</div>
            </div>
        `;
    }
    
    async updateActivityFeed() {
        try {
            const response = await fetch('/api/activity/live-feed?limit=10');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayActivityFeed(data.data);
            }
        } catch (error) {
            console.error('Error updating activity feed:', error);
        }
    }
    
    displayActivityFeed(activities) {
        const feedContainer = document.getElementById('activity-feed-container');
        if (!feedContainer) return;
        
        feedContainer.innerHTML = '';
        
        activities.forEach(activity => {
            const activityElement = document.createElement('div');
            activityElement.className = 'activity-item flex items-center gap-3 p-3 glass rounded-lg mb-2';
            
            const icon = this.getActivityIcon(activity.type);
            const color = this.getActivityColor(activity.type);
            
            activityElement.innerHTML = `
                <div class="w-8 h-8 rounded-full ${color} flex items-center justify-center">
                    <i class="fas ${icon} text-white text-sm"></i>
                </div>
                <div class="flex-1">
                    <div class="text-sm text-white">${activity.description}</div>
                    <div class="text-xs text-slate-400">${activity.time_ago}</div>
                </div>
                ${activity.xp_earned > 0 ? `<div class="text-xs text-accent">+${activity.xp_earned} XP</div>` : ''}
            `;
            
            feedContainer.appendChild(activityElement);
        });
    }
    
    getActivityIcon(activityType) {
        const icons = {
            'module_start': 'fa-play',
            'module_complete': 'fa-check-circle',
            'quiz_attempt': 'fa-question-circle',
            'quiz_pass': 'fa-trophy',
            'practice_session': 'fa-dumbbell',
            'skill_unlock': 'fa-star',
            'streak_milestone': 'fa-fire',
            'login': 'fa-sign-in-alt'
        };
        return icons[activityType] || 'fa-circle';
    }
    
    getActivityColor(activityType) {
        const colors = {
            'module_start': 'bg-blue-500',
            'module_complete': 'bg-emerald-500',
            'quiz_attempt': 'bg-purple-500',
            'quiz_pass': 'bg-amber-500',
            'practice_session': 'bg-indigo-500',
            'skill_unlock': 'bg-pink-500',
            'streak_milestone': 'bg-red-500',
            'login': 'bg-slate-500'
        };
        return colors[activityType] || 'bg-slate-500';
    }
    
    async updateWeeklyChart() {
        try {
            const response = await fetch('/api/activity/weekly-chart');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderWeeklyChart(data.data);
            }
        } catch (error) {
            console.error('Error updating weekly chart:', error);
        }
    }
    
    renderWeeklyChart(chartData) {
        const chartContainer = document.getElementById('weekly-chart-container');
        if (!chartContainer) return;
        
        // Simple bar chart implementation
        chartContainer.innerHTML = '';
        
        const maxValue = Math.max(...chartData.study_minutes, 1);
        
        chartData.labels.forEach((label, index) => {
            const barContainer = document.createElement('div');
            barContainer.className = 'flex flex-col items-center';
            
            const studyMinutes = chartData.study_minutes[index] || 0;
            const height = (studyMinutes / maxValue) * 100;
            
            barContainer.innerHTML = `
                <div class="w-8 bg-slate-700 rounded-t" style="height: 60px; position: relative;">
                    <div class="bg-accent rounded-t absolute bottom-0 w-full transition-all duration-500" 
                         style="height: ${height}%"></div>
                </div>
                <div class="text-xs text-slate-400 mt-1">${label}</div>
                <div class="text-xs text-accent">${Math.round(studyMinutes)}m</div>
            `;
            
            chartContainer.appendChild(barContainer);
        });
    }
    
    async logActivity(activityData) {
        try {
            const response = await fetch('/api/activity/log-activity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(activityData)
            });
            
            if (response.ok) {
                // Refresh stats after logging activity
                setTimeout(() => this.loadDashboardStats(), 1000);
            }
        } catch (error) {
            console.error('Error logging activity:', error);
        }
    }
    
    async updateModuleProgress(progressData) {
        try {
            const response = await fetch('/api/activity/update-module-progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(progressData)
            });
            
            if (response.ok) {
                // Refresh stats after updating progress
                setTimeout(() => this.loadDashboardStats(), 1000);
            }
        } catch (error) {
            console.error('Error updating module progress:', error);
        }
    }
    
    async startSession(sessionData = {}) {
        try {
            const response = await fetch('/api/activity/start-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sessionData)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.sessionId = data.session_id;
                this.isSessionActive = true;
                this.startSessionTimer();
            }
        } catch (error) {
            console.error('Error starting session:', error);
        }
    }
    
    async endSession() {
        if (!this.sessionId || !this.isSessionActive) return;
        
        try {
            const response = await fetch('/api/activity/end-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.isSessionActive = false;
                this.sessionId = null;
                this.stopSessionTimer();
                
                // Show session summary
                this.showSessionSummary(data.data);
                
                // Refresh stats
                setTimeout(() => this.loadDashboardStats(), 1000);
            }
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }
    
    startSessionTimer() {
        const timerElement = document.getElementById('session-timer');
        if (!timerElement) return;
        
        let seconds = 0;
        this.sessionTimer = setInterval(() => {
            seconds++;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    stopSessionTimer() {
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
            this.sessionTimer = null;
        }
    }
    
    showSessionSummary(sessionData) {
        // Show a notification or modal with session summary
        if (typeof LearningUtils !== 'undefined' && LearningUtils.showNotification) {
            LearningUtils.showNotification(
                `Session completed! ${sessionData.duration_minutes} minutes, +${sessionData.xp_earned} XP`,
                'success',
                5000
            );
        }
    }
    
    pauseSession() {
        // Pause session tracking when page is hidden
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
        }
    }
    
    resumeSession() {
        // Resume session tracking when page is visible
        if (this.isSessionActive) {
            this.startSessionTimer();
        }
    }
    
    startPeriodicUpdates() {
        // Update stats every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadQuickStats();
        }, 30000);
    }
    
    async loadQuickStats() {
        try {
            const response = await fetch('/api/activity/quick-stats');
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update only essential stats for performance
                this.updateElement('total-xp-points', data.data.total_xp);
                this.updateElement('current-streak', data.data.current_streak);
                this.updateElement('today-study-minutes', data.data.today_study_minutes);
                this.updateElement('skill-level', data.data.skill_level);
                this.updateElement('modules-completed', data.data.modules_completed);
            }
        } catch (error) {
            console.error('Error loading quick stats:', error);
        }
    }
    
    handleActivityUpdate(data) {
        // Handle real-time activity updates from WebSocket
        this.updateActivityFeed();
        this.loadQuickStats();
    }
    
    handleProgressUpdate(data) {
        // Handle real-time progress updates from WebSocket
        this.loadDashboardStats();
    }
    
    destroy() {
        // Cleanup when component is destroyed
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
        }
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        if (this.isSessionActive) {
            this.endSession();
        }
    }
}

// Global utility functions for triggering events
window.RealtimeTracker = {
    logActivity: (activityType, data = {}) => {
        document.dispatchEvent(new CustomEvent('userActivity', {
            detail: { activity_type: activityType, ...data }
        }));
    },
    
    updateProgress: (moduleId, progressData) => {
        document.dispatchEvent(new CustomEvent('moduleProgressUpdate', {
            detail: { module_id: moduleId, ...progressData }
        }));
    },
    
    startSession: (sessionType = 'study', moduleId = null) => {
        document.dispatchEvent(new CustomEvent('sessionStart', {
            detail: { session_type: sessionType, module_id: moduleId }
        }));
    },
    
    endSession: () => {
        document.dispatchEvent(new CustomEvent('sessionEnd'));
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dashboard-container') || document.body.classList.contains('dashboard-page')) {
        window.realtimeDashboard = new RealtimeDashboard();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.realtimeDashboard) {
        window.realtimeDashboard.destroy();
    }
});