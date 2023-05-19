function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
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
            url: 'ajax_tasks_filter/',
            dataType:"json",
            data: JSON.stringify(result),
            headers: {
                "X-Requested_With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken,
            },
            success: (data) => {
                console.log(data);

                var html_tasks = '';
                var html_showing_tasks = '';
                var html_pagination = '';

                for (task in data['tasks'][0]) {
                    if (data['tasks'][0][task].more_one) {
                        html_tasks += `
                            <div class="content__body">
                              <p class="content__body-titleDate">` + data['tasks'][0][task].created_at + `</p>`
                    }
                    html_tasks += `
                          <ul class="content__body-list">
                              <li class="content__body-box">
                                  <ul class="content__body-titles">
                                      <li class="content__titles-item">ID</li>
                                      <li class="content__titles-item">Title</li>
                                      <li class="content__titles-item">Created date</li>
                                      <li class="content__titles-item">Due date</li>
                                      <li class="content__titles-item">Status</li>
                                  </ul>
                                  <ul class="content__body-items">
                                      <li class="content__body-item style--width">
                                          <a href="detail/` + data['tasks'][0][task].id + `/">
                                              <p class="content__body-name">` + data['tasks'][0][task].id + `</p>
                                          </a>
                                      </li>
                                      <li class="content__body-item style--width">
                                        <a class="content__body-link" href="detail/` + data['tasks'][0][task].id + `/">
                                            <p class="content__body-name">` + data['tasks'][0][task].title + `</p>
                                        </a>
                                      </li>
                                      <li class="content__body-item style--width">
                                        <a class="content__body-link" href="detail/` + data['tasks'][0][task].id + `/">
                                            <p class="content__body-date">` + data['tasks'][0][task].created_at + `</p>
                                        </a>
                                      </li>
                                      <li class="content__body-item style--width">
                                          <a class="content__body-link" href="detail/` + data['tasks'][0][task].id + `/">
                                              <p class="content__body-date">` + data['tasks'][0][task].deadline + `</p>
                                          </a>
                                      </li>
                                      <li class="content__body-item style--width">
                                          <a class="content__body-link" href="detail/` + data['tasks'][0][task].id + `/">
                                              <p class="content__body-status style--width font--` + data['tasks'][0][task].status_color + `">` + data['tasks'][0][task].status_name + `</p>
                                          </a>
                                      </li>
                                  </ul>
                                  <div class="content__body-messages">
                                      <p>1</p>
                                      <img src="/static/images/mail.svg" alt="print">
                                  </div>
                                  <button class="content__body-btn">
                                      <img class="content__body-img" src="/static/images/chevron.svg" alt="arrow">
                                  </button>
                              </li>
                          </ul>`
                    if (data['tasks'][0][task].more_one) {
                        html_tasks += `</div>`
                    }
                }

                html_showing_tasks += `
                    <p class="content__showing-text">Showing</p>
                    <p id="content__showing-number" class="content__showing-number">10</p>
                    <img class="content__showing-img" src="/static/images/invoices/arrow-drop-down.svg" alt="icon">
                    <p class="content__showing-numbers">` + data.tasks_number + `</p>
                    <ul id="content__showing-list" class="content__showing-list">
                      <li class="content__showing-item">10</li>
                      <li class="content__showing-item">50</li>
                      <li class="content__showing-item">100</li>
                      <li class="content__showing-item">All</li>
                    </ul>`

                    html_pagination += `<div class="content__pagination">`
                    if (data['has_other_pages']) {
                        if (data['has_previous']) {
                            html_pagination += `<a id="prev" class="content__pagination-arrow" href="?page=` + (data['previous_page']) + `">
                              <svg width="46" height="46" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" d="M14.021 6.912a.69.69 0 0 1 0 .976L9.91 12l4.112 4.112a.69.69 0 0 1-.976.976l-4.6-4.6a.69.69 0 0 1 0-.976l4.6-4.6a.69.69 0 0 1 .976 0Z" clip-rule="evenodd"></path>
                              </svg>
                            </a>`
                        } else {
                            html_pagination += `<a id="prev" class="content__pagination-arrow" href="" style="pointer-events: none">
                              <svg width="46" height="46" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" d="M14.021 6.912a.69.69 0 0 1 0 .976L9.91 12l4.112 4.112a.69.69 0 0 1-.976.976l-4.6-4.6a.69.69 0 0 1 0-.976l4.6-4.6a.69.69 0 0 1 .976 0Z" clip-rule="evenodd"></path>
                              </svg>
                            </a>`
                        }

                        html_pagination += `<div class="content__pagination-buttons">`
                            if (data['has_other_pages']) {
                                for (page in data['page_range']) {
                                    if (data['tasks'].number == page) {
                                        html_pagination += `<span class="content__pagination-button pagination--active">` + data['page_range'][page] + `</span>`
                                    } else {
                                        html_pagination += `<a class="content__pagination-button" href="?page=` + data['page_range'][page] + `" >` + data['page_range'][page] + `</a>`
                                    }
                                }
                            }
                        html_pagination += `</div>`

                        if (data['has_next']) {
                            html_pagination += `
                            <a id="next" class="content__pagination-arrow" href="?page=` + data['next_page'] + `">
                              <svg width="46" height="46" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" d="M9.979 6.912a.69.69 0 0 1 .976 0l4.6 4.6a.69.69 0 0 1 0 .976l-4.6 4.6a.69.69 0 1 1-.976-.976L14.091 12 9.98 7.888a.69.69 0 0 1 0-.976Z" clip-rule="evenodd"></path>
                              </svg>
                            </a>`
                        } else {
                            html_pagination += `
                            <a id="next" class="content__pagination-arrow" href="" style="pointer-events: none">
                              <svg width="46" height="46" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" d="M9.979 6.912a.69.69 0 0 1 .976 0l4.6 4.6a.69.69 0 0 1 0 .976l-4.6 4.6a.69.69 0 1 1-.976-.976L14.091 12 9.98 7.888a.69.69 0 0 1 0-.976Z" clip-rule="evenodd"></path>
                              </svg>
                            </a>`
                        }
                    }
                    html_pagination += `</div>`

                $('#tasks_pagination').html(html_pagination);
                $('#content__showing-box').html(html_showing_tasks);
                $("#div-tasks").html(html_tasks);
            },
        });
    });
});
