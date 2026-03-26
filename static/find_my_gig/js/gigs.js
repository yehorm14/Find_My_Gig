document.addEventListener('DOMContentLoaded', function () {

    // ==========================================================================
    // 1. GIG LIST PAGE LOGIC (APPLY / BOOKMARK)
    // ==========================================================================
    const gigsList = document.getElementById('gigs-list');

    if (gigsList) {
        gigsList.addEventListener('click', function (e) {
            
            // --- Apply / Withdraw Actions ---
            const applyBtn = e.target.closest('.apply-btn') || e.target.closest('.withdraw-btn');
            if (applyBtn) {
                const isApplying = applyBtn.classList.contains('apply-btn');
                const gigId = applyBtn.dataset.gigId;

                if (!isLoggedIn()) { redirectToLogin(); return; }
                if (!isApplying && !confirm('Are you sure you want to withdraw your application?')) return;

                const url = isApplying ? `/gigs/${gigId}/apply/` : `/gigs/${gigId}/withdraw/`;

                fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        applyBtn.textContent = isApplying ? 'Withdraw' : 'Apply';
                        applyBtn.classList.toggle('apply-btn');
                        applyBtn.classList.toggle('withdraw-btn');
                        applyBtn.classList.toggle('btn-primary');
                        applyBtn.classList.toggle('btn-danger');
                        showStatusMessage('status-message', isApplying ? 'Application submitted!' : 'Application withdrawn.', 'success');
                    } else {
                        showStatusMessage('status-message', data.error || 'Something went wrong', 'error');
                    }
                })
                .catch(() => showStatusMessage('status-message', 'Network error.', 'error'));
            }

            // --- Bookmark / Unbookmark Actions ---
            const bookmarkBtn = e.target.closest('.bookmark-btn') || e.target.closest('.bookmarked-btn');
            if (bookmarkBtn) {
                const gigId = bookmarkBtn.dataset.gigId;
                const isSaving = bookmarkBtn.classList.contains('bookmark-btn');

                if (!isLoggedIn()) { redirectToLogin(); return; }

                const url = isSaving ? `/gigs/${gigId}/save/` : `/gigs/${gigId}/unsave/`;

                fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        bookmarkBtn.textContent = isSaving ? '★ Bookmarked' : '☆ Bookmark';
                        bookmarkBtn.classList.toggle('bookmark-btn');
                        bookmarkBtn.classList.toggle('bookmarked-btn');
                        bookmarkBtn.classList.toggle('btn-outline-light');
                        bookmarkBtn.classList.toggle('btn-light');
                        showStatusMessage('status-message', isSaving ? 'Gig saved!' : 'Removed from saved.', 'success');
                    } else {
                        showStatusMessage('status-message', data.error || 'Something went wrong', 'error');
                    }
                })
                .catch(() => showStatusMessage('status-message', 'Network error.', 'error'));
            }
        });
    }

    // ==========================================================================
    // 2. BAND/VENUE INTERACTION LOGIC (SEND INTEREST)
    // ==========================================================================
    const sendInterestBtn = document.getElementById('send-interest-btn');
    if (sendInterestBtn) {
        sendInterestBtn.addEventListener('click', function () {
            const musicianId = this.dataset.musicianId;
            const message = document.getElementById('interest-message').value.trim();

            if (!message) {
                alert("Please write a message first.");
                return;
            }

            fetch(`/musicians/${musicianId}/send-interest/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Requires Bootstrap JS to be loaded
                    const modalElement = document.getElementById('interestModal');
                    if(modalElement) {
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        modal.hide();
                    }
                    showStatusMessage('status-message', 'Message sent successfully!', 'success');
                } else {
                    alert(data.error);
                }
            })
            .catch(() => alert('Network error.'));
        });
    }

});

// ==========================================================================
// 3. GOOGLE MAPS INITIALIZATION (Must be globally accessible)
// ==========================================================================
function initMap() {
    const mapElements = document.querySelectorAll('.gig-mini-map');

    mapElements.forEach((mapDiv) => {
        const lat = parseFloat(mapDiv.getAttribute('data-lat'));
        const lng = parseFloat(mapDiv.getAttribute('data-lng'));
        const title = mapDiv.getAttribute('data-title');

        if (!isNaN(lat) && !isNaN(lng)) {
            const location = { lat: lat, lng: lng };
            const map = new google.maps.Map(mapDiv, {
                zoom: 14,
                center: location,
                disableDefaultUI: true 
            });
            new google.maps.Marker({ position: location, map: map, title: title });
        }
    });
}
window.initMap = initMap;