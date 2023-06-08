const genUrl = window.location.href

var generalUrl = genUrl.slice(0, genUrl.indexOf('/', genUrl.indexOf('/') + 2) + 1);

const generalSearchInput = document.getElementById('gs-input')

const generalResultsBox = document.getElementById('general_results_box')

const generalCsrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

const sendSearchData1 = (input_value) => {
    $.ajax({
        type: 'POST',
        url: generalUrl + 'search/general/',
        data: {
            'csrfmiddlewaretoken': generalCsrf,
            'input_value': input_value,
        },
        success: (response) => {
            console.log(response.data)
            const data = response.data
            if (Array.isArray(data)) {
                generalResultsBox.innerHTML = ""
                data.forEach(input_value => {
                    let html = '';

                    if (typeof input_value === "string" && !html.includes(input_value)) {
                        html += `<p>${input_value}</p>`;
                    } else if (input_value.Service) {
                        html += `
                            <a href="${generalUrl}services/about_service/${input_value.Service.pk}" class="item">
                                <div class="row mt-2 mb-2">
                                    <div class="col-2">
                                        <p class="text-muted">${input_value.Service.name}<br><span style="font-size: 12px;"><i>price:</i>  ${input_value.Service.price}</p>
                                    </div>
                                </div>
                            </a>
                        `;
                    }

                    if (typeof input_value === "string" && !html.includes(input_value)) {
                        html += `<p>${input_value}</p>`;
                    } else if (input_value.Invoice) {
                        html += `
                            <a href="${generalUrl}invoices/detail/${input_value.Invoice.pk}" class="item">
                                <div class="row mt-2 mb-2">
                                    <div class="col-2">
                                        <p class="text-muted"><i>invoice:</i>  ${input_value.Invoice.number}<br><span style="font-size: 12px;"><i>${input_value.Invoice.price}$<br><i>status:</i>  ${input_value.Invoice.status}</p>
                                    </div>
                                </div>
                            </a>
                        `;
                    }

                    if (typeof input_value === "string" && !html.includes(input_value)) {
                        html += `<p>${input_value}</p>`;
                    } else if (input_value.Ticket) {
                        html += `
                            <a href="${generalUrl}search/ticket/${input_value.Ticket.pk}" class="item">
                                <div class="row mt-2 mb-2">
                                    <div class="col-2">
                                        <p class="text-muted">${input_value.Ticket.title}<br><span style="font-size: 12px;">${input_value.Ticket.date}</p>
                                    </div>
                                </div>
                            </a>
                        `;
                    }

                    generalResultsBox.innerHTML += html;
                });

            } else {
                if (generalSearchInput.value.length > 0) {
                    generalResultsBox.innerHTML = `<b>${data}</b>`
                } else {
                    generalResultsBox.classList.add('not-visible')
                }
            }
        },
        error: (error) => {
            console.log(error)
        }
    })
}


generalSearchInput.addEventListener("keyup", a => {

    console.log(a.target.value);

    if (generalResultsBox.classList.contains('not-visible')){
        generalResultsBox.classList.remove('not-visible')
      }

    sendSearchData1(a.target.value)
})
