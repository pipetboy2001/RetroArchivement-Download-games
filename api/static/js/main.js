class RetroDownloader {
    constructor() {
        this.searchTimeout = null;
        this.currentSearchMode = 'name';
        this.i18n = window.__i18n || {
            noResults: 'No se encontraron juegos',
            searchError: 'Error en la búsqueda',
            versionsOf: 'Versiones de:',
            loadingVersions: 'Cargando versiones...',
            recommended: '✅ Recomendada',
            translation: 'TRADUCCIÓN',
            searching: 'Buscando en la base de datos...',
            downloading: 'Descargando...',
            downloaded: '¡Descargado!',
            loadVersionsError: 'No se pudieron cargar las versiones',
            loadVersionsGenericError: 'Error al cargar las versiones',
            notFoundHash: 'No se encontró el hash en la base de datos.',
            serverJsonError: 'No se pudo descargar el JSON desde la URL.',
            searchGameError: 'Error al buscar el juego.'
        };
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeUI();
    }

    bindEvents() {
        // Search mode toggle
        $('#nameSearchMode').on('click', () => this.switchToNameSearch());
        $('#hashSearchMode').on('click', () => this.switchToHashSearch());

        // Real-time name search
        $('#gameName').on('input', (e) => this.handleNameSearch(e.target.value));

        // Search result selection
        $(document).on('click', '.search-result-item', (e) => this.selectSearchResult(e));

        // Version selection
        $(document).on('click', '.version-option', (e) => this.selectVersion(e));

        // Hash search form
        $('#hashSearchForm').on('submit', (e) => this.handleHashSearch(e));

        // Hide search results when clicking outside
        $(document).on('click', (e) => this.handleOutsideClick(e));

        // Modal events
        this.bindModalEvents();
    }

    bindModalEvents() {
        // Close modals when clicking outside
        $(document).on('click', '.modal-overlay', (e) => {
            if (e.target === e.currentTarget) {
                this.closeAllModals();
            }
        });

        // ESC key to close modals
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    initializeUI() {
        // Add modal overlay class to modal backgrounds
        $('#versionsModal, #instructionsModal').addClass('modal-overlay');
    }

    switchToNameSearch() {
        this.currentSearchMode = 'name';
        $('#nameSearchMode')
            .removeClass('bg-gray-200 text-gray-700')
            .addClass('bg-retro-blue text-white');
        $('#hashSearchMode')
            .removeClass('bg-retro-blue text-white')
            .addClass('bg-gray-200 text-gray-700');
        
        $('#nameSearchForm').removeClass('hidden').addClass('slide-in');
        $('#hashSearchForm').addClass('hidden');
        $('#searchResults').addClass('hidden');
        this.clearStatus();
    }

    switchToHashSearch() {
        this.currentSearchMode = 'hash';
        $('#hashSearchMode')
            .removeClass('bg-gray-200 text-gray-700')
            .addClass('bg-retro-blue text-white');
        $('#nameSearchMode')
            .removeClass('bg-retro-blue text-white')
            .addClass('bg-gray-200 text-gray-700');
        
        $('#hashSearchForm').removeClass('hidden').addClass('slide-in');
        $('#nameSearchForm').addClass('hidden');
        $('#searchResults').addClass('hidden');
        this.clearStatus();
    }

    handleNameSearch(searchTerm) {
        clearTimeout(this.searchTimeout);
        
        if (searchTerm.trim().length < 2) {
            this.hideSearchResults();
            return;
        }

        this.searchTimeout = setTimeout(() => {
            this.searchGames(searchTerm.trim());
        }, 300);
    }

    async searchGames(searchTerm) {
        try {
            const response = await $.post('/search_games', { search_term: searchTerm });
            
            if (response.success && response.games.length > 0) {
                this.displaySearchResults(response.games);
            } else {
                this.displayNoResults();
            }
        } catch (error) {
            console.error('Search error:', error);
            this.displaySearchError();
        }
    }

    displaySearchResults(games) {
        let resultsHtml = '';
        
        games.forEach(game => {
            const versionBadge = game.total_versions > 1 
                ? `<span class="badge-primary text-xs">${game.total_versions} versiones</span>`
                : '';
            
            const regionTag = game.primary_info.region !== 'Unknown'
                ? `<span class="badge-success text-xs">${game.primary_info.region}</span>`
                : '';
            
            const hackTag = game.primary_info.is_hack
                ? `<span class="badge-warning text-xs">HACK</span>`
                : '';
            
            resultsHtml += `
                <div class="search-result-item p-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors duration-200" 
                     data-game-id="${game.id}" 
                     data-hash="${game.hash}" 
                     data-name="${game.name}" 
                     data-versions="${game.total_versions}">
                    <div class="flex justify-between items-start mb-1">
                        <h3 class="font-medium text-gray-800 text-sm">${game.name}</h3>
                        ${versionBadge}
                    </div>
                    <div class="flex flex-wrap gap-1 mb-1">
                        ${regionTag}${hackTag}
                    </div>
                    <p class="text-xs text-gray-600">
                        ID: ${game.id} | Hash: ${game.hash.substring(0, 16)}...
                    </p>
                </div>
            `;
        });
        
        $('#searchResults').html(resultsHtml).removeClass('hidden').addClass('fade-in');
    }

    displayNoResults() {
        $('#searchResults')
            .html(`<div class="p-3 text-center text-gray-600 text-sm">${this.i18n.noResults}</div>`)
            .removeClass('hidden')
            .addClass('fade-in');
    }

    displaySearchError() {
        $('#searchResults')
            .html(`<div class="p-3 text-center text-red-600 text-sm">${this.i18n.searchError}</div>`)
            .removeClass('hidden')
            .addClass('fade-in');
    }

    hideSearchResults() {
        $('#searchResults').addClass('hidden');
    }

    selectSearchResult(event) {
        const $item = $(event.currentTarget);
        const hash = $item.data('hash');
        const gameName = $item.data('name');
        const gameId = $item.data('game-id');
        const totalVersions = $item.data('versions');
        
        if (!hash) return;
        
        this.hideSearchResults();
        $('#gameName').val(gameName);
        
        if (totalVersions > 1) {
            this.showVersionsModal(gameId, gameName);
        } else {
            this.downloadGame(hash);
        }
    }

    async showVersionsModal(gameId, gameName) {
        $('#versionsModalLabel').html(`
            <span class="text-3xl">🎮</span>
            ${this.i18n.versionsOf} ${gameName}
        `);
        $('#versionsContainer').html(`
            <div class="text-center py-8">
                <div class="spinner mx-auto mb-4"></div>
                <p class="text-gray-600">${this.i18n.loadingVersions}</p>
            </div>
        `);
        
        this.openModal('versionsModal');
        
        try {
            const response = await $.post('/get_game_versions', { game_id: gameId });
            
            if (response.success && response.versions.length > 0) {
                this.displayVersions(response.versions);
            } else {
                this.displayVersionsError(this.i18n.loadVersionsError);
            }
        } catch (error) {
            console.error('Versions loading error:', error);
            this.displayVersionsError(this.i18n.loadVersionsGenericError);
        }
    }

    displayVersions(versions) {
        let versionsHtml = '';
        
        versions.forEach((version, index) => {
            const isRecommended = index === 0;
            const recommendedClass = isRecommended ? 'border-green-500 bg-green-50' : 'border-gray-200';
            const recommendedBadge = isRecommended 
                ? `<span class="badge-success text-xs">${this.i18n.recommended}</span>` 
                : '';
            
            const regionTag = version.info.region !== 'Unknown'
                ? `<span class="badge-success text-xs">${version.info.region}</span>`
                : '';
            
            const hackTag = version.info.is_hack
                ? `<span class="badge-warning text-xs">HACK</span>`
                : '';
            
            const translationTag = version.info.is_translation
                ? `<span class="badge-warning text-xs">${this.i18n.translation}</span>`
                : '';
            
            versionsHtml += `
                <div class="version-option border ${recommendedClass} rounded-lg p-3 hover:shadow-md transition-all duration-300 cursor-pointer" 
                     data-hash="${version.hash}">
                    <div class="flex justify-between items-start mb-1">
                        <h4 class="font-medium text-gray-800 text-sm">${version.info.filename}</h4>
                        ${recommendedBadge}
                    </div>
                    <div class="flex flex-wrap gap-1 mb-1">
                        ${regionTag}${hackTag}${translationTag}
                    </div>
                    <p class="text-xs text-gray-600">Hash: ${version.hash}</p>
                </div>
            `;
        });
        
        $('#versionsContainer').html(versionsHtml);
    }

    displayVersionsError(message) {
        $('#versionsContainer').html(`
            <div class="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg text-center">
                <span class="text-2xl">⚠️</span>
                <p class="mt-2">${message}</p>
            </div>
        `);
    }

    selectVersion(event) {
        const hash = $(event.currentTarget).data('hash');
        this.closeModal('versionsModal');
        this.downloadGame(hash);
    }

    handleHashSearch(event) {
        event.preventDefault();
        const searchTerm = $('#searchTerm').val().trim();
        if (searchTerm) {
            this.downloadGame(searchTerm);
        }
    }

    async downloadGame(hash) {
        console.log("Descarga iniciada para hash:", hash);
        
    this.setStatus(this.i18n.searching, 'info');
        this.showSpinner();

        try {
            const response = await $.post("/search", { search_term: hash });
            
            if (response.success) {
                this.setStatus(this.i18n.downloading, 'info');
                
                setTimeout(() => {
                    this.setStatus(this.i18n.downloaded, 'success');
                    this.hideSpinner();
                    window.open(response.download_url);
                }, 1000);
            } else {
                this.setStatus(response.message, 'error');
                this.hideSpinner();
            }
        } catch (error) {
            console.error("Error al buscar el juego:", error);
            
            let errorMessage = this.i18n.searchGameError;
            if (error.status === 404) {
                errorMessage = this.i18n.notFoundHash;
            } else if (error.status === 500) {
                errorMessage = this.i18n.serverJsonError;
            }
            
            this.setStatus(errorMessage, 'error');
            this.hideSpinner();
        }
    }

    handleOutsideClick(event) {
        if (!$(event.target).closest('.relative').length) {
            this.hideSearchResults();
        }
    }

    // UI Helper Methods
    setStatus(message, type = 'info') {
        const statusClass = type === 'success' ? 'status-success' : 
                           type === 'error' ? 'status-error' : 'status-info';
        
        $('#statusWrapper').removeClass('hidden');
        $('#status')
            .removeClass('status-success status-error status-info')
            .addClass(statusClass)
            .text(message);
    }

    clearStatus() {
        $('#status').text('').removeClass('status-success status-error status-info');
        if ($('#spinner').hasClass('hidden')) {
            $('#statusWrapper').addClass('hidden');
        }
    }

    showSpinner() {
        $('#statusWrapper').removeClass('hidden');
        $('#spinner').removeClass('hidden').addClass('flex');
    }

    hideSpinner() {
        $('#spinner').addClass('hidden').removeClass('flex');
        if (!$('#status').text().trim()) {
            $('#statusWrapper').addClass('hidden');
        }
    }

    openModal(modalId) {
        $(`#${modalId}`).removeClass('hidden').addClass('flex');
        $('body').addClass('overflow-hidden');
    }

    closeModal(modalId) {
        $(`#${modalId}`).addClass('hidden').removeClass('flex');
        $('body').removeClass('overflow-hidden');
    }

    closeAllModals() {
        $('.fixed.inset-0').addClass('hidden').removeClass('flex');
        $('body').removeClass('overflow-hidden');
    }
}

// Global modal functions for onclick events
window.openModal = function(modalId) {
    window.retroDownloader.openModal(modalId);
};

window.closeModal = function(modalId) {
    window.retroDownloader.closeModal(modalId);
};

// Initialize when document is ready
$(document).ready(function() {
    window.retroDownloader = new RetroDownloader();
});
