const url = window.location.href

// const searchForm = document.getElementById('search-form')

const searchInput = document.getElementById('search-input')

const resultsBox = document.getElementById('results_box')

const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

const sendSearchData = (input_value) => {
    $.ajax({    
        type: 'POST',    
        url: 'search/general/',    
        data: {
            'csrfmiddlewaretoken': csrf,
            'input_value': input_value,
        },    
        success: (response) => {    
            console.log(response.data)
            const data = response.data
            if (Array.isArray(data)) {
                resultsBox.innerHTML = ""
                data.forEach(input_value => {
                    let html = '';
                    
                    if (typeof input_value === "string" && !html.includes(input_value)) {
                        html += `<p>${input_value}</p>`;
                    } else if (input_value.Service) {
                        html += `
                            <a href="${url}search/service/${input_value.Service.pk}" class="item">
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
                            <a href="${url}search/invoice/${input_value.Invoice.pk}" class="item">
                                <div class="row mt-2 mb-2">
                                    <div class="col-2">
                                        <p class="text-muted"><i>ID:</i>  ${input_value.Invoice.number}<br><span style="font-size: 12px;"><i>${input_value.Invoice.price}$<br><i>status:</i>  ${input_value.Invoice.status}</p>
                                    </div>
                                </div>
                            </a>
                        `;
                    }
                    
                    if (typeof input_value === "string" && !html.includes(input_value)) {
                        html += `<p>${input_value}</p>`;
                    } else if (input_value.Ticket) {
                        html += `
                            <a href="${url}search/ticket/${input_value.Ticket.pk}" class="item">
                                <div class="row mt-2 mb-2">
                                    <div class="col-2">
                                        <p class="text-muted">${input_value.Ticket.title}<br><span style="font-size: 12px;">${input_value.Ticket.date}</p>
                                    </div>
                                </div>
                            </a>
                        `;
                    }
                    
                    resultsBox.innerHTML += html;
                });
                
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

let keyPressCount = 0

searchInput.addEventListener("keyup", e => {
    keyPressCount++
  
    if (keyPressCount % 2 === 0 ) {
      console.log(e.target.value)
    //   sendSearchData(e.target.value)  пошук при введенні кожного другого символу
    }
  
    if (resultsBox.classList.contains('not-visible')){
      resultsBox.classList.remove('not-visible')
      }

    sendSearchData(e.target.value)
})
