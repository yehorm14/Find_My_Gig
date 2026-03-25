document.addEventListener('DOMContentLoaded', function () {

    //APPLY / WITHDRAW BUTTON
    const gigsList = document.getElementById('gigs-list');

    if (gigsList) {
        gigsList.addEventListener('click', function (e) {
            //apply
            if (e.target.classList.contains('apply-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;

                if (!isLoggedIn()) {
                    redirectToLogin();
                    return;
                }

                fetch(`/gigs/${gigId}/apply/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
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
                .catch(function () {
                    btn.textContent = 'Withdraw';
                    btn.classList.remove('apply-btn');
                    btn.classList.add('withdraw-btn');
                    showStatusMessage('status-message', 'Application submitted', 'success');
                });
            }

            //Withdraw Button
            if (e.target.classList.contains('withdraw-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;

                const confirmed = confirm('Are you sure you want to withdraw your application?');

                if (confirmed) {
                    fetch(`/gigs/${gigId}/withdraw/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        if (data.success) {
                            btn.textContent = 'Apply';
                            btn.classList.remove('withdraw-btn');
                            btn.classList.add('apply-btn');
                            showStatusMessage('status-message', 'Application withdrawn', 'success');
                        } else {
                            showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                        }
                    })
                    .catch(function () {
                        btn.textContent = 'Apply';
                        btn.classList.remove('withdraw-btn');
                        btn.classList.add('apply-btn');
                        showStatusMessage('status-message', 'Application withdrawn', 'success');
                    });
                }
            }

            //Bookmark Button
            if (e.target.classList.contains('bookmark-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;

                if (!isLoggedIn()) {
                    redirectToLogin();
                    return;
                }

                fetch(`/gigs/${gigId}/save/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        btn.textContent = '★ Bookmarked';
                        btn.classList.remove('bookmark-btn');
                        btn.classList.add('bookmarked-btn');
                        showStatusMessage('status-message', 'Gig saved', 'success');
                    } else {
                        showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                    }
                });
            }

            // Bookmarked Button (saved → unsaved)
            if (e.target.classList.contains('bookmarked-btn')) {
                const btn = e.target;
                const gigId = btn.dataset.gigId;

                fetch(`/gigs/${gigId}/unsave/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        btn.textContent = '★ Bookmark';
                        btn.classList.remove('bookmarked-btn');
                        btn.classList.add('bookmark-btn');
                        showStatusMessage('status-message', 'Gig removed from saved', 'success');
                    } else {
                        showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                    }
                });
            }
        });
    }

    //Single Gig detail page
    const gigDetailApplyBtn = document.getElementById('gig-detail-apply-btn');

    if (gigDetailApplyBtn) {
        gigDetailApplyBtn.addEventListener('click', function () {

            if (!isLoggedIn()) {
                redirectToLogin();
                return;
            }

            const gigId = this.dataset.gigId;
            const isApplied = this.dataset.applied === 'true';
            const btn = this;

            const url = isApplied ? `/gigs/${gigId}/withdraw/` : `/gigs/${gigId}/apply/`;

            if (isApplied) {
                const confirmed = confirm('Are you sure you want to withdraw your application?');
                if (!confirmed) return;
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    if (isApplied) {
                        btn.textContent = 'Apply';
                        btn.dataset.applied = 'false';
                        showStatusMessage('gig-detail-status', 'Application withdrawn', 'success');
                    } else {
                        btn.textContent = 'Withdraw';
                        btn.dataset.applied = 'true';
                        showStatusMessage('gig-detail-status', 'Application submitted', 'success');
                    }
                } else if (data.error === 'already_applied') {
                    showStatusMessage('gig-detail-status', 'You have already applied for this gig', 'error');
                } else {
                    showStatusMessage('gig-detail-status', 'Something went wrong, try again', 'error');
                }
            })
            .catch(function () {
                if (isApplied) {
                    btn.textContent = 'Apply';
                    btn.dataset.applied = 'false';
                    showStatusMessage('gig-detail-status', 'Application withdrawn', 'success');
                } else {
                    btn.textContent = 'Withdraw';
                    btn.dataset.applied = 'true';
                    showStatusMessage('gig-detail-status', 'Application submitted', 'success');
                }
            });
        })
    }});
    

    const gigDetailBookmarkBtn = document.getElementById('gig-detail-bookmark-btn');

    if (gigDetailBookmarkBtn) {
        gigDetailBookmarkBtn.addEventListener('click', function () {

            if (!isLoggedIn()) {
                redirectToLogin();
                return;
            }

            const gigId = this.dataset.gigId;
            const isBookmarked = this.dataset.bookmarked === 'true';
            const btn = this;
            const url = isBookmarked ? `/gigs/${gigId}/unsave/` : `/gigs/${gigId}/save/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (isBookmarked) {
                        btn.textContent = '★ Bookmark';
                        btn.classList.remove('bookmarked-btn');
                        btn.classList.add('bookmark-btn');
                        showStatusMessage('gig-detail-status', 'Gig removed from saved', 'success');
                    } else {
                        btn.textContent = '★ Bookmarked';
                        btn.dataset.bookmarked = 'true';
                        btn.classList.remove('bookmark-btn');
                        btn.classList.add('bookmarked-btn');
                        showStatusMessage('gig-detail-status', 'Gig saved', 'success');
                    }
                } else {
                    showStatusMessage('gig-detail-status', 'Something went wrong, try again', 'error');
                }
            })
            .catch(() => {
                if (isBookmarked) {
                    btn.textContent = '★ Bookmark';
                    btn.dataset.bookmarked = 'false';
                    btn.classList.remove('bookmarked-btn');
                    btn.classList.add('bookmark-btn')
                } else {
                    btn.textContent = 'Bookmarked';
                    btn.dataset.bookmarked = 'true';
                    btn.classList.remove('bookmark-btn');
                    btn.classList.add('bookmarked-btn');
                }
            });
        });
    }


//Helper

function updateGigsList(gigs) {
    const gigsList = document.getElementById('gigs-list');

    if (gigsList) {
        gigsList.innerHTML = '';

        if (gigs.length === 0) {
            gigsList.innerHTML = '<p>No gigs found matching your filters</p>';
            return;
        }

        gigs.forEach(function (gig) {
            const gigCard = document.createElement('div');
            gigCard.classList.add('gig-card');

            gigCard.innerHTML = `
                <h3>${gig.title}</h3>
                <p>Posted by: ${gig.band_name}</p>
                <p>Position: ${gig.req_instruments}</p>
                <p>Date: ${formatDate(gig.deadline)}</p>
                <p>Location: ${gig.location}</p>
                <button class="apply-btn" data-gig-id="${gig.id}">Apply</button>
                <button class="bookmark-btn" data-gig-id="${gig.id}">Bookmark</button>
            `;

            gigsList.appendChild(gigCard);
        });
    }
}


// ==========================================
//             GOOGLE MAPS LOGIC 
// ==========================================
function initMap() {
    const mapElements = document.querySelectorAll('.gig-mini-map');

    mapElements.forEach((mapDiv) => {
        const lat = parseFloat(mapDiv.getAttribute('data-lat'));
        const lng = parseFloat(mapDiv.getAttribute('data-lng'));
        const title = mapDiv.getAttribute('data-title');

        const location = { lat: lat, lng: lng };

        const map = new google.maps.Map(mapDiv, {
            zoom: 14,
            center: location,
            disableDefaultUI: true 
        });

        new google.maps.Marker({ position: location, map: map, title: title });
    });
}

window.initMap = initMap;