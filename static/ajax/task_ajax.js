$(document).ready(function () {


    $('#content__form input[type=text]').val('');
    $('#content__form textarea').val('');


    $('#create-task-form').submit(function (event) {
        event.preventDefault();
        var taskName = $('#task-name').val();
        var taskDescription = $('#task-description').val();
        var taskDeadline = $('#contentFormDatePicker').val();
        $.ajax({
            url: '/tickets/',
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            data: {
                task_name: taskName,
                task_description: taskDescription,
                task_deadline: taskDeadline
            },
            success: function (response) {
                console.log(response);
                alert(response.message);
            },
            error: function (error) {
                console.log(error);
                alert('Failed to create task.');
            }
        });
    });
});
