document.addEventListener('DOMContentLoaded', function () {

    // ==========================================================================
    // 1. GIG LIST PAGE LOGIC (APPLY / BOOKMARK)
    // ==========================================================================
    const gigsList = document.getElementById('gigs-list');

    if (gigsList) {
        gigsList.addEventListener('click', function (e) {
            
            // --- Apply / Withdraw ---
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

            // --- Bookmark / Unbookmark ---
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
                        // Toggle the logic classes
                        bookmarkBtn.classList.toggle('bookmark-btn');
                        bookmarkBtn.classList.toggle('bookmarked-btn');
                        // Toggle the visual CSS colors!
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
                    btn.textContent = isApplied ? 'Apply' : 'Withdraw';
                    btn.dataset.applied = isApplied ? 'false' : 'true';
                    btn.classList.toggle('btn-primary');
                    btn.classList.toggle('btn-danger');
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
                    btn.textContent = isBookmarked ? '☆ Bookmark' : '★ Bookmarked';
                    btn.dataset.bookmarked = isBookmarked ? 'false' : 'true';
                    btn.classList.toggle('bookmark-btn');
                    btn.classList.toggle('bookmarked-btn');
                    btn.classList.toggle('btn-outline-light');
                    btn.classList.toggle('btn-light');
                    showStatusMessage('gig-detail-status', isBookmarked ? 'Gig removed from saved.' : 'Gig saved!', 'success');
                } else {
                    showStatusMessage('gig-detail-status', 'Something went wrong, try again', 'error');
                }
            })
            .catch(() => showStatusMessage('gig-detail-status', 'Network Error', 'error'));
        });
    }

    // ==========================================================================
    // 3. BAND DETAIL PAGE LOGIC (Musicians Saving Bands)
    // ==========================================================================
    const saveBandBtn = document.getElementById('save-band-btn');
    if (saveBandBtn) {
        saveBandBtn.addEventListener('click', function () {
            if (!isLoggedIn()) { redirectToLogin(); return; }

            const bandId = this.dataset.bandId;
            const isBookmarked = this.dataset.bookmarked === 'true';
            const btn = this;
            const url = isBookmarked ? `/bands/${bandId}/unsave/` : `/bands/${bandId}/save/`;

            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    btn.textContent = isBookmarked ? '☆ Save Band' : '★ Saved to Favorites';
                    btn.dataset.bookmarked = isBookmarked ? 'false' : 'true';
                    btn.classList.toggle('btn-outline-light');
                    btn.classList.toggle('apply-btn');
                    showStatusMessage('status-message', isBookmarked ? 'Band removed from favorites' : 'Band saved to favorites!', 'success');
                } else {
                    showStatusMessage('status-message', data.error || 'Something went wrong', 'error');
                }
            })
            .catch(() => showStatusMessage('status-message', 'Network error. Try again.', 'error'));
        });
    }

    // ==========================================================================
    // 4. MUSICIAN DETAIL PAGE LOGIC (Bands Scouting & Inviting)
    // ==========================================================================
    const scoutMusicianBtn = document.getElementById('scout-musician-btn');
    if (scoutMusicianBtn) {
        scoutMusicianBtn.addEventListener('click', function () {
            if (!isLoggedIn()) { redirectToLogin(); return; }

            const id = this.dataset.musicianId;
            const isScouted = this.dataset.scouted === 'true';
            const url = isScouted ? `/musicians/${id}/unsave/` : `/musicians/${id}/save/`;

            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.textContent = isScouted ? '☆ Scout Musician' : '★ On Your Roster';
                    this.dataset.scouted = isScouted ? 'false' : 'true';
                    this.classList.toggle('btn-outline-light');
                    this.classList.toggle('apply-btn');
                    showStatusMessage('status-message', isScouted ? 'Removed from roster' : 'Added to roster!', 'success');
                }
            });
        });
    }

    const confirmInviteBtn = document.getElementById('confirm-invite-btn');
    if (confirmInviteBtn) {
        confirmInviteBtn.addEventListener('click', function () {
            const musicianId = this.dataset.musicianId;
            const gigSelect = document.getElementById('invite-gig-select');
            if (!gigSelect) return;
            const listingId = gigSelect.value;

            fetch(`/musicians/${musicianId}/invite/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
                body: JSON.stringify({ listing_id: listingId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showStatusMessage('status-message', 'Invitation sent successfully!', 'success');
                    const modalEl = document.getElementById('inviteModal');
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                } else {
                    showStatusMessage('status-message', data.error || 'Failed to send invite.', 'error');
                }
            })
            .catch(() => showStatusMessage('status-message', 'Network error.', 'error'));
        });
    }

});

// ==========================================================================
// 5. GOOGLE MAPS LOGIC 
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