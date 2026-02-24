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
});

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
