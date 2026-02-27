/* static/js/main.js */
// ===== إدارة Dark Mode والواجهة =====

document.addEventListener('DOMContentLoaded', function () {
    // 1. التحقق من وجود الوضع المختار محفوظ مسبقاً
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // 2. إعداد زر تبديل الأوضاع
    setupThemeToggle();

    // 3. تفعيل القائمة الجانبية للجوال
    setupMobileSidebar();

    // 4. تفعيل العناصر النشطة في القائمة
    setupActiveNav();

    // 5. تهيئة وضع رمضان
    initRamadan();
});

// دالة تهيئة وضع رمضان
function initRamadan() {
    const isRamadan = localStorage.getItem('ramadanMode') === 'enabled';
    if (isRamadan) {
        document.documentElement.setAttribute('data-ramadan', 'enabled');
        generateStars();
    }
}

// دالة تبديل وضع رمضان
window.toggleRamadan = function () {
    const currentState = document.documentElement.getAttribute('data-ramadan');
    const newState = currentState === 'enabled' ? 'disabled' : 'enabled';

    document.documentElement.setAttribute('data-ramadan', newState);
    localStorage.setItem('ramadanMode', newState);

    if (newState === 'enabled') {
        generateStars();
        showFestiveEffect();
    } else {
        removeStars();
    }
};

function generateStars() {
    let container = document.querySelector('.ramadan-stars');
    if (!container) {
        container = document.createElement('div');
        container.className = 'ramadan-stars';
        document.body.prepend(container);
    }
    container.innerHTML = '';

    for (let i = 0; i < 50; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 3 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.setProperty('--duration', `${Math.random() * 3 + 2}s`);
        star.style.animationDelay = `${Math.random() * 5}s`;
        container.appendChild(star);
    }
}

function removeStars() {
    const container = document.querySelector('.ramadan-stars');
    if (container) container.innerHTML = '';
}

function showFestiveEffect() {
    // Simple alert or micro-animation for the first toggle
    console.log('رمضان كريم! 🌙✨');
}

// دالة تطبيق السمة
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.classList.remove('dark-mode'); // Clean up old class approach

    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
}

// دالة إعداد زر تبديل السمات (دائري)
function setupThemeToggle() {
    const toggle = document.querySelector('.dark-mode-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        let nextTheme = 'light';

        if (currentTheme === 'light') {
            nextTheme = 'dark';
        } else if (currentTheme === 'dark') {
            // Only allow Gold Mode for Admin
            if (window.userRole === 'admin') {
                nextTheme = 'gold';
            } else {
                nextTheme = 'light';
            }
        } else {
            nextTheme = 'light';
        }

        applyTheme(nextTheme);
    });
}

// دالة تحديث الأيقونة
function updateThemeIcon(theme) {
    const icon = document.querySelector('.dark-mode-toggle i');
    if (icon) {
        if (theme === 'light') icon.className = 'fas fa-water';
        else if (theme === 'dark') icon.className = 'fas fa-moon';
        else if (theme === 'gold') icon.className = 'fas fa-crown';
    }
}

// دالة إعداد القائمة الجانبية للجوال
function setupMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.querySelector('.menu-toggle-btn');
    const mainContent = document.querySelector('.main-content');

    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });

        // إغلاق عند النقر بالخارج
        document.addEventListener('click', function (e) {
            if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

// دالة تفعيل الكلاس النشط عند الضغط
function setupActiveNav() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function () {
            // إزالة الكلاس النشط من الجميع
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            // إضافة النشط للعنصر الحالي
            this.classList.add('active');

            // إغلاق القائمة في الجوال بعد النقر
            if (window.innerWidth <= 992) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar) sidebar.classList.remove('open');
            }
        });
    });
}

// تصدير دالة التبديل للاستخدام المباشر إذا لزم الأمر
window.toggleSidebar = function () {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('open');
};

// 5. تسجيل الـ Service Worker لدعم PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js').then(function (registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, function (err) {
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}
