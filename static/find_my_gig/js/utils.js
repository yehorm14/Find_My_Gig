function getCookie(name){
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');

        cookies.forEach(function (cookie){
            const trimmed = cookie.trim();

            if (trimmed.startsWith(name + '=')){
                cookieValue = decodeURIComponent(
                    trimmed.slice(name.length + 1)
                );
            }

        });
    }
    return cookieValue;
}

function showStatusMessage(elementId,message,type){
    const messageDiv = document.getElementById(elementId);

    if (messageDiv){
        messageDiv.textContent = message;

        messageDiv.className = 'status-' + type;

        messageDiv.style.display = 'block';

        setTimeout(function (){
            messageDiv.style.display = 'none';
            messageDiv.textContent = '';
        }, 3000);


    }
}

function isLoggedIn() {
    return document.body.classList.contains('user-logged-in');
}

function redirectToLogin() {
    const currentPage = window.location.pathname;
    window.location.href = '/login/?next=' + currentPage;
}

function formatDate(dateString) {
    const date = new Date(dateString);

    const options = {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    };

    return date.toLocaleDateString('en-GB', options);
}