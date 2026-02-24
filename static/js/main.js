/* static/js/main.js */
// ===== إدارة Dark Mode والواجهة =====

document.addEventListener('DOMContentLoaded', function () {
    // 1. التحقق من وجود الوضع المظلم محفوظ مسبقاً
    const darkMode = localStorage.getItem('darkMode') === 'enabled';
    if (darkMode) {
        document.body.classList.add('dark-mode');
        document.documentElement.setAttribute('data-theme', 'dark');
        updateDarkModeIcon(true);
    }

    // 2. إعداد زر Dark Mode
    setupDarkModeToggle();

    // 3. تفعيل القائمة الجانبية للجوال
    setupMobileSidebar();

    // 4. تفعيل العناصر النشطة في القائمة
    setupActiveNav();
});

// دالة إعداد زر Dark Mode
function setupDarkModeToggle() {
    const toggle = document.querySelector('.dark-mode-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', function () {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');

        // تحديث السمة في html للتوافق مع CSS
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');

        // حفظ الحالة في localStorage
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');

        // تحديث الأيقونة
        updateDarkModeIcon(isDark);
    });
}

// دالة تحديث أيقونة Dark Mode
function updateDarkModeIcon(isDark) {
    const icon = document.querySelector('.dark-mode-toggle i');
    if (icon) {
        icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
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
