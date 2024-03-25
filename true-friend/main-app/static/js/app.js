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

// modal.js

// Get the modal
var modal = document.getElementById("notificationModal");

// Get the button that opens the modal
var btn = document.getElementById("notificationButton");

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

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


// JSON 데이터를 토대로 회고록을 생성하는 함수
function insertJSONIntoRETROSPECTLIST(data) {
    var container = document.getElementById("notificationBox");
    var html = ""; // 초기화
    for (var retrospect_date in data) {
        var item = data[retrospect_date];
        html += "<div class=\"" + item.retrospectId + " border rounded-lg p-4 mb-4 bg-gray-50 hover:bg-blue-100\">";
        html += "<p class=\"" + item.retrospectId + " text-gray-700 mb-2\">" + item.created_at + " - 일간 회고" +"</p>";
        html += "</div>";
    }
    container.innerHTML = html; // 새로운 HTML로 대체
}


// JSON 데이터를 retrospect Modal에 넣는 함수
function insertJSONIntoRETROSPECTMODAL(data, postId) {
    var date_block = document.getElementById("date");
    var content_block = document.getElementById("content");
    var note_block = document.getElementById("note");
    
    // 모달창 요소들의 내용을 초기화
    date_block.textContent = "";
    content_block.textContent = "";
    note_block.textContent = "";

    for (var retrospect_date in data) {
        var item = data[retrospect_date];
        if (item.retrospectId == postId){
            date_block.textContent = item.created_at;
            content_block.textContent = item.text;
            note_block.textContent = item.luna;
        }
    }
}

