/**
 * TECH BLOG PORTFOLIO - JAVASCRIPT
 * Modern, accessible, and performant interactions
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeThemeToggle();
    initializeMobileMenu();
    initializeNavigation();
    initializeAnimations();
    initializeAccessibility();
    updateCurrentYear();
    logWelcomeMessage();
});

// ==============================================
// THEME TOGGLE FUNCTIONALITY
// ==============================================

function initializeThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

    if (!themeToggleBtn || !themeToggleDarkIcon || !themeToggleLightIcon) {
        console.warn('Theme toggle elements not found');
        return;
    }

    // Check for saved theme preference or default to system preference
    function getThemePreference() {
        if (localStorage.getItem('theme')) {
            return localStorage.getItem('theme');
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // Set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            htmlElement.classList.add('dark');
            themeToggleLightIcon.classList.remove('hidden');
            themeToggleDarkIcon.classList.add('hidden');
        } else {
            htmlElement.classList.remove('dark');
            themeToggleLightIcon.classList.add('hidden');
            themeToggleDarkIcon.classList.remove('hidden');
        }
        localStorage.setItem('theme', theme);
    }

    // Initialize theme on page load
    setTheme(getThemePreference());

    // Theme toggle button event listener
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

// ==============================================
// MOBILE MENU TOGGLE
// ==============================================

function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (!mobileMenuButton || !mobileMenu) {
        console.warn('Mobile menu elements not found');
        return;
    }

    mobileMenuButton.addEventListener('click', () => {
        const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
        mobileMenuButton.setAttribute('aria-expanded', !isExpanded);
        mobileMenu.classList.toggle('hidden');
    });

    // Close mobile menu when clicking on a link
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!mobileMenuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        }
    });

    // Keyboard support for mobile menu
    mobileMenuButton.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            mobileMenuButton.focus();
        }
    });
}

// ==============================================
// NAVIGATION FUNCTIONALITY
// ==============================================

function initializeNavigation() {
    initializeSmoothScrolling();
    initializeHeaderScrollEffect();
    initializeActiveNavHighlighting();
}

// ==============================================
// SMOOTH SCROLLING WITH OFFSET FOR FIXED HEADER
// ==============================================

function initializeSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            
            // Skip if it's just '#' or '#home'
            if (href === '#' || href === '#home') {
                return;
            }
            
            e.preventDefault();
            
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const header = document.getElementById('header');
                const headerHeight = header ? header.offsetHeight : 0;
                const targetPosition = targetElement.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL without triggering scroll
                history.pushState(null, null, href);
            }
        });
    });
}

// ==============================================
// HEADER SCROLL EFFECT
// ==============================================

function initializeHeaderScrollEffect() {
    const header = document.getElementById('header');
    
    if (!header) {
        console.warn('Header element not found');
        return;
    }

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Add shadow when scrolled
        if (currentScroll > 20) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
}

// ==============================================
// ACTIVE NAVIGATION LINK HIGHLIGHTING
// ==============================================

function initializeActiveNavHighlighting() {
    function updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPosition = window.pageYOffset + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                // Remove active class from all links
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add active class to current section's link
                const activeLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
                if (activeLink) {
                    activeLink.classList.add('active');
                }
            }
        });
    }

    // Debounce scroll and resize events
    const debouncedScroll = debounce(updateActiveNavLink, 10);
    
    window.addEventListener('scroll', debouncedScroll);
    window.addEventListener('load', updateActiveNavLink);
}

// ==============================================
// INTERSECTION OBSERVER FOR FADE-IN ANIMATIONS
// ==============================================

function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                // Optionally unobserve after animation
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all elements with animation classes
    const animatedElements = document.querySelectorAll('.fade-in, .skill-category, .project-card, .contact-card');
    animatedElements.forEach(el => observer.observe(el));

    // Lazy loading for images (when added)
    initializeLazyLoading();
}

// ==============================================
// LAZY LOADING FOR IMAGES
// ==============================================

function initializeLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy-blur');
                        img.classList.add('loaded');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// ==============================================
// ACCESSIBILITY FEATURES
// ==============================================

function initializeAccessibility() {
    // Add skip to main content functionality
    const skipLink = document.querySelector('a[href="#main"]');
    if (skipLink) {
        skipLink.addEventListener('click', (e) => {
            e.preventDefault();
            const main = document.querySelector('main');
            if (main) {
                main.setAttribute('tabindex', '-1');
                main.focus();
            }
        });
    }
}

// ==============================================
// PERFORMANCE: DEBOUNCE FUNCTION
// ==============================================

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

// ==============================================
// DYNAMIC YEAR IN FOOTER
// ==============================================

function updateCurrentYear() {
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    yearElements.forEach(el => {
        el.textContent = currentYear;
    });
}

// ==============================================
// CONSOLE WELCOME MESSAGE
// ==============================================

function logWelcomeMessage() {
    console.log(
        '%c👋 Welcome to Tech Blog Portfolio!',
        'font-size: 20px; font-weight: bold; color: #0ea5e9;'
    );
    console.log(
        '%cInterested in the code? Check out the repository!',
        'font-size: 14px; color: #666;'
    );
    console.log('✅ Portfolio initialized successfully');
}

// ==============================================
// ANALYTICS & PERFORMANCE MONITORING
// ==============================================

// Track page load time
window.addEventListener('load', () => {
    if (window.performance) {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        if (pageLoadTime > 0) {
            console.log(`Page load time: ${pageLoadTime}ms`);
        }
    }
});

// Track visibility changes (for analytics)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page is hidden');
    } else {
        console.log('Page is visible');
    }
});

// ==============================================
// ERROR HANDLING
// ==============================================

window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});

// ==============================================
// PRINT OPTIMIZATION
// ==============================================

window.addEventListener('beforeprint', () => {
    console.log('Preparing to print...');
});

window.addEventListener('afterprint', () => {
    console.log('Print completed');
});

// ==============================================
// PERFORMANCE: PREFETCH LINKS ON HOVER
// ==============================================

const prefetchLinks = document.querySelectorAll('a[data-prefetch]');

prefetchLinks.forEach(link => {
    link.addEventListener('mouseenter', () => {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('#')) {
            const linkElement = document.createElement('link');
            linkElement.rel = 'prefetch';
            linkElement.href = href;
            document.head.appendChild(linkElement);
        }
    });
});

// ==============================================
// INITIALIZATION COMPLETE
// ==============================================
