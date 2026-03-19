document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('[data-url]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            window.location.href = this.dataset.url;
        });
    });

});