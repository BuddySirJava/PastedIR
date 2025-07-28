// Theme Manager for Pasted IR
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.themeIcon = document.getElementById('themeIcon');
        this.highlightStyle = document.getElementById('highlight-style');
        this.highlightStyleLight = document.getElementById('highlight-style-light');
        
        this.init();
    }

    init() {
        // Load saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Add event listener
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                this.setTheme(newTheme);
            });
        }
        
        // Add keyboard shortcut (Ctrl/Cmd + T)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 't') {
                e.preventDefault();
                const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                this.setTheme(newTheme);
            }
        });
    }

    setTheme(theme) {
        const html = document.documentElement;
        
        try {
            if (theme === 'dark') {
                html.classList.add('dark');
                if (this.themeToggle) this.themeToggle.classList.add('dark');
                if (this.themeIcon) this.themeIcon.textContent = '☀️';
                if (this.highlightStyle) this.highlightStyle.disabled = true;
                if (this.highlightStyleLight) this.highlightStyleLight.disabled = false;
            } else {
                html.classList.remove('dark');
                if (this.themeToggle) this.themeToggle.classList.remove('dark');
                if (this.themeIcon) this.themeIcon.textContent = '🌙';
                if (this.highlightStyle) this.highlightStyle.disabled = false;
                if (this.highlightStyleLight) this.highlightStyleLight.disabled = true;
            }
            
            localStorage.setItem('theme', theme);
            
            // Re-highlight code blocks if highlight.js is loaded
            if (typeof hljs !== 'undefined') {
                setTimeout(() => {
                    try {
                        hljs.highlightAll();
                        // Force update code colors after highlighting
                        const codeElements = document.querySelectorAll('code');
                        codeElements.forEach(code => {
                            if (theme === 'dark') {
                                code.style.color = '#ffffff';
                            } else {
                                code.style.color = '#000000';
                            }
                        });
                    } catch (error) {
                        console.warn('Failed to re-highlight code blocks:', error);
                    }
                }, 100);
            }
            
            // Dispatch custom event for other scripts
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
            
        } catch (error) {
            console.error('Error setting theme:', error);
        }
    }

    getCurrentTheme() {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }

    toggleTheme() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
} 