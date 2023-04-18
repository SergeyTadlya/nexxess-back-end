
//____pages tickets, block aside____
$('#fromDatePicker').datepicker({
  firstDay: 1,
  showOtherMonths: true,
  changeMonth: true,
  changeYear: true,
  dateFormat: 'MM.dd.yy',
})

$('#toDatePicker').datepicker({
  firstDay: 1,
  showOtherMonths: true,
  changeMonth: true,
  changeYear: true,
  dateFormat: 'MM.dd.yy',
})


$('.aside-filter__accordion-date').mousedown(function () {
  $('.ui-datepicker').addClass('active')
})

//___pages tickers , block content form____

$('#contentFormDatePicker').datepicker({
  firstDay: 1,
  showOtherMonths: true,
  changeMonth: true,
  changeYear: true,
  dateFormat: 'MM.dd.yy',
})

$('.content__form__accordion-date').mousedown(function () {
  $('.ui-datepicker').addClass('active')
})
