document.addEventListener('DOMContentLoaded', function () {

    // ==========================================================================
    // 1. GIG LIST PAGE LOGIC (APPLY / BOOKMARK)
    // ==========================================================================
    const gigsList = document.getElementById('gigs-list');

    if (gigsList) {
        gigsList.addEventListener('click', function (e) {
            
            // --- Apply to a Gig ---
            if (e.target.classList.contains('apply-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;

                if (!isLoggedIn()) { redirectToLogin(); return; }

                fetch(`/gigs/${gigId}/apply/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        btn.textContent = 'Withdraw';
                        btn.classList.remove('apply-btn');
                        btn.classList.add('withdraw-btn');
                        showStatusMessage('status-message', 'Application submitted', 'success');
                    } else if (data.error === 'already_applied') {
                        showStatusMessage('status-message', 'You have already applied for this gig', 'error');
                    } else {
                        showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                    }
                })
                .catch(() => showStatusMessage('status-message', 'Network error.', 'error'));
            }

            // --- Withdraw Application ---
            if (e.target.classList.contains('withdraw-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;

                if (confirm('Are you sure you want to withdraw your application?')) {
                    fetch(`/gigs/${gigId}/withdraw/`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            btn.textContent = 'Apply';
                            btn.classList.remove('withdraw-btn');
                            btn.classList.add('apply-btn');
                            showStatusMessage('status-message', 'Application withdrawn', 'success');
                        } else {
                            showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                        }
                    })
                    .catch(() => showStatusMessage('status-message', 'Network Error', 'error'));
                }
            }

            // --- Bookmark Toggle (Save/Unsave Gig) ---
            if (e.target.classList.contains('bookmark-btn') || e.target.classList.contains('bookmarked-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;
                const isSaving = btn.classList.contains('bookmark-btn');

                if (!isLoggedIn()) { redirectToLogin(); return; }

                const url = isSaving ? `/gigs/${gigId}/save/` : `/gigs/${gigId}/unsave/`;

                fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        btn.textContent = isSaving ? '★ Bookmarked' : '★ Bookmark';
                        btn.classList.toggle('bookmark-btn');
                        btn.classList.toggle('bookmarked-btn');
                        showStatusMessage('status-message', isSaving ? 'Gig saved' : 'Removed from saved', 'success');
                    } else {
                        showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                    }
                })
                .catch(() => showStatusMessage('status-message', 'Network error.', 'error'));
            }
        });
    }

    // ==========================================================================
    // 2. SINGLE GIG DETAIL PAGE LOGIC
    // ==========================================================================
    
    // Single Gig: Apply/Withdraw
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
                    showStatusMessage('gig-detail-status', isApplied ? 'Application withdrawn' : 'Application submitted', 'success');
                } else if (data.error === 'already_applied') {
                    showStatusMessage('gig-detail-status', 'You have already applied for this gig', 'error');
                } else {
                    showStatusMessage('gig-detail-status', 'Something went wrong, try again', 'error');
                }
            })
            .catch(() => showStatusMessage('gig-detail-status', 'Network Error', 'error'));
        });
    }
    
    // Single Gig: Bookmark
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
                    btn.textContent = isBookmarked ? '★ Bookmark' : '★ Bookmarked';
                    btn.dataset.bookmarked = isBookmarked ? 'false' : 'true';
                    btn.classList.toggle('bookmark-btn');
                    btn.classList.toggle('bookmarked-btn');
                    showStatusMessage('gig-detail-status', isBookmarked ? 'Gig removed from saved' : 'Gig saved', 'success');
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
            const url = isBookmarked ? `/gigs/bands/${bandId}/unsave/` : `/gigs/bands/${bandId}/save/`;

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
    
    // Scout Musician Toggle
    const scoutMusicianBtn = document.getElementById('scout-musician-btn');
    if (scoutMusicianBtn) {
        scoutMusicianBtn.addEventListener('click', function () {
            if (!isLoggedIn()) { redirectToLogin(); return; }

            const id = this.dataset.musicianId;
            const isScouted = this.dataset.scouted === 'true';
            const url = isScouted ? `/gigs/musicians/${id}/unsave/` : `/gigs/musicians/${id}/save/`;

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

    // Confirm Invitation from Modal
    const confirmInviteBtn = document.getElementById('confirm-invite-btn');
    if (confirmInviteBtn) {
        confirmInviteBtn.addEventListener('click', function () {
            const musicianId = this.dataset.musicianId;
            const gigSelect = document.getElementById('invite-gig-select');
            if (!gigSelect) return;
            const listingId = gigSelect.value;

            fetch(`/gigs/musicians/${musicianId}/invite/`, {
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