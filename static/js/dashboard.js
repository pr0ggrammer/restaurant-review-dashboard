/**
 * Restaurant Review Dashboard - JavaScript Module
 * Handles UI interactions, data loading, and chart management
 */

class DashboardManager {
    constructor() {
        this.charts = {};
        this.currentInterval = 'monthly';
        this.isLoading = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // DOM elements
        this.elements = {
            loadingOverlay: document.getElementById('loading-overlay'),
            errorOverlay: document.getElementById('error-overlay'),
            errorMessage: document.getElementById('error-message'),
            refreshBtn: document.getElementById('refresh-btn'),
            retryBtn: document.getElementById('retry-btn'),
            timeInterval: document.getElementById('time-interval'),
            
            // Status indicators
            overviewStatus: document.getElementById('overview-status'),
            trendsStatus: document.getElementById('trends-status'),
            volumeStatus: document.getElementById('volume-status'),
            sentimentStatus: document.getElementById('sentiment-status'),
            themesStatus: document.getElementById('themes-status'),
            distributionStatus: document.getElementById('distribution-status'),
            
            // Content containers
            totalReviews: document.getElementById('total-reviews'),
            averageRating: document.getElementById('average-rating'),
            sentimentScore: document.getElementById('sentiment-score'),
            helpfulVotes: document.getElementById('helpful-votes'),
            themesContainer: document.getElementById('themes-container'),
            sentimentSummary: document.getElementById('sentiment-summary'),
            ratingDistribution: document.getElementById('rating-distribution')
        };
        
        this.init();
    }
    
    init() {
        console.log('Initializing Restaurant Review Dashboard...');
        
        // Bind event listeners
        this.bindEvents();
        
        // Initialize charts
        this.initializeCharts();
        
        // Load initial data
        this.loadDashboardData();
    }
    
    bindEvents() {
        // Refresh button
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => {
                this.loadDashboardData();
            });
        }
        
        // Retry button
        if (this.elements.retryBtn) {
            this.elements.retryBtn.addEventListener('click', () => {
                this.hideError();
                this.loadDashboardData();
            });
        }
        
        // Time interval selector
        if (this.elements.timeInterval) {
            this.elements.timeInterval.addEventListener('change', (e) => {
                this.currentInterval = e.target.value;
                this.loadDashboardData();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.loadDashboardData();
            }
        });
    }
    
    async loadDashboardData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        this.setAllStatusLoading();
        
        try {
            // Load data in parallel
            const [metricsData, sentimentData] = await Promise.all([
                this.loadMetrics(),
                this.loadSentiment()
            ]);
            
            // Update UI with loaded data
            this.updateOverviewMetrics(metricsData);
            this.updateCharts(metricsData);
            this.updateSentimentAnalysis(sentimentData);
            this.updateThemes(metricsData.themes || []);
            this.updateRatingDistribution(metricsData.overall_metrics?.rating_distribution || {});
            
            this.setAllStatusSuccess();
            this.retryCount = 0;
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.handleError(error);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    async loadMetrics() {
        const response = await fetch(`/api/metrics?interval=${this.currentInterval}&num=100`);
        if (!response.ok) {
            throw new Error(`Metrics API error: ${response.status} ${response.statusText}`);
        }
        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Failed to load metrics');
        }
        return result.data;
    }
    
    async loadSentiment() {
        const response = await fetch('/api/sentiment?num=100');
        if (!response.ok) {
            throw new Error(`Sentiment API error: ${response.status} ${response.statusText}`);
        }
        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Failed to load sentiment data');
        }
        return result.data;
    }
    
    updateOverviewMetrics(data) {
        const metrics = data.overall_metrics || {};
        
        this.updateElement(this.elements.totalReviews, metrics.total_reviews || 0);
        this.updateElement(this.elements.averageRating, 
            metrics.average_rating ? `${metrics.average_rating}★` : '--');
        this.updateElement(this.elements.helpfulVotes, metrics.total_helpful_votes || 0);
        
        // Calculate sentiment score (placeholder)
        const sentimentScore = metrics.average_rating ? 
            Math.round((metrics.average_rating / 5) * 100) : 0;
        this.updateElement(this.elements.sentimentScore, `${sentimentScore}%`);
    }
    
    updateSentimentAnalysis(data) {
        const percentages = data.sentiment_percentages || {};
        
        // Update sentiment summary
        const positiveEl = document.getElementById('positive-percentage');
        const negativeEl = document.getElementById('negative-percentage');
        const neutralEl = document.getElementById('neutral-percentage');
        
        if (positiveEl) positiveEl.textContent = `${percentages.positive || 0}%`;
        if (negativeEl) negativeEl.textContent = `${percentages.negative || 0}%`;
        if (neutralEl) neutralEl.textContent = `${percentages.neutral || 0}%`;
        
        // Update sentiment chart
        this.updateSentimentChart(data);
    }
    
    updateThemes(themes) {
        if (!this.elements.themesContainer) return;
        
        if (!themes || themes.length === 0) {
            this.elements.themesContainer.innerHTML = '<p class="loading-text">No themes found</p>';
            return;
        }
        
        const themesHTML = themes.map(theme => `
            <div class="theme-tag">
                ${theme.theme}
                <span class="theme-frequency">${theme.frequency}</span>
            </div>
        `).join('');
        
        this.elements.themesContainer.innerHTML = themesHTML;
    }
    
    updateRatingDistribution(distribution) {
        if (!this.elements.ratingDistribution) return;
        
        const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
        
        ['5_star', '4_star', '3_star', '2_star', '1_star'].forEach((rating, index) => {
            const ratingNum = 5 - index;
            const count = distribution[rating] || 0;
            const percentage = total > 0 ? (count / total) * 100 : 0;
            
            const barEl = this.elements.ratingDistribution.querySelector(`[data-rating="${ratingNum}"]`);
            if (barEl) {
                const fillEl = barEl.querySelector('.bar-fill');
                const countEl = barEl.querySelector('.rating-count');
                
                if (fillEl) fillEl.style.width = `${percentage}%`;
                if (countEl) countEl.textContent = count;
            }
        });
    }
    
    initializeCharts() {
        // Chart.js default configuration
        Chart.defaults.color = 'rgba(255, 255, 255, 0.8)';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        Chart.defaults.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        
        // Initialize placeholder charts
        this.initRatingTrendsChart();
        this.initVolumeChart();
        this.initSentimentChart();
    }
    
    initRatingTrendsChart() {
        const ctx = document.getElementById('rating-trends-chart');
        if (!ctx) return;
        
        this.charts.ratingTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Average Rating',
                    data: [],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    initVolumeChart() {
        const ctx = document.getElementById('review-volume-chart');
        if (!ctx) return;
        
        this.charts.volume = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Review Count',
                    data: [],
                    backgroundColor: 'rgba(79, 172, 254, 0.6)',
                    borderColor: 'rgba(79, 172, 254, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    initSentimentChart() {
        const ctx = document.getElementById('sentiment-chart');
        if (!ctx) return;
        
        this.charts.sentiment = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(107, 114, 128, 0.8)'
                    ],
                    borderColor: [
                        'rgba(16, 185, 129, 1)',
                        'rgba(239, 68, 68, 1)',
                        'rgba(107, 114, 128, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    updateCharts(data) {
        // Update rating trends chart
        if (this.charts.ratingTrends && data.rating_trends) {
            const labels = data.rating_trends.map(item => item.date);
            const ratings = data.rating_trends.map(item => item.average_rating);
            
            this.charts.ratingTrends.data.labels = labels;
            this.charts.ratingTrends.data.datasets[0].data = ratings;
            this.charts.ratingTrends.update();
        }
        
        // Update volume chart
        if (this.charts.volume && data.volume_data) {
            const labels = data.volume_data.map(item => item.date);
            const volumes = data.volume_data.map(item => item.review_count);
            
            this.charts.volume.data.labels = labels;
            this.charts.volume.data.datasets[0].data = volumes;
            this.charts.volume.update();
        }
    }
    
    updateSentimentChart(data) {
        if (!this.charts.sentiment) return;
        
        const distribution = data.sentiment_distribution || {};
        const chartData = [
            distribution.positive || 0,
            distribution.negative || 0,
            distribution.neutral || 0
        ];
        
        this.charts.sentiment.data.datasets[0].data = chartData;
        this.charts.sentiment.update();
    }
    
    // Utility methods
    updateElement(element, value) {
        if (element) {
            element.textContent = value;
        }
    }
    
    setStatusIndicator(element, status) {
        if (!element) return;
        
        const indicator = element.querySelector('.status-indicator');
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
        }
    }
    
    setAllStatusLoading() {
        Object.values(this.elements).forEach(element => {
            if (element && element.id && element.id.includes('status')) {
                this.setStatusIndicator(element, 'loading');
            }
        });
    }
    
    setAllStatusSuccess() {
        Object.values(this.elements).forEach(element => {
            if (element && element.id && element.id.includes('status')) {
                this.setStatusIndicator(element, 'success');
            }
        });
    }
    
    setAllStatusError() {
        Object.values(this.elements).forEach(element => {
            if (element && element.id && element.id.includes('status')) {
                this.setStatusIndicator(element, 'error');
            }
        });
    }
    
    showLoading() {
        if (this.elements.loadingOverlay) {
            this.elements.loadingOverlay.classList.remove('hidden');
        }
    }
    
    hideLoading() {
        if (this.elements.loadingOverlay) {
            this.elements.loadingOverlay.classList.add('hidden');
        }
    }
    
    showError(message) {
        if (this.elements.errorMessage) {
            this.elements.errorMessage.textContent = message;
        }
        if (this.elements.errorOverlay) {
            this.elements.errorOverlay.classList.remove('hidden');
        }
        this.setAllStatusError();
    }
    
    hideError() {
        if (this.elements.errorOverlay) {
            this.elements.errorOverlay.classList.add('hidden');
        }
    }
    
    handleError(error) {
        console.error('Dashboard error:', error);
        
        let message = 'An unexpected error occurred while loading dashboard data.';
        
        if (error.message.includes('API error')) {
            message = 'Unable to connect to the data service. Please check your connection and try again.';
        } else if (error.message.includes('Failed to fetch')) {
            message = 'Network error. Please check your internet connection.';
        }
        
        this.showError(message);
        
        // Auto-retry logic
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`Auto-retry attempt ${this.retryCount}/${this.maxRetries}`);
            setTimeout(() => {
                this.hideError();
                this.loadDashboardData();
            }, 2000 * this.retryCount); // Exponential backoff
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Restaurant Review Dashboard - Initializing...');
    
    // Create global dashboard instance
    window.dashboard = new DashboardManager();
    
    console.log('Dashboard initialization complete');
});