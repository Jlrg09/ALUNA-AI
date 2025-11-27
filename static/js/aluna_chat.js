/**
 * ORIGEN - JavaScript Principal
 * Sistema de chat inteligente con interfaz moderna
 */

class OrigenChat {
    constructor() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.characterCount = document.getElementById('characterCount');
        this.conversationsList = document.getElementById('conversationsList');
        this.conversationTitle = document.getElementById('conversationTitle');
        this.conversationDate = document.getElementById('conversationDate');
        this.appLayout = document.querySelector('.app-layout');
        this.searchInput = document.getElementById('chatSearchInput');
        this.clearSearchBtn = document.getElementById('clearChatSearch');
        this.searchTrigger = document.getElementById('chatSearchTrigger');
        this.noResultsMessage = document.getElementById('noSearchResults');
        
        this.isTyping = false;
        this.messageHistory = [];
        this.settings = this.loadSettings();
        this.currentConversationId = null;
        this.conversations = [];
        this.searchQuery = '';
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkApiStatus();
        this.applySettings();
        this.loadConversations();
        this.welcomeMessage();
        this.bindSuggestions();
        this.restoreSidebarState();
    }

    restoreSidebarState() {
        if (!this.appLayout) return;
            this.pendingImages = [];

        if (localStorage.getItem('sidebarHidden') === null) {
            localStorage.setItem('sidebarHidden', 'true');
        }

        if (localStorage.getItem('sidebarCollapsed') === null) {
            localStorage.setItem('sidebarCollapsed', 'false');
        }

        this.handleWindowResize();
        this.updateSearchControls();
    }

    bindEvents() {
        // Eventos del input
        this.messageInput.addEventListener('input', this.handleInputChange.bind(this));
        this.messageInput.addEventListener('keydown', this.handleKeyDown.bind(this));
        
        // Evento del botón enviar
        this.sendBtn.addEventListener('click', this.sendMessage.bind(this));
        
        // Botones de acción rápida
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.currentTarget.dataset.question;
                this.messageInput.value = question;
                this.sendMessage();
            });
            if (attachmentBtn && fileInput) {
                attachmentBtn.addEventListener('click', () => fileInput.click());
                fileInput.addEventListener('change', (e) => {
                    const files = Array.from(e.target.files || []);
                    if (!files.length) return;
                    const imageFiles = files.filter(f => /image\/(png|jpg|jpeg|gif|webp)/i.test(f.type));
                    if (!imageFiles.length) {
                        this.showToast('Selecciona imágenes válidas (png, jpg, webp)', 'info');
                        return;
                    }
                    // Queue images for sending on Enviar
                    this.pendingImages = imageFiles;
                    this.sendBtn.disabled = false;
                    this.showToast(`Imágenes listas para enviar: ${imageFiles.length}`, 'success');
                });
            }
        const fileInput = document.getElementById('fileUploadInput');
        if (attachmentBtn && fileInput) {
            attachmentBtn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', this.handleFileUpload.bind(this));
        }

        // Botones del header
        const clearBtn = document.getElementById('clearChat');
        if (clearBtn) clearBtn.addEventListener('click', this.clearChat.bind(this));
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) settingsBtn.addEventListener('click', this.openSettings.bind(this));
        const newConvBtn = document.getElementById('newConversationBtn');
        if (newConvBtn) newConvBtn.addEventListener('click', () => {
            this.createNewConversation();
        });

        // Botones del Hero Panel
        const heroStartBtn = document.getElementById('heroStartConversation');
        if (heroStartBtn) {
            heroStartBtn.addEventListener('click', () => {
                this.messageInput.focus();
                // Opcional: Scroll hacia abajo si es necesario
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            });
        }

        const heroUploadBtn = document.getElementById('heroUploadDocs');
        if (heroUploadBtn) {
            heroUploadBtn.addEventListener('click', () => {
                if (fileInput) fileInput.click();
            });
        }

        const toggleThemeBtn = document.getElementById('toggleTheme');
        if (toggleThemeBtn) {
            toggleThemeBtn.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Toggle sidebar
        const toggleSidebarBtn = document.getElementById('toggleSidebar');
        if (toggleSidebarBtn) {
            toggleSidebarBtn.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        if (this.searchTrigger) {
            this.searchTrigger.addEventListener('click', () => {
                this.toggleSearchBox();
            });
        }

        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.handleSearchInput.bind(this));
            this.searchInput.addEventListener('blur', (e) => {
                // Si el input está vacío y no hay búsqueda activa, ocultar el search box
                // Pero esperar un poco para que el click en clear button funcione
                setTimeout(() => {
                    if (!this.searchInput.value.trim() && !this.searchQuery) {
                        this.hideSearchBox();
                    }
                }, 200);
            });
        }

        if (this.clearSearchBtn) {
            this.clearSearchBtn.addEventListener('click', () => {
                this.clearSearch();
                this.hideSearchBox();
            });
        }

        // Modal de configuración
        const closeSettingsBtn = document.getElementById('closeSettings');
        if (closeSettingsBtn) {
            closeSettingsBtn.addEventListener('click', this.closeSettings.bind(this));
        }
        const settingsModal = document.getElementById('settingsModal');
        if (settingsModal) {
            settingsModal.addEventListener('click', (e) => {
                if (e.target === e.currentTarget) {
                    this.closeSettings();
                }
            });
        }
        
        // Configuraciones
        this.bindSettingsEvents();
        
        // Auto-resize del textarea
        this.messageInput.addEventListener('input', this.autoResizeTextarea.bind(this));

        if (this.appLayout) {
            this.appLayout.addEventListener('click', this.handleLayoutClick.bind(this));
        }

        window.addEventListener('resize', this.handleWindowResize.bind(this));
    }

    bindSuggestions() {
        document.querySelectorAll('.suggestion-chip').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.currentTarget.dataset.question || e.currentTarget.textContent;
                this.messageInput.value = question.trim();
                this.handleInputChange();
                this.sendMessage();
            });
        });
    }

    bindSettingsEvents() {
        const themeSelect = document.getElementById('themeSelect');
        const fontSizeRange = document.getElementById('fontSizeRange');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const soundNotifications = document.getElementById('soundNotifications');
        const autoScroll = document.getElementById('autoScroll');

        themeSelect.addEventListener('change', (e) => {
            this.settings.theme = e.target.value;
            this.applyTheme();
            this.saveSettings();
        });

        fontSizeRange.addEventListener('input', (e) => {
            const size = e.target.value;
            this.settings.fontSize = size;
            fontSizeValue.textContent = size + 'px';
            this.applyFontSize();
            this.saveSettings();
        });

        soundNotifications.addEventListener('change', (e) => {
            this.settings.soundNotifications = e.target.checked;
            this.saveSettings();
        });

        autoScroll.addEventListener('change', (e) => {
            this.settings.autoScroll = e.target.checked;
            this.saveSettings();
        });
    }

    handleInputChange() {
        const value = this.messageInput.value;
        const length = value.length;
        
        // Actualizar contador de caracteres
        this.characterCount.textContent = `${length}/2000`;
        
        // Habilitar/deshabilitar botón de envío (permitir envío si hay imágenes en cola)
        const hasImagesQueued = Array.isArray(this.pendingImages) && this.pendingImages.length > 0;
        this.sendBtn.disabled = (!hasImagesQueued && (length === 0 || length > 2000));
        
        // Cambiar color del contador si se acerca al límite
        if (length > 1800) {
            this.characterCount.style.color = '#f56565';
        } else if (length > 1500) {
            this.characterCount.style.color = '#ed8936';
        } else {
            this.characterCount.style.color = 'var(--text-muted)';
        }
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!this.sendBtn.disabled) {
                this.sendMessage();
            }
        }
    }

    autoResizeTextarea() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        const hasImagesQueued = Array.isArray(this.pendingImages) && this.pendingImages.length > 0;
        if ((!message && !hasImagesQueued) || this.isTyping) return;

        // Si no hay conversación activa, crear una nueva
        if (!this.currentConversationId) {
            await this.createNewConversation();
        }

        // Agregar mensaje del usuario si hay texto
        if (message) {
            this.addMessage('user', message);
            await this.saveMessage('user', message);
        }

        // Renderizar imágenes en el chat como mensajes del usuario y preparar upload
        let uploadedFilesResult = null;
        if (hasImagesQueued) {
            for (const imgFile of this.pendingImages) {
                const url = URL.createObjectURL(imgFile);
                this.renderImageMessage({ role: 'user', src: url, name: imgFile.name });
            }
            try {
                const formData = new FormData();
                this.pendingImages.forEach(f => formData.append('files', f));
                const res = await fetch('/api/upload/batch', { method: 'POST', body: formData });
                uploadedFilesResult = await res.json();
                this.showToast(`Enviadas ${this.pendingImages.length} imagen(es)`, 'success');
            } catch (err) {
                console.error('Error subiendo imágenes:', err);
                this.showToast('Error al subir imágenes', 'error');
            }
        }
        
        // Limpiar input
        this.messageInput.value = '';
        this.handleInputChange();
        this.autoResizeTextarea();
        // Limpiar cola de imágenes
        this.pendingImages = [];
        const fileInput = document.getElementById('fileUploadInput');
        if (fileInput) fileInput.value = '';
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        try {
            // Enviar mensaje a la API
            const response = await this.callChatAPI(message);
            
            // Ocultar indicador de escritura
            this.hideTypingIndicator();
            
            const aiResponse = response.answer || 'Lo siento, no pude procesar tu pregunta.';
            
            // Agregar respuesta de ORIGEN
            this.addMessage('ai', aiResponse);
            
            // Guardar respuesta en el backend
            await this.saveMessage('ai', aiResponse);
            
            // Recargar la lista de conversaciones para actualizar el título
            await this.loadConversations();
            
            // Reproducir sonido si está habilitado
            if (this.settings.soundNotifications) {
                this.playNotificationSound();
            }
            
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            this.hideTypingIndicator();
            this.addMessage('ai', 'Lo siento, ocurrió un error. Por favor intenta de nuevo.');
            this.showToast('Error al enviar mensaje', 'error');
        }
    }

    async callChatAPI(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    addMessage(type, content, saveToHistory = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        const avatarIcon = type === 'user' ? 'fas fa-user' : 'fas fa-brain';
        const senderName = type === 'user' ? 'Tú' : 'ORIGEN';

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${this.formatMessage(content)}
                </div>
                <div class="message-time">${senderName} • ${timeString}</div>
            </div>
        `;

        // Remover mensaje de bienvenida si existe
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        this.messagesContainer.appendChild(messageDiv);
        
        // Scroll automático
        if (this.settings.autoScroll) {
            this.scrollToBottom();
        }

        // Guardar en historial local solo si se indica
        if (saveToHistory) {
            this.messageHistory.push({
                type,
                content,
                timestamp: now.toISOString()
            });
        }
    }

    formatMessage(content) {
        // Formatear el contenido del mensaje
        // Convertir saltos de línea
        let formatted = content.replace(/\n/g, '<br>');
        
        // Convertir URLs en enlaces
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        formatted = formatted.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Convertir texto en negrita
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convertir texto en cursiva
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        return formatted;
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        if (this.settings.autoScroll) {
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    async clearChat() {
        if (!confirm('¿Estás seguro de que quieres limpiar la conversación?')) {
            return;
        }
        
        if (this.currentConversationId) {
            try {
                const response = await fetch(`/api/conversations/${this.currentConversationId}/clear`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.messagesContainer.innerHTML = '';
                    this.messageHistory = [];
                    this.welcomeMessage();
                    this.updateConversationHeader('Nueva conversación', new Date());
                    await this.loadConversations();
                    this.showToast('Conversación limpiada', 'info');
                }
            } catch (error) {
                console.error('Error limpiando conversación:', error);
                this.showToast('Error al limpiar conversación', 'error');
            }
        } else {
            this.messagesContainer.innerHTML = '';
            this.messageHistory = [];
            this.welcomeMessage();
            this.showToast('Conversación limpiada', 'info');
        }
    }

    welcomeMessage() {
        // La bienvenida ya está en el HTML, solo necesitamos mostrarla
        setTimeout(() => {
            const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.style.animation = 'fadeInUp 0.6s ease-out';
            }
        }, 500);
    }

    renderImageMessage({ role = 'user', src, name }) {
        if (!this.messagesContainer || !src) return;
        const wrapper = document.createElement('div');
        wrapper.className = `message ${role}`;
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        const content = document.createElement('div');
        content.className = 'message-content';
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        const img = document.createElement('img');
        img.src = src;
        img.alt = name || 'imagen adjunta';
        img.style.maxWidth = '360px';
        img.style.borderRadius = '16px';
        img.style.display = 'block';
        bubble.appendChild(img);
        content.appendChild(bubble);
        wrapper.appendChild(avatar);
        wrapper.appendChild(content);
        this.messagesContainer.appendChild(wrapper);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async checkApiStatus() {
        try {
            const response = await fetch('/api/chat/health');
            const data = await response.json();
            
            const statusDot = this.statusIndicator.querySelector('.status-dot');
            const statusText = this.statusIndicator.querySelector('.status-text');
            
            if (data.status === 'healthy') {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'En línea';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'Fuera de línea';
            }
        } catch (error) {
            console.error('Error verificando estado de la API:', error);
            const statusDot = this.statusIndicator.querySelector('.status-dot');
            const statusText = this.statusIndicator.querySelector('.status-text');
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Error de conexión';
        }
    }

    openSettings() {
        const modal = document.getElementById('settingsModal');
        if (!modal) return;
        
        modal.style.display = 'flex';
        
        // Cargar valores actuales
        const themeSelect = document.getElementById('themeSelect');
        const fontSizeRange = document.getElementById('fontSizeRange');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const soundNotifications = document.getElementById('soundNotifications');
        const autoScroll = document.getElementById('autoScroll');
        
        if (themeSelect) themeSelect.value = this.settings.theme || 'light';
        if (fontSizeRange) fontSizeRange.value = this.settings.fontSize || 14;
        if (fontSizeValue) fontSizeValue.textContent = (this.settings.fontSize || 14) + 'px';
        if (soundNotifications) soundNotifications.checked = this.settings.soundNotifications || false;
        if (autoScroll) autoScroll.checked = this.settings.autoScroll !== false;
    }

    closeSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    loadSettings() {
        const defaultSettings = {
            theme: 'light',
            fontSize: 14,
            soundNotifications: false,
            autoScroll: true
        };

        try {
            const saved = localStorage.getItem('origen-settings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (error) {
            console.error('Error cargando configuración:', error);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('origen-settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('Error guardando configuración:', error);
        }
    }

    applySettings() {
        this.applyTheme();
        this.applyFontSize();
    }

    applyTheme() {
        const { theme } = this.settings;
        const root = document.documentElement;
        
        if (theme === 'dark') {
            root.classList.add('dark-theme');
            this.updateThemeIcon('dark');
        } else {
            root.classList.remove('dark-theme');
            this.updateThemeIcon('light');
        }
    }

    toggleTheme() {
        // Alternar entre claro y oscuro
        const currentTheme = this.settings.theme || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        this.settings.theme = newTheme;
        this.applyTheme();
        this.saveSettings();
        
        this.showToast(
            newTheme === 'dark' ? 'Tema oscuro activado' : 'Tema claro activado',
            'info'
        );
    }

    updateThemeIcon(theme) {
        const toggleBtn = document.getElementById('toggleTheme');
        if (!toggleBtn) return;
        const icon = toggleBtn.querySelector('i');
        if (!icon) return;

        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    toggleSidebar(forceExpand = null) {
        if (!this.appLayout) return;
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            const currentlyHidden = this.appLayout.classList.contains('sidebar-hidden');
            let hideSidebar;

            if (forceExpand === true) {
                hideSidebar = false;
            } else if (forceExpand === false) {
                hideSidebar = true;
            } else {
                hideSidebar = !currentlyHidden;
            }

            if (hideSidebar) {
                this.appLayout.classList.add('sidebar-hidden');
            } else {
                this.appLayout.classList.remove('sidebar-hidden');
            }

            localStorage.setItem('sidebarHidden', hideSidebar);
        } else {
            const currentlyCollapsed = this.appLayout.classList.contains('sidebar-collapsed');
            let collapseSidebar;

            if (forceExpand === true) {
                collapseSidebar = false;
            } else if (forceExpand === false) {
                collapseSidebar = true;
            } else {
                collapseSidebar = !currentlyCollapsed;
            }

            if (collapseSidebar) {
                this.appLayout.classList.add('sidebar-collapsed');
            } else {
                this.appLayout.classList.remove('sidebar-collapsed');
            }

            localStorage.setItem('sidebarCollapsed', collapseSidebar);
        }

        this.updateSidebarToggleIcon();
    }

    updateSidebarToggleIcon() {
        const toggleBtn = document.getElementById('toggleSidebar');
        if (!toggleBtn) return;
        const icon = toggleBtn.querySelector('i');
        if (!icon) return;

        if (window.innerWidth <= 768) {
            icon.className = 'fas fa-bars';
        } else if (this.appLayout && this.appLayout.classList.contains('sidebar-collapsed')) {
            icon.className = 'fas fa-angles-right';
        } else {
            icon.className = 'fas fa-angles-left';
        }
    }

    handleLayoutClick(event) {
        if (!this.appLayout) return;
        const isMobile = window.innerWidth <= 768;
        if (!isMobile) return;

        const sidebarIsHidden = this.appLayout.classList.contains('sidebar-hidden');
        if (!sidebarIsHidden && event.target === this.appLayout) {
            this.toggleSidebar(false);
        }
    }

    ensureSidebarExpandedForSearch() {
        if (!this.appLayout) return;

        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            this.toggleSidebar(true);
        } else if (this.appLayout.classList.contains('sidebar-collapsed')) {
            this.toggleSidebar(true);
        }
    }

    toggleSearchBox() {
        const searchBox = document.querySelector('.search-box');
        if (!searchBox) return;

        // Asegurar que el sidebar esté expandido
        this.ensureSidebarExpandedForSearch();

        // Mostrar el search box y ocultar el botón trigger
        if (this.searchTrigger) {
            this.searchTrigger.style.display = 'none';
        }
        searchBox.classList.remove('hidden');
        
        // Hacer focus en el input
        if (this.searchInput) {
            setTimeout(() => {
                this.searchInput.focus();
            }, 100);
        }
    }

    hideSearchBox() {
        const searchBox = document.querySelector('.search-box');
        if (!searchBox) return;

        // Ocultar el search box y mostrar el botón trigger
        searchBox.classList.add('hidden');
        if (this.searchTrigger) {
            this.searchTrigger.style.display = 'flex';
        }
    }

    handleSearchInput(event) {
        this.searchQuery = event.target.value.trim().toLowerCase();
        this.updateSearchControls();
        this.renderConversationsList();
    }

    clearSearch() {
        this.searchQuery = '';
        if (this.searchInput) {
            this.searchInput.value = '';
        }
        this.updateSearchControls();
        this.renderConversationsList();
    }

    updateSearchControls() {
        if (this.clearSearchBtn) {
            if (this.searchQuery.length > 0) {
                this.clearSearchBtn.classList.remove('hidden');
            } else {
                this.clearSearchBtn.classList.add('hidden');
            }
        }
    }

    handleWindowResize() {
        if (!this.appLayout) return;

        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            this.appLayout.classList.remove('sidebar-collapsed');
            const storedHidden = localStorage.getItem('sidebarHidden');
            if (storedHidden === 'false') {
                this.appLayout.classList.remove('sidebar-hidden');
            } else {
                this.appLayout.classList.add('sidebar-hidden');
                if (storedHidden === null) {
                    localStorage.setItem('sidebarHidden', 'true');
                }
            }
        } else {
            this.appLayout.classList.remove('sidebar-hidden');
            const storedCollapsed = localStorage.getItem('sidebarCollapsed');
            if (storedCollapsed === 'true') {
                this.appLayout.classList.add('sidebar-collapsed');
            } else {
                this.appLayout.classList.remove('sidebar-collapsed');
                if (storedCollapsed === null) {
                    localStorage.setItem('sidebarCollapsed', 'false');
                }
            }
        }

        this.updateSidebarToggleIcon();
    }

    applyFontSize() {
        document.documentElement.style.setProperty('--base-font-size', this.settings.fontSize + 'px');
    }

    playNotificationSound() {
        // Crear un sonido de notificación simple
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    showToast(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Remover después del tiempo especificado
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    // Método para exportar conversación
    exportChat() {
        const data = {
            timestamp: new Date().toISOString(),
            messages: this.messageHistory
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `origen-chat-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Conversación exportada', 'success');
    }

    // Método para importar conversación
    importChat(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.messages && Array.isArray(data.messages)) {
                    this.messageHistory = data.messages;
                    this.renderChatHistory();
                    this.showToast('Conversación importada', 'success');
                } else {
                    throw new Error('Formato de archivo inválido');
                }
            } catch (error) {
                console.error('Error importando chat:', error);
                this.showToast('Error al importar conversación', 'error');
            }
        };
        reader.readAsText(file);
    }

    renderChatHistory() {
        this.messagesContainer.innerHTML = '';
        this.messageHistory.forEach(msg => {
            this.addMessage(msg.type, msg.content);
        });
    }

    // ==================== MÉTODOS DE GESTIÓN DE CONVERSACIONES ====================

    async loadConversations() {
        try {
            const response = await fetch('/api/conversations/');
            const data = await response.json();
            
            if (data.success) {
                this.conversations = data.conversations;
                this.renderConversationsList();
            }
        } catch (error) {
            console.error('Error cargando conversaciones:', error);
        }
    }

    renderConversationsList() {
        const emptyState = document.getElementById('emptyConversations');
        const noResults = this.noResultsMessage;
        const query = (this.searchQuery || '').trim().toLowerCase();

        this.updateSearchControls();

        if (this.conversations.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
            if (noResults) noResults.style.display = 'none';
            this.clearConversationItems();
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        const filtered = query
            ? this.conversations.filter(conv => (conv.title || '').toLowerCase().includes(query))
            : this.conversations;

        if (filtered.length === 0) {
            if (noResults) noResults.style.display = 'block';
            this.clearConversationItems();
            return;
        }

        if (noResults) noResults.style.display = 'none';

        this.clearConversationItems();

        filtered.forEach(conv => {
            const item = this.createConversationItem(conv);
            this.conversationsList.appendChild(item);
        });
    }

    clearConversationItems() {
        if (!this.conversationsList) return;
        const items = this.conversationsList.querySelectorAll('.conversation-item');
        items.forEach(item => item.remove());
    }

    createConversationItem(conversation) {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conversation.id === this.currentConversationId) {
            item.classList.add('active');
        }
        const title = (conversation.title || 'Nueva conversación').trim();
        item.title = title;
        item.dataset.title = title.toLowerCase();
        
        const date = new Date(conversation.updated_at);
        const dateStr = this.formatConversationDate(date);
        
        item.innerHTML = `
            <div class="conversation-main">
                <div class="conversation-meta">
                    <div class="conversation-title">${this.escapeHtml(title)}</div>
                    <div class="conversation-date">${dateStr}</div>
                </div>
            </div>
            <div class="conversation-actions">
                <button class="conversation-action-btn delete-btn" data-id="${conversation.id}" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        // Evento para cargar la conversación
        item.addEventListener('click', () => {
            this.loadConversation(conversation.id);
        });
        
        // Evento para eliminar
        const deleteBtn = item.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteConversation(conversation.id);
        });
        
        return item;
    }

    formatConversationDate(date) {
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days === 0) {
            return 'Hoy';
        } else if (days === 1) {
            return 'Ayer';
        } else if (days < 7) {
            return `Hace ${days} días`;
        } else if (days < 30) {
            const weeks = Math.floor(days / 7);
            return `Hace ${weeks} ${weeks === 1 ? 'semana' : 'semanas'}`;
        } else {
            return date.toLocaleDateString('es-ES', { 
                day: 'numeric', 
                month: 'short',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async createNewConversation() {
        try {
            const response = await fetch('/api/conversations/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentConversationId = data.conversation.id;
                this.messagesContainer.innerHTML = '';
                this.messageHistory = [];
                this.welcomeMessage();
                this.updateConversationHeader('Nueva conversación', new Date());
                await this.loadConversations();
                this.showToast('Nueva conversación creada', 'success');
            }
        } catch (error) {
            console.error('Error creando conversación:', error);
            this.showToast('Error al crear conversación', 'error');
        }
    }

    async loadConversation(conversationId) {
        try {
            const response = await fetch(`/api/conversations/${conversationId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentConversationId = conversationId;
                this.messagesContainer.innerHTML = '';
                this.messageHistory = [];
                
                const conversation = data.conversation;
                
                // Actualizar header
                this.updateConversationHeader(conversation.title, new Date(conversation.created_at));
                
                // Renderizar mensajes
                if (conversation.messages && conversation.messages.length > 0) {
                    conversation.messages.forEach(msg => {
                        this.addMessage(msg.type, msg.content, false);
                        this.messageHistory.push(msg);
                    });
                } else {
                    this.welcomeMessage();
                }
                
                // Actualizar UI
                this.renderConversationsList();
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error cargando conversación:', error);
            this.showToast('Error al cargar conversación', 'error');
        }
    }

    async deleteConversation(conversationId) {
        if (!confirm('¿Estás seguro de que quieres eliminar esta conversación?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/conversations/${conversationId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Si era la conversación activa, crear una nueva
                if (conversationId === this.currentConversationId) {
                    this.currentConversationId = null;
                    this.messagesContainer.innerHTML = '';
                    this.messageHistory = [];
                    this.welcomeMessage();
                    this.updateConversationHeader('Nueva conversación', new Date());
                }
                
                await this.loadConversations();
                this.showToast('Conversación eliminada', 'success');
            }
        } catch (error) {
            console.error('Error eliminando conversación:', error);
            this.showToast('Error al eliminar conversación', 'error');
        }
    }

    async saveMessage(type, content) {
        if (!this.currentConversationId) return;
        
        try {
            await fetch(`/api/conversations/${this.currentConversationId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: type,
                    content: content
                })
            });
        } catch (error) {
            console.error('Error guardando mensaje:', error);
        }
    }

    updateConversationHeader(title, date) {
        this.conversationTitle.textContent = title;
        this.conversationDate.textContent = this.formatConversationDate(date);
    }

    async handleFileUpload(e) {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        // Mostrar indicador de carga o mensaje temporal
        this.showToast(`Subiendo ${files.length} archivo(s)...`, 'info');

        try {
            const response = await fetch('/api/upload/batch', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showToast('Archivos subidos correctamente', 'success');
            
            // Opcional: Agregar mensaje al chat indicando que se subieron archivos
            this.addMessage('user', `[Archivos adjuntos: ${Array.from(files).map(f => f.name).join(', ')}]`);
            
            // Limpiar el input para permitir subir el mismo archivo de nuevo si es necesario
            e.target.value = '';

        } catch (error) {
            console.error('Error subiendo archivos:', error);
            this.showToast('Error al subir archivos', 'error');
        }
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.origenChat = new OrigenChat();
    
    // Verificar estado de la API cada 30 segundos
    setInterval(() => {
        window.origenChat.checkApiStatus();
    }, 30000);
});

// Manejar eventos de teclado globales
document.addEventListener('keydown', (e) => {
    // Cerrar modal con Escape
    if (e.key === 'Escape') {
        const modal = document.getElementById('settingsModal');
        if (modal.style.display === 'flex') {
            window.origenChat.closeSettings();
        }
    }
    
    // Enfocar input con Ctrl/Cmd + /
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        document.getElementById('messageInput').focus();
    }
});

// Manejar cambios en el tema del sistema
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (window.origenChat && window.origenChat.settings.theme === 'auto') {
        window.origenChat.applyTheme();
    }
});

// Evitar que la página se recargue al arrastrar archivos
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
});

// Agregar estilos para slideOutRight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(300px);
        }
    }
`;
document.head.appendChild(style);