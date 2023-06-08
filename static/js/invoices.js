'use strict'


//________content__titles_____

const contentTitles = document.querySelectorAll('.content__titles-item');
let isBig = false;
let currentElement = null;

const savedState = localStorage.getItem('elementState');
if (savedState) {
  const { elementId, state } = JSON.parse(savedState);
  currentElement = document.getElementById(elementId);
  isBig = state;

  if (currentElement) {
    currentElement.classList.toggle('content__titles-big-to-small', isBig);
    currentElement.classList.toggle('content__titles-small-to-big', !isBig);
  }
}

for (let item of contentTitles) {
  item.addEventListener('click', function() {
    if (currentElement !== item) {
      if (currentElement) {
        currentElement.classList.remove('content__titles-big-to-small');
        currentElement.classList.remove('content__titles-small-to-big');
        currentElement.classList.add('content__titles-item');
      }
      currentElement = item;
      isBig = false;
    }

    if (isBig) {
      item.classList.remove('content__titles-big-to-small');
      item.classList.add('content__titles-small-to-big');
      isBig = false;
    } else {
      item.classList.remove('content__titles-small-to-big');
      item.classList.add('content__titles-big-to-small');
      isBig = true;
    }

    const stateToSave = {
      elementId: currentElement.id,
      state: isBig
    };
    localStorage.setItem('elementState', JSON.stringify(stateToSave));

    const invoiceLink = document.getElementById(currentElement.id);
    const hrefValue = `?state=${isBig}&invoice_field=${currentElement.id}`;
    invoiceLink.setAttribute('href', hrefValue);
  });
}

//_______Mobile content arrow_____

const contentBox = document.querySelectorAll('.content__body-box')
const contentBtn = document.querySelectorAll('.content__body-btn')

contentBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    contentBox[index].classList.toggle('content__body-activeBox')
    contentBtn[index].classList.toggle('content__body-activeBtn')
  })
})

// $(document).ready(function () {
//   $(".button_pay").click(function()
//   {
//     var button = $(this);
//     var b24_product_id = $(button).data("b24invoice");
//
//     $.ajax({
//       url: '/invoices/create_payment_link/',
//       type: 'POST',
//       data: {"b24_invoice_id":b24_product_id},
//       dataType: 'json',
//       success: function(data) {
//         if (data.pay_link){
//           window.location.href = data.pay_link;
//         }else
//         {
//           alert("We have some problem. Please try late")
//         }
//       },
//     });
//   });
// });
