// View Paste JavaScript functionality
(function() {
    'use strict';

    // Configuration - will be set by Django template
    let PASTE_CONFIG = {
        content: '',
        pasteId: '',
        csrfToken: '',
        chatbotUrl: '',
        langAlias: ''
    };

    // Function to apply the correct styling to AI responses
    function styleAiResponse(container) {
        const chatHistory = document.getElementById('paste-chat-history');
        const isDarkMode = document.documentElement.classList.contains('dark');

        if (!isDarkMode) {
            // Light Mode: high contrast with white background and black text
            chatHistory.style.backgroundColor = '#ffffff';
            container.style.color = '#000000';
        } else {
            // Dark Mode: use theme's secondary background and a light gray text
            chatHistory.style.backgroundColor = 'var(--bg-secondary, #0f172a)'; // Fallback color
            container.style.color = '#cbd5e1';
        }

        // Style for <pre> blocks (the "box" for code blocks)
        const preElements = container.querySelectorAll('pre');
        preElements.forEach(pre => {
            pre.style.backgroundColor = '#000000'; // Black background
            pre.style.color = '#ffffff';           // White text
            pre.style.padding = '1rem';
            pre.style.borderRadius = '0.5rem';
            pre.style.whiteSpace = 'pre-wrap';     // Wrap long lines
            pre.style.overflowX = 'auto';
        });

        // Style for <code> elements (inline and within <pre>)
        const codeElements = container.querySelectorAll('code');
        codeElements.forEach(code => {
            code.style.fontFamily = "'Courier New', Courier, monospace";
            if (code.parentElement.tagName.toLowerCase() !== 'pre') {
                // Inline code: black box, white text
                code.style.backgroundColor = '#000000';
                code.style.color = '#ffffff';
                code.style.padding = '0.2rem 0.4rem';
                code.style.borderRadius = '0.3rem';
            } else {
                // Code inside <pre>: inherit colors, no extra styling
                code.style.backgroundColor = 'transparent';
                code.style.color = 'inherit';
                code.style.padding = '0';
            }
        });
    }

    // Initialize the view paste functionality
    function initializeViewPage() {
        // Load content from the JSON script tag
        const contentScript = document.getElementById('paste-content');
        if (contentScript) {
            try {
                PASTE_CONFIG.content = JSON.parse(contentScript.textContent);
            } catch (e) {
                console.error('Failed to parse paste content from JSON script tag:', e);
                return;
            }
        } else {
            console.error('Paste content script tag not found.');
            return;
        }
        
        const copyBtn = document.querySelector('button#paste-copy-btn');
        const highlightToggle = document.querySelector('button#paste-highlight-toggle');
        const codeElement = document.querySelector('code');

        if (codeElement) {
            codeElement.textContent = PASTE_CONFIG.content;
            if (typeof hljs !== 'undefined') {
                hljs.highlightElement(codeElement);
            }
        }
        
        if (copyBtn) {
            class CopyComboButton {
                constructor(button, content, options = {}) {
                    this.button = button;
                    this.content = content;
                    this.resetDelayMs = options.resetDelayMs ?? 2000;
                    this.count = 0;
                    this.timerId = null;
                    this.baseClasses = 'copy-button font-semibold px-4 py-2 rounded-lg transition-colors focus:ring-2 focus:ring-offset-2 cursor-pointer';
                    this.stages = [
                        { label: 'Copied!', icon: '✅', bg: '#16a34a', color: '#ffffff' },
                        { label: 'Double Copy!', icon: '⚡', bg: '#2563eb', color: '#ffffff' },
                        { label: 'Triple Copy!', icon: '🔥', bg: '#ea580c', color: '#ffffff' },
                        { label: 'Mega Copy!', icon: '🚀', bg: '#7c3aed', color: '#ffffff' },
                        { label: 'Ultra Copy!', icon: '💎', bg: '#4f46e5', color: '#ffffff' },
                        { label: 'Super Copy!', icon: '🌟', bg: '#eab308', color: '#000000' },
                        { label: 'Epic Copy!', icon: '👑', bg: '#db2777', color: '#ffffff' },
                        { label: 'Legendary Copy!', icon: '🏆', bg: '#dc2626', color: '#ffffff' },
                        { label: 'Mythical Copy!', icon: '✨', bg: '#0d9488', color: '#ffffff' }
                    ];
                    this.applyIdle();
                    this.button.addEventListener('click', (e) => this.onClick(e));
                }

                onClick(e) {
                    e.preventDefault();
                    this.count += 1;
                    try { this.button.dataset.copyCount = String(this.count); } catch (_) {}
                    if (this.timerId) clearTimeout(this.timerId);
                    this.applyStage(this.count);
                    this.timerId = setTimeout(() => this.reset(), this.resetDelayMs);
                    this.copyToClipboard();
                }

                applyStage(count) {
                    const overflow = count > this.stages.length;
                    const stage = overflow ? null : this.stages[count - 1];
                    this.button.className = this.baseClasses;
                    this.button.style.backgroundImage = '';
                    if (overflow) {
                        this.button.style.backgroundImage = 'linear-gradient(to right, #7c3aed, #db2777)';
                        this.button.style.backgroundColor = '';
                        this.button.style.color = '#ffffff';
                        this.button.textContent = `⚡ God Copy!`;
                    } else {
                        this.button.style.backgroundColor = stage.bg;
                        this.button.style.color = stage.color;
                        this.button.textContent = `${stage.icon} ${stage.label}`;
                    }
                }

                applyIdle() {
                    this.button.className = this.baseClasses;
                    this.button.style.backgroundImage = '';
                    this.button.style.backgroundColor = '#16a34a';
                    this.button.style.color = '#ffffff';
                    this.button.textContent = '📋 Copy';
                }

                reset() {
                    this.count = 0;
                    this.timerId = null;
                    this.applyIdle();
                }

                copyToClipboard() {
                    try {
                        if (navigator.clipboard && window.isSecureContext) {
                            navigator.clipboard.writeText(this.content).catch(() => {});
                        } else {
                            const ta = document.createElement('textarea');
                            ta.value = this.content;
                            ta.setAttribute('readonly', '');
                            ta.style.position = 'fixed';
                            ta.style.pointerEvents = 'none';
                            ta.style.opacity = '0';
                            document.body.appendChild(ta);
                            ta.focus();
                            ta.select();
                            try { document.execCommand('copy'); } catch (_) {}
                            document.body.removeChild(ta);
                        }
                    } catch (_) {}
                }
            }

            new CopyComboButton(copyBtn, PASTE_CONFIG.content, { resetDelayMs: 2000 });
        }
        
        if (highlightToggle && codeElement) {
            let isHighlighted = true;
            highlightToggle.addEventListener('click', function(e) {
                e.preventDefault();
                if (isHighlighted) {
                    codeElement.className = '';
                    highlightToggle.innerHTML = '🎨 Enable Highlight';
                    isHighlighted = false;
                } else {
                    codeElement.className = `language-${PASTE_CONFIG.langAlias}`;
                    highlightToggle.innerHTML = '🎨 Disable Highlight';
                    isHighlighted = true;
                    if (typeof hljs !== 'undefined') {
                        setTimeout(() => {
                            hljs.highlightAll();
                            const isDark = document.documentElement.classList.contains('dark');
                            codeElement.style.color = isDark ? '#ffffff' : '#000000';
                        }, 100);
                    }
                }
            });
            
            document.addEventListener('keydown', function(e) {
                if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
                    e.preventDefault();
                    highlightToggle.click();
                }
            });
        }

        // Chatbot functionality
        const askAiBtn = document.querySelector('button#paste-ask-ai-btn');
        const chatModal = document.querySelector('div#paste-chat-modal');
        const closeChatBtn = document.querySelector('button#paste-close-chat-btn');
        const chatHistory = document.querySelector('div#paste-chat-history');
        const chatInput = document.querySelector('input#paste-chat-input');
        const sendChatBtn = document.querySelector('button#paste-send-chat-btn');

        if (askAiBtn && chatModal) {
            askAiBtn.addEventListener('click', (e) => {
                e.preventDefault();
                chatModal.classList.remove('hidden');
            });
        }

        if (closeChatBtn && chatModal) {
            closeChatBtn.addEventListener('click', (e) => {
                e.preventDefault();
                chatModal.classList.add('hidden');
            });
        }

        if (sendChatBtn && chatInput && chatHistory) {
            const handleSendChat = async () => {
                const question = chatInput.value;
                if (!question) return;

                const userMessage = document.createElement('div');
                userMessage.classList.add('mb-2', 'chat-message-user');
                userMessage.innerHTML = `<strong class="text-theme-primary">You:</strong> <span class="text-theme-secondary">${question}</span>`;
                chatHistory.appendChild(userMessage);
                chatInput.value = '';

                const aiMessageContainer = document.createElement('div');
                aiMessageContainer.classList.add('mb-2', 'chat-message-ai');
                aiMessageContainer.innerHTML = `<strong class="text-theme-primary">AI:</strong> <span></span>`;
                chatHistory.appendChild(aiMessageContainer);
                const aiResponseSpan = aiMessageContainer.querySelector('span');
                chatHistory.scrollTop = chatHistory.scrollHeight;

                try {
                    const response = await fetch(PASTE_CONFIG.chatbotUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': PASTE_CONFIG.csrfToken,
                            'X-Bot-Token': 'Used-For-Bot-API-Calls'
                        },
                        body: JSON.stringify({
                            paste_id: PASTE_CONFIG.pasteId,
                            question: question
                        })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let fullResponse = '';

                    function processStream() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                try {
                                    if (window.marked) {
                                        aiResponseSpan.innerHTML = marked.parse(fullResponse);
                                        styleAiResponse(aiResponseSpan);
                                    } else {
                                        aiResponseSpan.textContent = fullResponse;
                                    }
                                } catch (e) {
                                    aiResponseSpan.textContent = fullResponse;
                                }
                                chatHistory.scrollTop = chatHistory.scrollHeight;
                                return;
                            }
                            
                            const chunk = decoder.decode(value, {stream: true});
                            const lines = chunk.split('\n');
                            
                            for (const line of lines) {
                                if (line.startsWith('data: ')) {
                                    try {
                                        const jsonData = JSON.parse(line.slice(6));
                                        
                                        if (jsonData.end_of_stream) {
                                            try {
                                                if (window.marked) {
                                                    aiResponseSpan.innerHTML = marked.parse(fullResponse);
                                                    styleAiResponse(aiResponseSpan);
                                                } else {
                                                    aiResponseSpan.textContent = fullResponse;
                                                }
                                            } catch (e) {
                                                aiResponseSpan.textContent = fullResponse;
                                            }
                                            chatHistory.scrollTop = chatHistory.scrollHeight;
                                            return;
                                        } else if (jsonData.response_chunk) {
                                            fullResponse += jsonData.response_chunk;
                                            aiResponseSpan.textContent = fullResponse;
                                            chatHistory.scrollTop = chatHistory.scrollHeight;
                                        } else if (jsonData.error) {
                                            aiResponseSpan.textContent = `Error: ${jsonData.error}`;
                                            chatHistory.scrollTop = chatHistory.scrollHeight;
                                            return;
                                        }
                                    } catch (parseError) {
                                        // Skip invalid lines silently
                                    }
                                }
                            }
                            
                            processStream();
                        }).catch(error => {
                            aiResponseSpan.textContent = 'Error reading response from server.';
                        });
                    }
                    processStream();

                } catch (error) {
                    console.error('Error:', error);
                    aiResponseSpan.textContent = 'Sorry, something went wrong.';
                }
            };

            sendChatBtn.addEventListener('click', (e) => {
                e.preventDefault();
                handleSendChat();
            });

            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSendChat();
                }
            });
        }
    }

    // Public API
    window.PasteViewer = {
        init: function(config) {
            PASTE_CONFIG = config;
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initializeViewPage);
            } else {
                initializeViewPage();
            }
        }
    };

})();