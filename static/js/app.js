// static/js/app.js

// State
let allNews = [];
let filteredNews = [];
let currentCategory = 'all';
let displayedCount = 6;

// Category mapping
const categoryMap = {
    'europe': 'Europe',
    'asia': 'Asia',
    'middle-east': 'Middle East',
    'usa': 'USA',
    'all': 'all'
};

const categoryLabels = {
    'europe': 'Европа',
    'asia': 'Азия',
    'middle-east': 'Ближний Восток',
    'usa': 'США',
    'all': 'Все'
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 App initialized');
    loadNews();
    setupEventListeners();
});

// Load news from API
async function loadNews() {
    try {
        console.log('📡 Fetching news from /api/news...');
        const response = await fetch('/api/news');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        allNews = await response.json();
        console.log(`✅ Loaded ${allNews.length} news articles`);

        filteredNews = [...allNews];
        updateCategoryCounts();
        updateStats();
        renderNews();
    } catch (error) {
        console.error('❌ Error loading news:', error);
        document.getElementById('newsGrid').innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">⚠️</div>
                <h3 class="empty-state-title">Ошибка загрузки</h3>
                <p class="empty-state-text">Проверьте подключение к серверу</p>
            </div>
        `;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Main nav buttons
    document.querySelectorAll('.main-nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            setCategory(btn.dataset.category);
        });
    });

    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            setCategory(tab.dataset.category);
        });
    });

    // Sidebar categories
    document.querySelectorAll('#sidebarCategories .category-item').forEach(item => {
        item.addEventListener('click', () => {
            setCategory(item.dataset.category);
        });
    });

    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            filterNews(e.target.value);
        }, 300));
    }

    // Load more button
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            displayedCount += 6;
            renderNews();
        });
    }
}

// Set active category
function setCategory(category) {
    console.log(`📂 Switching to category: ${category}`);
    currentCategory = category;
    displayedCount = 6;

    // Update main nav
    document.querySelectorAll('.main-nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });

    // Update category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.category === category);
    });

    // Update sidebar categories
    document.querySelectorAll('#sidebarCategories .category-item').forEach(item => {
        item.classList.toggle('active', item.dataset.category === category);
    });

    // Filter news
    filterNews(document.getElementById('searchInput').value);
}

// Filter news by category and search
function filterNews(searchQuery = '') {
    let news = [...allNews];

    // Filter by category
    if (currentCategory !== 'all') {
        const categoryLabel = categoryMap[currentCategory];
        news = news.filter(n => {
            const newsCategory = (n.category || '').toLowerCase();
            return newsCategory.includes(categoryLabel.toLowerCase());
        });
    }

    // Filter by search query
    if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        news = news.filter(n =>
            (n.title || '').toLowerCase().includes(query) ||
            (n.description || '').toLowerCase().includes(query)
        );
    }

    // Sort by date (newest first)
    news.sort((a, b) => new Date(b.date) - new Date(a.date));

    filteredNews = news;
    renderNews();
}

// Render news cards
function renderNews() {
    const grid = document.getElementById('newsGrid');
    const loadMoreBtn = document.getElementById('loadMoreBtn');

    if (!grid) return;

    if (filteredNews.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">📰</div>
                <h3 class="empty-state-title">Ничего не найдено</h3>
                <p class="empty-state-text">Попробуйте изменить поисковый запрос или выбрать другую категорию</p>
            </div>
        `;
        if (loadMoreBtn) loadMoreBtn.disabled = true;
        return;
    }

    const visibleNews = filteredNews.slice(0, displayedCount);
    grid.innerHTML = visibleNews.map(news => createNewsCard(news)).join('');

    // Update load more button
    if (loadMoreBtn) {
        loadMoreBtn.disabled = displayedCount >= filteredNews.length;
        loadMoreBtn.style.display = displayedCount >= filteredNews.length ? 'none' : 'inline-block';
    }
}

// Create news card HTML
function createNewsCard(news) {
    const categoryClass = (news.category || 'international').toLowerCase().replace(' ', '-');
    const categoryLabel = categoryLabels[categoryClass] || news.category || 'International';
    const date = new Date(news.date).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });

    return `
        <article class="news-card" onclick="window.open('${news.url || '#'}', '_blank')">
            <div class="news-card-image placeholder">📰</div>
            <div class="news-card-content">
                <span class="news-card-category ${categoryClass}">${escapeHtml(categoryLabel)}</span>
                <h3 class="news-card-title">${escapeHtml(news.title || 'Без заголовка')}</h3>
                <p class="news-card-description">${escapeHtml(news.description || news.title || '')}</p>
                <div class="news-card-meta">
                    <span class="news-card-source">${escapeHtml(news.source || 'Unknown')}</span>
                    <span class="news-card-date">${date}</span>
                </div>
            </div>
        </article>
    `;
}

// Update category counts
function updateCategoryCounts() {
    const counts = {
        'all': allNews.length,
        'europe': allNews.filter(n => (n.category || '').toLowerCase().includes('europe')).length,
        'asia': allNews.filter(n => (n.category || '').toLowerCase().includes('asia')).length,
        'middle-east': allNews.filter(n => (n.category || '').toLowerCase().includes('middle')).length,
        'usa': allNews.filter(n => (n.category || '').toLowerCase().includes('usa')).length
    };

    Object.keys(counts).forEach(cat => {
        const el = document.getElementById(`count-${cat}`);
        if (el) el.textContent = counts[cat];
    });
}

// Update statistics
function updateStats() {
    const totalEl = document.getElementById('totalNews');
    const todayEl = document.getElementById('todayNews');

    if (totalEl) totalEl.textContent = allNews.length;

    if (todayEl) {
        const today = new Date().toDateString();
        const todayCount = allNews.filter(n => new Date(n.date).toDateString() === today).length;
        todayEl.textContent = todayCount;
    }
}

// Show info modal
function showInfo(type) {
    const messages = {
        'about': 'MOIMP-PROJECT — Политический Агрегатор Новостей\n\nВерсия: 1.0.0\nРазработано в 2026 году',
        'settings': 'Настройки\n\n🔔 Уведомления: Включено\n🌐 Язык: Русский\n📱 Тема: Тёмная'
    };
    alert(messages[type] || 'Информация недоступна');
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}