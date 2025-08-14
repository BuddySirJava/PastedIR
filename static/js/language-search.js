// Language Search Component for Pasted IR
// Optimized for performance with large language lists

class LanguageSearch {
    constructor() {
        this.select = null;
        this.searchInput = null;
        this.optionsContainer = null;
        this.originalOptions = [];
        this.filteredOptions = [];
        this.isOpen = false;
        this.selectedIndex = -1;
        this.debounceTimer = null;
        this.maxResults = 50; // Limit results for performance
    }

    init() {
        this.select = document.getElementById('language');
        if (!this.select) {
            return;
        }

        this.createSearchInterface();
        this.bindEvents();
        this.loadOriginalOptions();
    }

    createSearchInterface() {
        const container = this.select.parentElement;
        
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'language-search-wrapper relative';
        wrapper.style.position = 'relative';
        
        // Create visible trigger button
        this.triggerButton = document.createElement('div');
        this.triggerButton.className = 'w-full border border-theme rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer bg-white dark:bg-gray-800 text-left flex justify-between items-center';
        this.triggerButton.innerHTML = `
            <span class="selected-text">🤖 Auto Detect</span>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
        `;
        
        // Create search input
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.placeholder = 'Search languages...';
        this.searchInput.className = 'w-full border border-theme rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent';
        this.searchInput.style.display = 'none';
        
        // Create options container
        this.optionsContainer = document.createElement('div');
        this.optionsContainer.className = 'language-options absolute w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-y-auto z-50';
        this.optionsContainer.style.display = 'none';
        this.optionsContainer.style.top = '100%';
        this.optionsContainer.style.left = '0';
        
        // Add custom styles for better appearance
        const style = document.createElement('style');
        style.textContent = `
            .language-options {
                scrollbar-width: thin;
                scrollbar-color: #cbd5e1 #f1f5f9;
            }
            .language-options::-webkit-scrollbar {
                width: 6px;
            }
            .language-options::-webkit-scrollbar-track {
                background: #f1f5f9;
                border-radius: 3px;
            }
            .language-options::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 3px;
            }
            .language-options::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
            }
            .dark .language-options::-webkit-scrollbar-track {
                background: #374151;
            }
            .dark .language-options::-webkit-scrollbar-thumb {
                background: #6b7280;
            }
            .dark .language-options::-webkit-scrollbar-thumb:hover {
                background: #9ca3af;
            }
            .language-option {
                border-bottom: 1px solid #f1f5f9;
            }
            .dark .language-option {
                border-bottom: 1px solid #374151;
            }
            .language-option:last-child {
                border-bottom: none;
            }
        `;
        document.head.appendChild(style);
        
        // Replace select with new elements
        container.insertBefore(wrapper, this.select);
        wrapper.appendChild(this.triggerButton);
        wrapper.appendChild(this.searchInput);
        wrapper.appendChild(this.optionsContainer);
        wrapper.appendChild(this.select);
        
        // Hide original select
        this.select.style.display = 'none';
    }

    loadOriginalOptions() {
        this.originalOptions = [];
        
        // Get all options from the original select
        Array.from(this.select.options).forEach((option, index) => {
            if (option.value && option.value !== 'auto') {
                this.originalOptions.push({
                    value: option.value,
                    text: option.textContent.trim(),
                    originalIndex: index
                });
            }
        });
        
        // Sort alphabetically for better UX
        this.originalOptions.sort((a, b) => a.text.localeCompare(b.text));
        
        // Add auto-detect option at the beginning
        this.originalOptions.unshift({
            value: 'auto',
            text: '🤖 Auto Detect',
            originalIndex: 0
        });
    }

    bindEvents() {
        // Toggle search on trigger button click
        this.triggerButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleSearch();
        });

        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });

        this.searchInput.addEventListener('focus', () => {
            this.showOptions();
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.searchInput.parentElement.contains(e.target) && !this.triggerButton.contains(e.target)) {
                this.closeSearch();
            }
        });

        // Prevent form submission on enter
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.selectOption(this.selectedIndex);
            }
        });
    }

    toggleSearch() {
        if (this.isOpen) {
            this.closeSearch();
        } else {
            this.openSearch();
        }
    }

    openSearch() {
        this.isOpen = true;
        this.searchInput.style.display = 'block';
        this.searchInput.focus();
        this.showOptions();
        this.searchInput.value = '';
        this.handleSearch('');
    }

    closeSearch() {
        this.isOpen = false;
        this.searchInput.style.display = 'none';
        this.hideOptions();
        this.selectedIndex = -1;
    }

    handleSearch(query) {
        // Debounce search for performance
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 150);
    }

    performSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (!searchTerm) {
            this.filteredOptions = this.originalOptions.slice(0, this.maxResults);
        } else {
            // Optimized search with multiple strategies
            this.filteredOptions = this.originalOptions.filter(option => {
                const text = option.text.toLowerCase();
                
                // Exact match gets highest priority
                if (text === searchTerm) return true;
                
                // Starts with search term
                if (text.startsWith(searchTerm)) return true;
                
                // Contains search term
                if (text.includes(searchTerm)) return true;
                
                // Check for word boundaries
                const words = text.split(/\s+/);
                return words.some(word => word.startsWith(searchTerm));
            }).slice(0, this.maxResults);
        }
        
        this.renderOptions();
        this.selectedIndex = this.filteredOptions.length > 0 ? 0 : -1;
        this.updateSelection();
    }

    renderOptions() {
        this.optionsContainer.innerHTML = '';
        
        if (this.filteredOptions.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'px-3 py-2 text-gray-500 dark:text-gray-400 text-sm';
            noResults.textContent = 'No languages found';
            this.optionsContainer.appendChild(noResults);
            return;
        }
        
        // Add results count header
        const resultsCount = document.createElement('div');
        resultsCount.className = 'px-3 py-2 text-xs text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-600';
        resultsCount.textContent = `${this.filteredOptions.length} language${this.filteredOptions.length !== 1 ? 's' : ''} found`;
        this.optionsContainer.appendChild(resultsCount);
        
        this.filteredOptions.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'language-option px-3 py-2 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors';
            optionElement.textContent = option.text;
            optionElement.dataset.index = index;
            optionElement.dataset.value = option.value;
            
            optionElement.addEventListener('click', () => {
                this.selectOption(index);
            });
            
            optionElement.addEventListener('mouseenter', () => {
                this.selectedIndex = index;
                this.updateSelection();
            });
            
            this.optionsContainer.appendChild(optionElement);
        });
    }

    handleKeydown(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredOptions.length - 1);
                this.updateSelection();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
                
            case 'Escape':
                e.preventDefault();
                this.closeSearch();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectOption(this.selectedIndex);
                }
                break;
        }
    }

    updateSelection() {
        const options = this.optionsContainer.querySelectorAll('.language-option');
        
        options.forEach((option, index) => {
            if (index === this.selectedIndex) {
                option.classList.add('bg-blue-100', 'dark:bg-gray-700');
                option.classList.remove('hover:bg-blue-50', 'dark:hover:bg-gray-700');
                
                // Scroll into view if needed
                if (option.offsetTop < this.optionsContainer.scrollTop) {
                    this.optionsContainer.scrollTop = option.offsetTop;
                } else if (option.offsetTop + option.offsetHeight > this.optionsContainer.scrollTop + this.optionsContainer.offsetHeight) {
                    this.optionsContainer.scrollTop = option.offsetTop + option.offsetHeight - this.optionsContainer.offsetHeight;
                }
            } else {
                option.classList.remove('bg-blue-100', 'dark:bg-gray-700');
                option.classList.add('hover:bg-blue-50', 'dark:hover:bg-gray-700');
            }
        });
    }

    selectOption(index) {
        if (index < 0 || index >= this.filteredOptions.length) return;
        
        const option = this.filteredOptions[index];
        
        // Update the original select
        this.select.value = option.value;
        
        // Update the trigger button text
        const selectedText = this.triggerButton.querySelector('.selected-text');
        if (selectedText) {
            selectedText.textContent = option.text;
        }
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        this.select.dispatchEvent(event);
        
        // Dispatch custom event for language detection
        const customEvent = new CustomEvent('languageSelected', { 
            detail: { value: option.value, text: option.text } 
        });
        document.dispatchEvent(customEvent);
        
        // Update the search input to show selected value
        this.searchInput.value = option.text;
        
        // Close the search
        this.closeSearch();
    }

    showOptions() {
        this.optionsContainer.style.display = 'block';
    }

    hideOptions() {
        this.optionsContainer.style.display = 'none';
    }

    // Public method to get selected value
    getValue() {
        return this.select.value;
    }

    // Public method to set value
    setValue(value) {
        this.select.value = value;
        const option = this.originalOptions.find(opt => opt.value === value);
        if (option) {
            this.searchInput.value = option.text;
            // Update the trigger button text
            const selectedText = this.triggerButton.querySelector('.selected-text');
            if (selectedText) {
                selectedText.textContent = option.text;
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the create page
    if (document.getElementById('language')) {
        window.languageSearch = new LanguageSearch();
        window.languageSearch.init(); // Call init() to set up the search interface
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageSearch;
}
