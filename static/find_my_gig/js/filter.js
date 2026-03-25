document.addEventListener('DOMContentLoaded', function () {
    const filterBtn = document.getElementById('filter-btn');

    if (filterBtn) {
        filterBtn.addEventListener('click', function () {
            const instrumentFilter = document.getElementById('filter-instrument')?.value || '';
            const params = new URLSearchParams();
            if (instrumentFilter) params.append('instrument', instrumentFilter);
            window.location.href = window.location.pathname + '?' + params.toString();
        });
    }
});