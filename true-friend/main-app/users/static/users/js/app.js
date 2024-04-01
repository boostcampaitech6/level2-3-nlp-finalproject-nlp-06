function previewImage() {
    var file = document.getElementById('id_profile_image').files[0];
    var reader = new FileReader();
    reader.onloadend = function() {
        document.getElementById('profile-image-preview').src = reader.result;
        document.getElementById('profile-image-preview').style.display = 'block';
    }
    if (file) {
        reader.readAsDataURL(file);
    } else {
        document.getElementById('profile-image-preview').src = "";
        document.getElementById('profile-image-preview').style.display = 'none';
    }
}


let notices = document.querySelectorAll('.notice');
notices.forEach((notice) => {
    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    let noticeId = notice.dataset.id;
    let deleteBtn = notice.querySelector('.delete-notice div');
    deleteBtn.addEventListener('click', function(event) {
        event.preventDefault();
        fetch(`http://${hostname}:8000/api/notices/${noticeId}/`, {
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
                if (response.status !== 201 || response.status !== 204) { // 204 No Content
                    return response.json();
                }
                return null; // Or any other handling for no-content responses
            })
            .then(data => {
                notice.remove();
                if (data) {
                    console.log(data.message); // Process your data here
                } else {
                    console.log('Notice deleted');
                }
            })
            .catch(error => console.error('There has been a problem with your fetch operation:', error));
    });
});


// document.getElementById('clear-collection').addEventListener('click', function() {
//     const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
//     fetch('/api/vectorstores/', {
//         method: 'DELETE',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrftoken,
//         },
//         credentials: 'same-origin',
//     })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             // Check if the response has content before parsing as JSON
//             if (response.status !== 204) { // 204 No Content
//                 return response.json();
//             }
//             return null; // Or any other handling for no-content responses
//         })
//         .then(data => {
//             if (data) {
//                 console.log(data.message); // Process your data here
//             } else {
//                 // Handle no-content response
//                 console.log('Collection cleared');
//             }
//         })
//         .catch(error => console.error('There has been a problem with your fetch operation:', error));
// });


