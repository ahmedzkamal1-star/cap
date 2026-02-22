// Toggle Sidebar Visibility
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('hidden');
    }
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function (event) {
    const sidebar = document.querySelector('.sidebar');
    const hamburger = document.querySelector('.hamburger-menu');

    if (sidebar && hamburger) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnHamburger = hamburger.contains(event.target);

        if (!isClickInsideSidebar && !isClickOnHamburger && !sidebar.classList.contains('hidden')) {
            sidebar.classList.add('hidden');
        }
    }
});
