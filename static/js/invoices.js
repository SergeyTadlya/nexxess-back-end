'use strict'

//_________*BLOCK*Cotent-top______

const contentTopBox = document.querySelector('#content__showing-box')
const contentTopList = document.querySelector('#content__showing-list')
const contentTopNumber = document.querySelector('#content__showing-number')

const contentTopItem = document.querySelectorAll('.content__showing-item')

contentTopBox.addEventListener('click', () => {
  contentTopList.classList.toggle('content__showing--active')
})

contentTopItem.forEach((item) => {
  item.addEventListener('click', () => {
    contentTopNumber.textContent = item.textContent
  })
})

//________content__titles_____

const contentTitles = document.querySelectorAll('.content__titles-item');
let isBig = false;
let currentElement = null;

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
