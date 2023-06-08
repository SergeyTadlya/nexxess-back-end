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

const csrftoken = getCookie('csrftoken');

$(document).ready(function () {
    $("#cabinet__btn-edit").click(function() {
        $.ajax({
            type: 'POST',
            async: true,
            url: '/ajax_errors/',
            dataType:"json",
            data: JSON.stringify({}),
            headers: {
                "X-Requested_With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken,
            },
            success: (data) => {
                $("#first_name").val(data['first_name']);
                $("#last_name").val(data['last_name']);
                $("#phone").val(data['phone']);
                $("#bio").val(data['bio']);

                $("#country").val(data['country']);
                $("#city").val(data['city']);
                $("#street").val(data['street']);
                $("#tax_id").val(data['tax_id']);
            },
        });
    });
});
