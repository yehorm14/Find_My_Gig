document.addEventListener('DOMContentLoaded', function () {

    let pendingMediaLinks = [];
    let linksToDelete = [];
    
    //Update Profile
    const updateProfileBtn = document.getElementById('update-profile-btn');

    if (updateProfileBtn){
        updateProfileBtn.addEventListener('click', function(){

            const username = document.getElementById('profile-username')?.value.trim();
            
            if (!username) {
                showStatusMessage('status-message', 'Username is required', 'error');
                return;
            }

            const firstname = document.getElementById('firstname')?.value.trim() || '';   // ADD
            const surname = document.getElementById('surname')?.value.trim() || ''; 
            const bandName = document.getElementById('band-name')?.value.trim() || '';
            const profileAbout = document.getElementById('profile-about')?.value.trim() || '';
            const profileAge = document.getElementById('profile-age')?.value || '';
            const profileInstruments = document.getElementById('profile-instruments')?.value || '';
            const profilePictureInput = document.getElementById('profile-picture-input');
            const hasPicture = profilePictureInput?.files[0];

            if (hasPicture){
                const formData = new FormData();
                formData.append('username', username);
                formData.append('firstname', firstname);
                formData.append('surname', surname);
                formData.append('band_name', bandName);
                formData.append('about', profileAbout);
                formData.append('age', profileAge);
                formData.append('instruments', profileInstruments);
                formData.append('profile_picture', profilePictureInput.files[0]);
                formData.append('media_links', JSON.stringify(pendingMediaLinks));
                formData.append('delete_media', JSON.stringify(linksToDelete));


                fetch('/dashboard/my-profile/update/',{
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: formData
                })
                .then(function(response){
                    return response.json();
                })
                .then(function(data){
                handleProfileUpdateResponse(data);
                })
                .catch(function (){
                    showStatusMessage('status-message', 'Profile updated successfully', 'success');
                    pendingMediaLinks = [];
                    linksToDelete = []
                });

            } else {
                const profileData = {
                    username: username,
                    firstname: firstname,   
                    surname: surname, 
                    band_name: bandName,
                    about: profileAbout,
                    age: profileAge,
                    instruments: profileInstruments,
                    media_links: pendingMediaLinks,
                    delete_media: linksToDelete

                };

                fetch('/dashboard/my-profile/update/',{
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(profileData)
                })
                .then(function (response){
                    return response.json();
                })
                .then(function(data){
                    handleProfileUpdateResponse(data);
                })
                .catch(function(){
                    showStatusMessage('status-message', 'Profile updated successfully', 'success');
                    pendingMediaLinks = [];
                    linksToDelete = [];
                });
            }
        });
    }

    //Profile Picture preview
    const profilePictureInput = document.getElementById('profile-picture-input');
    const profilePicturePreview = document.getElementById('profile-picture-preview');

    if (profilePictureInput && profilePicturePreview) {

        profilePictureInput.addEventListener('change', function () {

            const file = this.files[0];

            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    profilePicturePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    //Media Links
    const addMediaBtn = document.getElementById('add-media-btn');

    if (addMediaBtn){
        addMediaBtn.addEventListener('click', function (e) {
            e.preventDefault()
            e.stopPropagation()

            const mediaInput = document.getElementById('media-link-input');
            const mediaUrl = mediaInput?.value.trim();

            if (!mediaUrl) {
                showStatusMessage('status-message', 'Please enter a URL', 'error');
                return;
            }

            if (!isValidUrl(mediaUrl)) {
                showStatusMessage('status-message', 'Please enter a valid link e.g. https://youtube.com/...', 'error');
                return;
            }

            pendingMediaLinks.push(mediaUrl);

            addMediaLinkToList(mediaUrl, 'pending-' + pendingMediaLinks.length);

            mediaInput.value = '';

            showStatusMessage('status-message', 'Link added - press Update to save', 'success');
        });
    }

    //Delete media links
    const mediaList = document.getElementById('media-links-list');

    if (mediaList) {
        mediaList.addEventListener('click', function (e) {

            if (e.target.classList.contains('delete-media-btn')) {
                const mediaId = e.target.dataset.mediaId;
                const mediaItem = e.target.parentElement;

                if (String(mediaId).startsWith('pending-')){
                    const pendingIndex = parseInt(mediaId.replace('pending-', '')) - 1;
                    pendingMediaLinks.splice(pendingIndex, 1);
                    mediaItem.remove();
                    showStatusMessage('status-message', 'Link removed', 'success');
                    return;
                }

                linksToDelete.push(mediaId);
                mediaItem.remove();
                showStatusMessage('status-message', 'Link removed - press Update to save changes', 'success');
            }
        });
    }
    
    //delete account
    const deleteAccountBtn = document.getElementById('delete-account-btn');

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const confirmed = confirm('Are you sure you want to delete your account? This cannot be undone.');

            if (confirmed){
                fetch('/dashboard/my-profile/delete-account/', {
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
                        window.location.href = '/';
                    }
                })
                .catch(function(){
                    window.location.href = '/';
                });
            }
        });
    }

    //Withdraw application
    document.querySelectorAll('.withdraw-application-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {

            const gigId = this.dataset.gigId;
            const applicationCard = this.closest('.application-card');

            const confirmed = confirm('Are you sure you want to withdraw this application?');

            if (confirmed) {
                fetch(`/gigs/${gigId}/withdraw/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(function (response){
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        applicationCard.remove();
                        showStatusMessage('status-message', 'Application withdrawn', 'success');
                    }
                })
                .catch(function(){
                    applicationCard.remove();
                    showStatusMessage('status-message', 'Application withdrawn', 'success');
                });
            }
        });
    });

    //Create Gig Listing
    const createGigBtn = document.getElementById('create-gig-btn');
    
    if (createGigBtn) {
        createGigBtn.addEventListener('click', function () {
            const gigTitle = document.getElementById('listing-title')?.value?.trim();
            const gigPosition = document.getElementById('gig-position')?.value;
            const gigDate = document.getElementById('gig-date')?.value;
            const gigDescription = document.getElementById('gig-description')?.value?.trim();
            const gigLocation = document.getElementById('gig-location')?.value?.trim();

            if (!gigTitle) {
                showStatusMessage('status-message', 'Please enter a title for your listing', 'error');
                return;
            }

            if (!gigPosition) {
                showStatusMessage('status-message', 'Please select a position', 'error');
                return;
            }

            if (!gigDate) {
                showStatusMessage('status-message', 'Please select a date', 'error');
                return;
            }

            if (!gigDescription) {
                showStatusMessage('status-message', 'Please enter a description', 'error');
                return;
            }

            if (!gigLocation) {
                showStatusMessage('status-message', 'Please enter a location', 'error');
                return;
            }

            const gigData = {
                title: gigTitle,
                req_instruments: gigPosition,
                date: gigDate,
                description: gigDescription,
                location: gigLocation
            };

            fetch('/dashboard/my-listings/create/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gigData)
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    showStatusMessage('status-message', 'Gig listing created successfully', 'success');
                    window.location.href = '/dashboard/my-listings/';
                } else {
                    showStatusMessage('status-message', 'Something went wrong, try again', 'error');
                }
            })
        });
    }



    //Delete Listing
    const myListingsList = document.getElementById('my-listings-list');

    if (myListingsList) {
    myListingsList.addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-listing-btn')) {
            
            const listingId = e.target.dataset.listingId;
            const listingCard = e.target.closest('.listing-card');

            const confirmed = confirm('Are you sure you want to delete this listing?');

            if (confirmed) {
                fetch(`/dashboard/my-listings/${listingId}/delete/`, {
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
                        listingCard.remove();
                        showStatusMessage('status-message', 'Listing deleted', 'success');
                    }
                })
                .catch(function () {
                    listingCard.remove();
                    showStatusMessage('status-message', 'Listing deleted', 'success');
                });
            }
        }
    });
    }


    //Remove saved gig
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-saved-gig-btn')) {
        e.preventDefault();

        const btn = e.target;
        const gigId = btn.dataset.gigId;
        const savedGigCard = btn.closest('.listing-card'); 

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
                savedGigCard?.remove();
                showStatusMessage('status-message', 'Gig removed from saved', 'success');
            } else {
                showStatusMessage('status-message', 'Failed to remove bookmark', 'error');
            }
        })
        .catch(error => {
            console.error(error);
            showStatusMessage('status-message', 'Failed to remove bookmark', 'error');
        });
    }
});
});

//helper functions

function handleProfileUpdateResponse(data) {
    if (data.success) {
        showStatusMessage('status-message', 'Profile updated successfully', 'success');
        pendingMediaLinks = [];
        linksToDelete = [];

    } else if (data.error === 'username_taken') {
        showStatusMessage('status-message', 'That username is already taken, please choose another', 'error');
    
    } else {
        showStatusMessage('status-message', 'Something went wrong, try again', 'error');
    }
}

function isValidUrl(url){
    try{
        new URL(url);
        return true;
    } catch{
        return false;
    }
}

function addMediaLinkToList(url,mediaId){
    const mediaList = document.getElementById('media-links-list');

    if (mediaList) {
        const listItem = document.createElement('li');

        const link = document.createElement('a');
        link.href = url;
        link.textContent = url;
        link.target = '_blank';

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete File';
        deleteBtn.classList.add('delete-media-btn');
        deleteBtn.dataset.mediaId = mediaId;

        if (String(mediaId).startsWith('pending-')) {
            const pendingLabel = document.createElement('span');
            pendingLabel.textContent = ' (not saved yet)';
            pendingLabel.classList.add('pending-label');
            listItem.appendChild(link);
            listItem.appendChild(pendingLabel);
            listItem.appendChild(deleteBtn);
        } else {
            listItem.appendChild(link);
            listItem.appendChild(deleteBtn);
        }

        mediaList.appendChild(listItem);
    }
}

function clearCreateGigForm() {
    const fields = [
        'lisitng-title',
        'gig-description',
        'gig-location',
        'gig-date'
    ];
    fields.forEach(function (id) {
        const field = document.getElementById(id);
        if (field) field.value = '';
    });

    const positionField = document.getElementById('gig-position');
    if (positionField) positionField.selectedIndex = 0;
}

function addListingToPage(listing) {
    const listingsList = document.getElementById('my-listings-list');

    if (listingsList && listing) {
        const listingCard = document.createElement('div');
        listingCard.classList.add('listing-card');

        listingCard.innerHTML = `
            <div class="row align-items-center">
                <div class="col-md-4">
                    <h4 style="color: #fff; font-weight: 700;">${listing.title}</h4>
                    <p class="mb-1 text-muted-custom">🎸 Position: ${listing.req_instruments}</p>
                    <p class="mb-0 text-muted-custom">⏳ Date: ${listing.deadline}</p>
                </div>

                <div class="col-md-5">
                    <p class="description-text mb-1">${listing.description}</p>
                    <p class="gig-accent-text mb-0">📍 ${listing.location}</p>
                </div>

                <div class="col-md-3 d-flex flex-column align-items-end justify-content-center">
                    <button type="button"
                        class="delete-listing-btn btn btn-outline-danger rounded-pill w-100 my-2"
                        data-listing-id="${listing.id}">
                        Delete Listing
                    </button>
                </div>
            </div>
        `;

        listingsList.appendChild(listingCard);
    }
}





