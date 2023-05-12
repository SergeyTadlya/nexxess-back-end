'use strict'

const accordionBtn = document.querySelectorAll('#aside-info__accordion-top')
const accordionList = document.querySelectorAll('.aside-info__accordion-list')
const accordionArrow = document.querySelectorAll('.aside-info__top-arrow')

//________BURGER_____

const asideInfo = document.querySelector('.aside-info')
const burger = document.querySelector('.burger')

burger.addEventListener('click', menu)

function menu() {
  burger.classList.toggle('burger--active')
  asideInfo.classList.toggle('aside-info--active')

  if (document.body.classList.contains('body--active')) {
    document.body.classList.remove('body--active')
  } else {
    document.body.classList.add('body--active')
  }
}

$(document).ready(function () {
  $(".order_click").click(function()
  {
    var button = $(".order_click")[0];
    var b24_product_id = $(button).data("b24id");
    alert(b24_product_id);
    $.ajax({
      url: '/services/create_invoice/',
      type: 'POST',
      data: {"b24_product_id":b24_product_id},
      dataType: 'json',
      success: function(data) {
        if (data.invoice_id){
          window.location.href = '/invoices/';
        }else
        {
          alert("We have some problem. Please try late")
        }
        console.log(data);

      },
    });
  });
});

