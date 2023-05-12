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

const headerNav = document.querySelector('.nav__list')
const burger = document.querySelector('.burger')

burger.addEventListener('click', menu)

function menu() {
  burger.classList.toggle('burger--active')
  headerNav.classList.toggle('show-nav')
}