document.addEventListener('DOMContentLoaded', (event) => {
    // When the DOM is fully loaded
    const noticeModal = document.getElementById("notice-modal");
    const noticeContainer = noticeModal.querySelector(".notice-container");
    const noticeModalTrigger = document.getElementById("notice-modal-trigger");

    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    fetch(`http://${hostname}:8000/api/${username}/notices/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        credentials: 'same-origin',
    })
        .then(response => response.json())
        .then(data => {
            data = data.slice(0, 10);
            data.forEach(notice => {
                // const date = new Date(notice.created_at);
                const date = notice.created;
                const formattedDate = date.replace(/-/g, '/').substring(0, 10) + ' ' + date.substring(11, 16);
                const noticeItem = document.createElement('div');
                noticeItem.classList.add('notice');
                noticeItem.dataset.id = notice.id;
                
                noticeItem.innerHTML = `
                <div class="notice-title">${formattedDate}</div>
                <div class="notice-text">${notice.text}</div>
                `

                if (notice.is_read) {
                    noticeItem.classList.add('read');
                } else {
                    noticeItem.addEventListener('click', function(event) {
                        event.preventDefault();
                        console.log(`Notice ID: ${notice.id} has been clicked!`);
                        fetch(`http://${hostname}/api/notices/${notice.id}/`, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken,
                            },
                            credentials: 'same-origin',
                        })
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Network response was not ok');
                                }
                                // Check if the response has content before parsing as JSON
                                if (response.status !== 201 || response.status != 204) { // 204 No Content
                                    return response.json();
                                }
                                return null; // Or any other handling for no-content responses
                            })
                            .then(data => {
                                noticeItem.classList.add('read');
                            })
                            .catch(error => console.error('There has been a problem with your fetch operation:', error));
                    });
                }
                noticeContainer.appendChild(noticeItem);
            });
        });

    noticeModalTrigger.addEventListener('click', function(event) {
        event.preventDefault();
        noticeModal.classList.add('active');
    });

    window.addEventListener('click', function(event) {
        if (event.target === noticeModal) {
            noticeModal.classList.remove('active');
        }
    });

});
