const url = window.location.href;

var ticketUrl = url.slice(0, url.indexOf('/', url.indexOf('/') + 2) + 1);

const searchInput = document.getElementById('search-input')

const resultsBox = document.getElementById('results_box')

const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

const sendSearchData = (input_value) => {
    $.ajax({
        type: 'POST',
        url: 'search/ticket/',
        data: {
            'csrfmiddlewaretoken': csrf,
            'input_value': input_value,
        },
        success: (response) => {
            console.log(response.data)
            const data = response.data
            if (Array.isArray(data)) {
                resultsBox.innerHTML = ""
                data.forEach(input_value=> {
                    resultsBox.innerHTML += `
                        <a href="${ticketUrl}search/ticket/${input_value.Ticket.pk}" class="item">
                            <div class="row mt-2 mb-2">
                                <div class="col-2">
                                    <p class="text-muted">${input_value.Ticket.title}<br><span style="font-size: 12px;">${input_value.Ticket.date}<br></p>
                                </div>
                            </div>
                        </a>
                    `
                })
            } else {
                if (searchInput.value.length > 0) {
                    resultsBox.innerHTML = `<b>${data}</b>`
                } else {
                    resultsBox.classList.add('not-visible')
                }
            }
        },
        error: (error) => {
            console.log(error)
        }
    })
}


searchInput.addEventListener("keyup", e => {

    console.log(e.target.value);
  
    if (resultsBox.classList.contains('not-visible')){
      resultsBox.classList.remove('not-visible')
      }

    sendSearchData(e.target.value)
})
