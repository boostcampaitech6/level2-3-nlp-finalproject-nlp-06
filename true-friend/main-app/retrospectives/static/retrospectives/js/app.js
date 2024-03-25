// 실험용 가상 데이터(지워야함)
retrospect_data = {
    data_20240324 : {
        'retrospectId':'d20240324',
        'userName': 'jaehyun',
        'text':'2024.03.24에 생성된 회고입니다.',
        'created_at':'2024/03/24',
        'luna':'Hello, World!',
        'checked':false,
    },

    data_20240323 : {
        'retrospectId':'d20240323',
        'userName': 'jaehyun',
        'text':'2024.03.23에 생성된 회고입니다.',
        'created_at':'2024/03/23',
        'luna':'Hello, World!',
        'checked':false,
    },

    data_20240322 : {
        'retrospectId':'d20240322',
        'userName': 'jaehyun',
        'text':'2024.03.22에 생성된 회고입니다.',
        'created_at':'2024/03/22',
        'luna':'Hello, World!',
        'checked':false,
    },

    data_20240321 : {
        'retrospectId':'d20240321',
        'userName': 'jaehyun',
        'text':'2024.03.21에 생성된 회고입니다.',
        'created_at':'2024/03/21',
        'luna':'Hello, World!',
        'checked':false,
    },
}

// ======================================================================

// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("notificationBox");

// Get the <span> element that closes the modal : (X)
var span = document.getElementsByClassName("close")[0];

// // Get the <span> element that closes the modal : (확인)
// var span_modal_btn = document.getElementsByClassName("modal_btn")[0];

// When the user clicks on the button, open the modal
btn.onclick = function(event) {
    var clickedElement = event.target; // 클릭한 요소 가져오기
    var postId = clickedElement.classList.item(0); // 클릭한 요소의 첫번째 클래스를 postId로 설정
    insertJSONIntoRETROSPECTMODAL(retrospect_data, postId); // 데이터 삽입 함수 호출
    modal.style.display = "block"; // 모달 표시
};

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// ================================================================

// Get the modal
var modal_notice = document.getElementById("notificationModal");

// Get the button that opens the modal
var btn_notice = document.getElementById("notificationButton");

// When the user clicks the button, open the modal 
btn_notice.onclick = function() {
    modal_notice.style.display = "block";
}

// When the user click the Windows, close the modal | modal_notice
window.addEventListener('click', function(event) {
    // modal_notice를 클릭한 경우
    if (event.target == modal_notice) {
        modal_notice.style.display = "none";
    }
    // modal_another를 클릭한 경우
    if (event.target == modal) {
        modal.style.display = "none";
    }
});

// JSON 데이터를 AlarmModalWindow에 넣는 함수
function insertJSONIntoALARM(data) {
    var containers = document.getElementsByClassName("alarm-container");
    for (var i = 0; i < containers.length; i++) {
        var container = containers[i];
        var html = ""; // 초기화
        for (var retrospect_date in data) {
            var item = data[retrospect_date];
            if (item.chcked!=false){
                html += "<a href=\"/retrospectives/?postId="+item.retrospectId+"\">"
                html += '<button class="p-4 bg-gray-200 rounded hover:bg-gray-300 focus:outline-none">' + item.text + "</button>";
                html += "</a>";
                item.chcked=true; // 로드한 json파일의 값이 변경되진 않음 : 어떻게 해야할까????
            }
        }
        container.innerHTML = html; // 새로운 HTML로 대체
    }
}


// 알림창타고 들어왔을 때 해당 회고가 뜨게 만드는 스크립트
window.onload = function() {
    var urlParams = new URLSearchParams(window.location.search);
    var postId = urlParams.get('postId');
    var modal = document.getElementById("myModal");

    if (postId) {
        
        var postElement = document.querySelector("." + postId);
        if (postElement) {
            insertJSONIntoRETROSPECTMODAL(retrospect_data, postId);
            modal.style.display = "block";
        }
    }
};
