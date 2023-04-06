//<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
//<script>
//$(document).ready(function() {
//    $('#login-form').submit(function(event) {
//        event.preventDefault(); // prevent default form submit
//        $.ajax({
//            url: "{% url 'account_login' %}", // your login view URL
//            type: "POST",
//            data: $('#login-form').serialize(), // serialize form data
//            success: function(response) {
//                if (response.success) {
//                    alert("Login successful");
//                    location.reload(); // reload page on successful login
//                } else {
//                    // login failed, display error message
//                    $('.alert-danger').remove();
//                    $('#login-form').before('<div class="alert alert-danger">' + response.error_message + '</div>');
//                }
//            },
//            error: function(xhr, status, error) {
//                // display error message
//                $('.alert-danger').remove();
//                $('#login-form').before('<div class="alert alert-danger">' + error + '</div>');
//            }
//        });
//    });
//});
//</script>


$(document).ready(function() {
    $('#authentication__login-button').click(function(event) {
        event.preventDefault();
        $.ajax({
            url: $('#authentication__login').attr('action'),
            type: 'POST',
            data: $('#authentication__login').serialize(),
            success: function(response) {
                window.location.href = response.redirect_url;
            },
            error: function(xhr, status, error) {
                $('.authentication__box-input').val('');
                $('.authentication__box-input').addClass('invalid');
            }
        });
    });
});
