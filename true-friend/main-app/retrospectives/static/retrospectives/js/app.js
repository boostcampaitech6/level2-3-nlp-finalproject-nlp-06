document.addEventListener('DOMContentLoaded', (event) => {
    // When the DOM is fully loaded
    const retrospectiveModal = document.getElementById("retrospective-modal");
    const retrospectiveModalDate = retrospectiveModal.querySelector("#retrospective-modal-date");
    const retrospectiveModalText = retrospectiveModal.querySelector("#retrospective-modal-text");
    const retrospectiveModalComment = retrospectiveModal.querySelector("#retrospective-modal-comment");
    const modalClose = retrospectiveModal.querySelector(".modal-close");

    let retrospectives = document.querySelectorAll('.retrospective');
    retrospectives.forEach(retrospective => {
        retrospective.addEventListener('click', function(event) {
            event.preventDefault();
            retrospectiveModalDate.innerHTML = retrospective.dataset.date;
            retrospectiveModalText.innerHTML = retrospective.dataset.text;
            retrospectiveModalComment.innerHTML = retrospective.dataset.comment;
            retrospectiveModal.classList.add('active');
        });
    }); 

    window.addEventListener('click', function(event) {
        if (event.target === retrospectiveModal) {
            retrospectiveModal.classList.remove('active');
            retrospectiveModalDate.innerHTML = "";
            retrospectiveModalText.innerHTML = "";
            retrospectiveModalComment.innerHTML = "";
        }
    });

    modalClose.addEventListener('click', function(event) {
        if (event.target === retrospectiveModal) {
            retrospectiveModal.classList.remove('active');
            retrospectiveModalDate.innerHTML = "";
            retrospectiveModalText.innerHTML = "";
            retrospectiveModalComment.innerHTML = "";
        }
    });

});