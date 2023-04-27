'use strict'

const accordionBtn = document.querySelectorAll('#aside-info__accordion-top')
const accordionList = document.querySelectorAll('.aside-info__accordion-list')
const accordionArrow = document.querySelectorAll('.aside-info__top-arrow')

accordionBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    accordionBtn[index].classList.toggle('accordion__top--active')
    accordionList[index].classList.toggle('accordion__list--active')
    accordionArrow[index].classList.toggle('accordion__arrow--active')
  })
})

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