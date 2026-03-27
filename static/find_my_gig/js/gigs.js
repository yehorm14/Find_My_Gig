document.addEventListener('DOMContentLoaded', function () {

    // ==========================================================================
    // 1. GIG LIST PAGE LOGIC (APPLY / BOOKMARK via Event Delegation)
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
                        
                        // Find the review button inside this specific gig's card
                        const listingCard = applyBtn.closest('.listing-card') || applyBtn.closest('.card');
                        if (listingCard) {
                            const reviewBtn = listingCard.querySelector('.review-btn');
                            if (reviewBtn) {
                                if (isApplying) {
                                    reviewBtn.classList.remove('d-none'); // Unhide on Apply
                                } else {
                                    reviewBtn.classList.add('d-none');    // Hide on Withdraw
                                }
                            }
                        }
                        // --------------------------------------------

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
    // 2. SINGLE GIG DETAIL PAGE LOGIC 
    // ==========================================================================
    const gigDetailApplyBtn = document.getElementById('gig-detail-apply-btn');
    if (gigDetailApplyBtn) {
        gigDetailApplyBtn.addEventListener('click', function () {
            if (!isLoggedIn()) { redirectToLogin(); return; }

            const gigId = this.dataset.gigId;
            const isApplied = this.dataset.applied === 'true';
            const btn = this;
            const url = isApplied ? `/gigs/${gigId}/withdraw/` : `/gigs/${gigId}/apply/`;

            if (isApplied && !confirm('Are you sure you want to withdraw your application?')) return;

            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    btn.dataset.applied = isApplied ? 'false' : 'true';
                    btn.textContent = isApplied ? 'Apply Now' : 'Withdraw Application';
                    btn.className = isApplied ? 'btn apply-btn rounded-pill px-4 py-2' : 'btn withdraw-btn rounded-pill px-4 py-2';
                    
                    const reviewBtn = document.getElementById('gig-detail-review-btn');
                    if (reviewBtn) {
                        if (isApplied) {
                            reviewBtn.classList.add('d-none');    // Hide on Withdraw
                        } else {
                            reviewBtn.classList.remove('d-none'); // Unhide on Apply
                        }
                    }
                    // --------------------------------------------

                    showStatusMessage('gig-detail-status', isApplied ? 'Application withdrawn.' : 'Application submitted!', 'success');
                } else {
                    showStatusMessage('gig-detail-status', data.error || 'Something went wrong', 'error');
                }
            })
            .catch(() => showStatusMessage('gig-detail-status', 'Network Error', 'error'));
        });
    }
    
    const gigDetailBookmarkBtn = document.getElementById('gig-detail-bookmark-btn');
    if (gigDetailBookmarkBtn) {
        gigDetailBookmarkBtn.addEventListener('click', function () {
            if (!isLoggedIn()) { redirectToLogin(); return; }

            const gigId = this.dataset.gigId;
            const isBookmarked = this.dataset.bookmarked === 'true';
            const btn = this;
            const url = isBookmarked ? `/gigs/${gigId}/unsave/` : `/gigs/${gigId}/save/`;

            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    btn.dataset.bookmarked = isBookmarked ? 'false' : 'true';
                    btn.textContent = isBookmarked ? '☆ Bookmark' : '★ Bookmarked';
                    showStatusMessage('gig-detail-status', isBookmarked ? 'Gig removed from saved.' : 'Gig saved!', 'success');
                } else {
                    showStatusMessage('gig-detail-status', 'Something went wrong, try again', 'error');
                }
            })
            .catch(() => showStatusMessage('gig-detail-status', 'Network Error', 'error'));
        });
    }

    // ==========================================================================
    // 3. BAND/VENUE INTERACTION LOGIC (SEND INTEREST)
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
// 4. GOOGLE MAPS INITIALIZATION (Must be globally accessible)
// ==========================================================================
function initMap() {
    const mapElements = document.querySelectorAll('.gig-mini-map, .gig-map-large');

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