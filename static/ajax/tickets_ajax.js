function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim(); // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken')

$(document).ready(function () {
    $("#search-btn").click(function() {
        let statuses_amount = document.getElementById('statuses_amount').value;
        var result = {};

        for (let i = 1; i < statuses_amount + 1; i++) {
            let status_name = document.getElementById(''.concat('status',i)).value;
            let status_value = document.getElementById(''.concat('status',i)).checked;
            result[status_name] = status_value;
        }

        result['from_date'] = document.getElementById('fromDatePicker').value;
        result['to_date'] = document.getElementById('toDatePicker').value;
        result['local_search'] = document.getElementById('search-input').value;
        result['showing_amount'] = document.getElementById('content__showing-number').textContent;

//        let elements = document.querySelectorAll('.content__titles-item');
//
//        for (let i = 0; i < elements.length; i++) {
//            if (elements[i].classList.contains('content__titles-small-to-big')){
//                result['ascending'] = document.getElementsByClassName('content__titles-small-to-big')[0].id;
//            }
//            else if (elements[i].classList.contains('content__titles-big-to-small')){
//                result['descending'] = document.getElementsByClassName('content__titles-big-to-small')[0].id;
//            }
//        }

        $.ajax({
            type: 'POST',
            async: true,
            url: 'ajax_filter/',
            dataType:"json",
            data: JSON.stringify(result),
            headers: {
                "X-Requested_With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken,
            },
            success: (data) => {
            console.log(data);
            },
        });
    });
});
