/**
 * AttendX Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initDarkMode();
    
    // Initialize theme switcher
    initThemeSwitcher();
    
    // Initialize page loading bar
    initPageLoadingBar();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // CSRF Token setup for AJAX
    setupCSRFToken();

    // Initialize page-specific functionality
    initAttendancePage();
    initQRCodePage();

    // Initialize animations
    initScrollAnimations();
    initCounterAnimations();
    initHoverEffects();
    initStaggeredAnimations();
    
    // Initialize mobile sidebar
    initMobileSidebar();
    
    // Initialize confetti system
    initConfetti();
});

/**
 * Setup CSRF token for AJAX requests
 */
function setupCSRFToken() {
    const csrftoken = getCookie('csrftoken');
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

/**
 * Get cookie value by name
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Initialize Attendance Page functionality
 */
function initAttendancePage() {
    const attendanceTable = document.getElementById('attendanceTable');
    if (attendanceTable) {
        // Auto-refresh attendance list every 10 seconds
        setInterval(refreshAttendanceList, 10000);
    }
}

/**
 * Refresh attendance list via AJAX
 */
function refreshAttendanceList() {
    const container = document.getElementById('attendanceList');
    if (!container) return;

    $.ajax({
        url: '/attendance/api/refresh/',
        type: 'GET',
        success: function(data) {
            if (data.success) {
                container.innerHTML = data.html;
                updateAttendanceCounter(data.present_count, data.total_count);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error refreshing attendance:', error);
        }
    });
}

/**
 * Update attendance counter display
 */
function updateAttendanceCounter(present, total) {
    const counterElement = document.getElementById('attendanceCounter');
    if (counterElement) {
        counterElement.textContent = `${present} / ${total}`;
    }
    
    const percentageElement = document.getElementById('attendancePercentage');
    if (percentageElement && total > 0) {
        const percentage = ((present / total) * 100).toFixed(1);
        percentageElement.textContent = `${percentage}%`;
    }
}

/**
 * Initialize QR Code Page functionality
 */
function initQRCodePage() {
    const qrTimer = document.getElementById('qrTimer');
    if (qrTimer) {
        startQRTimer();
    }
}

/**
 * QR Code countdown timer
 */
let qrCountdown;
let qrExpiryTime;

function startQRTimer() {
    const timerElement = document.getElementById('qrTimer');
    if (!timerElement) return;

    // Get expiry time from data attribute
    qrExpiryTime = new Date(timerElement.dataset.expiry).getTime();
    
    // Update timer every second
    qrCountdown = setInterval(updateQRTimer, 1000);
}

function updateQRTimer() {
    const timerElement = document.getElementById('qrTimer');
    if (!timerElement) {
        clearInterval(qrCountdown);
        return;
    }

    const now = new Date().getTime();
    const distance = qrExpiryTime - now;

    if (distance < 0) {
        clearInterval(qrCountdown);
        timerElement.textContent = 'EXPIRED';
        timerElement.classList.add('text-danger');
        
        // Auto-refresh QR code
        autoRefreshQR();
        return;
    }

    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    // Change color when less than 15 seconds
    if (distance < 15000) {
        timerElement.classList.add('text-warning');
        timerElement.classList.remove('text-primary');
    }
}

/**
 * Auto-refresh QR code when expired
 */
function autoRefreshQR() {
    $.ajax({
        url: '/qr/api/regenerate/',
        type: 'POST',
        success: function(data) {
            if (data.success) {
                // Update QR image
                const qrImage = document.getElementById('qrImage');
                if (qrImage) {
                    qrImage.src = data.qr_image_url;
                }
                
                // Update timer
                const timerElement = document.getElementById('qrTimer');
                if (timerElement) {
                    timerElement.dataset.expiry = data.expiry_time;
                    timerElement.classList.remove('text-danger', 'text-warning');
                    timerElement.classList.add('text-primary');
                    startQRTimer();
                }
                
                showToast('QR Code refreshed successfully', 'success');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error refreshing QR code:', error);
            showToast('Failed to refresh QR code', 'error');
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        // Create toast container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
        toastContainer = container;
    }

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * ============================================
 * CONFETTI SYSTEM
 * ============================================
 */
let confettiCanvas = null;
let confettiCtx = null;
let confettiPieces = [];
let confettiAnimId = null;
const confettiColors = ['#6366f1', '#8b5cf6', '#a78bfa', '#10b981', '#34d399', '#f59e0b', '#fbbf24', '#ef4444', '#f87171', '#06b6d4', '#22d3ee', '#ec4899'];

function initConfetti() {
    confettiCanvas = document.createElement('canvas');
    confettiCanvas.id = 'confetti-canvas-global';
    confettiCanvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;';
    document.body.appendChild(confettiCanvas);
    confettiCtx = confettiCanvas.getContext('2d');
    resizeConfettiCanvas();
    window.addEventListener('resize', resizeConfettiCanvas);
}

function resizeConfettiCanvas() {
    if (!confettiCanvas) return;
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
}

class ConfettiPiece {
    constructor() {
        this.x = Math.random() * (confettiCanvas ? confettiCanvas.width : window.innerWidth);
        this.y = -10 - Math.random() * 60;
        this.size = Math.random() * 8 + 4;
        this.color = confettiColors[Math.floor(Math.random() * confettiColors.length)];
        this.velocityX = (Math.random() - 0.5) * 8;
        this.velocityY = Math.random() * 4 + 3;
        this.rotation = Math.random() * 360;
        this.rotationSpeed = (Math.random() - 0.5) * 12;
        this.opacity = 1;
        this.shape = Math.random() > 0.5 ? 'rect' : 'circle';
        this.wobble = Math.random() * Math.PI * 2;
        this.wobbleSpeed = Math.random() * 0.1 + 0.05;
    }
    update() {
        this.y += this.velocityY;
        this.x += this.velocityX + Math.sin(this.wobble) * 0.8;
        this.rotation += this.rotationSpeed;
        this.wobble += this.wobbleSpeed;
        this.velocityY += 0.06; // gravity
        this.velocityX *= 0.99; // air resistance
        this.opacity -= 0.004;
        return this.opacity > 0 && this.y < (confettiCanvas ? confettiCanvas.height : window.innerHeight) + 20;
    }
    draw() {
        if (!confettiCtx) return;
        confettiCtx.save();
        confettiCtx.globalAlpha = this.opacity;
        confettiCtx.translate(this.x, this.y);
        confettiCtx.rotate((this.rotation * Math.PI) / 180);
        confettiCtx.fillStyle = this.color;
        if (this.shape === 'rect') {
            confettiCtx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 0.6);
        } else {
            confettiCtx.beginPath();
            confettiCtx.arc(0, 0, this.size / 2, 0, Math.PI * 2);
            confettiCtx.fill();
        }
        confettiCtx.restore();
    }
}

function launchConfetti(count) {
    if (!confettiCanvas || !confettiCtx) {
        initConfetti();
    }
    count = count || 200;
    confettiPieces = [];
    for (let i = 0; i < count; i++) {
        confettiPieces.push(new ConfettiPiece());
    }
    if (!confettiAnimId) {
        animateConfetti();
    }
}

function animateConfetti() {
    if (!confettiCtx || !confettiCanvas) return;
    confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    confettiPieces = confettiPieces.filter(function(piece) {
        piece.draw();
        return piece.update();
    });
    if (confettiPieces.length > 0) {
        confettiAnimId = requestAnimationFrame(animateConfetti);
    } else {
        confettiAnimId = null;
        confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    }
}

// Make launchConfetti globally available
window.launchConfetti = launchConfetti;

/**
 * Confirm dialog helper
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Debounce function for search inputs
 */
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

/**
 * Initialize Theme Switcher
 */
function initThemeSwitcher() {
    const switcherBtn = document.getElementById('themeSwitcherBtn');
    const dropdown = document.getElementById('themeSwitcherDropdown');
    const colorBtns = document.querySelectorAll('.theme-color-btn');
    
    if (!switcherBtn || !dropdown) return;
    
    // Load saved accent color
    const savedColor = localStorage.getItem('attendx-accent-color') || 'indigo';
    setAccentColor(savedColor);
    
    // Toggle dropdown on button click
    switcherBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!switcherBtn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
    
    // Handle color selection
    colorBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const color = this.getAttribute('data-theme-color');
            setAccentColor(color);
            
            // Update active state and aria-pressed
            colorBtns.forEach(function(b) { 
                b.classList.remove('active'); 
                b.setAttribute('aria-pressed', 'false'); 
            });
            this.classList.add('active');
            this.setAttribute('aria-pressed', 'true');
            
            // Save preference
            localStorage.setItem('attendx-accent-color', color);
            
            // Close dropdown
            dropdown.classList.remove('show');
            
            // Trigger transition effect
            triggerThemeTransition();
        });
    });
    
    // Set active state and aria-pressed on load
    colorBtns.forEach(function(btn) {
        const isActive = btn.getAttribute('data-theme-color') === savedColor;
        if (isActive) {
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
        } else {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        }
    });
}

/**
 * Set accent color theme
 */
function setAccentColor(color) {
    // Set data-theme on body for CSS selector compatibility
    document.body.setAttribute('data-theme', color);
}

/**
 * Trigger theme transition effect
 */
function triggerThemeTransition() {
    // Remove any existing transition elements to prevent accumulation
    document.querySelectorAll('.theme-transition').forEach(function(el) {
        el.remove();
    });
    
    const transition = document.createElement('div');
    transition.className = 'theme-transition';
    document.body.appendChild(transition);
    
    // Force reflow to ensure animation triggers
    void transition.offsetWidth;
    transition.classList.add('active');
    
    setTimeout(function() {
        transition.remove();
    }, 400);
}

/**
 * Initialize Dark Mode
 */
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    const icon = document.getElementById('darkModeIcon');
    
    if (!toggle || !icon) return;
    
    // Check for saved preference or system preference
    // Support both old key (attendx-theme) and new key (attendx-dark-mode) for migration
    const savedTheme = localStorage.getItem('attendx-dark-mode') || localStorage.getItem('attendx-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark-mode');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        toggle.setAttribute('aria-pressed', 'true');
    } else {
        toggle.setAttribute('aria-pressed', 'false');
    }
    
    // Toggle dark mode on click
    toggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        
        if (document.body.classList.contains('dark-mode')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            localStorage.setItem('attendx-dark-mode', 'dark');
            // Also update old key for backward compatibility
            localStorage.setItem('attendx-theme', 'dark');
            toggle.setAttribute('aria-pressed', 'true');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            localStorage.setItem('attendx-dark-mode', 'light');
            localStorage.setItem('attendx-theme', 'light');
            toggle.setAttribute('aria-pressed', 'false');
        }
    });
}

/**
 * Initialize Mobile Sidebar Toggle
 */
function initMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggler = document.querySelector('.navbar-toggler');
    
    if (!sidebar || !toggler) return;
    
    // Toggle sidebar when hamburger is clicked
    toggler.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (window.innerWidth < 768) {
            sidebar.classList.toggle('show');
        }
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 768 && 
            sidebar.classList.contains('show') && 
            !sidebar.contains(e.target) && 
            !toggler.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    });
    
    // Close sidebar on nav link click (mobile)
    sidebar.querySelectorAll('.nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth < 768) {
                sidebar.classList.remove('show');
            }
        });
    });
}

/**
 * Initialize Page Loading Bar
 */
function initPageLoadingBar() {
    const bar = document.getElementById('pageLoadingBar');
    if (!bar) return;
    
    // Show loading bar on page start
    bar.style.width = '30%';
    
    // Complete loading bar
    window.addEventListener('load', function() {
        bar.style.width = '100%';
        setTimeout(function() {
            bar.style.opacity = '0';
            setTimeout(function() {
                bar.style.display = 'none';
            }, 300);
        }, 200);
    });
}

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

/**
 * Initialize Scroll-Triggered Animations
 */
function initScrollAnimations() {
    // Respect prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            el.classList.add('animated');
        });
        return;
    }

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Add staggered delay based on element index
                setTimeout(() => {
                    entry.target.classList.add('animated');
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Initialize Counter Animations
 */
function initCounterAnimations() {
    const counters = document.querySelectorAll('[data-counter]');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-counter'));
    const duration = 1500;
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

/**
 * Initialize Hover Effects
 */
function initHoverEffects() {
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.className = 'btn-ripple';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add tilt effect to cards on hover
    document.querySelectorAll('.stat-card, .chart-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
}

/**
 * Initialize Staggered Animations
 */
function initStaggeredAnimations() {
    const staggerElements = document.querySelectorAll('.stagger-item');
    
    const staggerObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = `${index * 0.1}s`;
                entry.target.classList.add('animate-in');
                staggerObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    staggerElements.forEach(el => staggerObserver.observe(el));
}
