'use strict'

//________BURGER_____

const headerNav = document.querySelector('.nav__list')
const burger = document.querySelector('.burger')

// burger.addEventListener('click', menu)

burger.onclick = function () {
  burger.classList.toggle('burger--active')
  headerNav.classList.toggle('show-nav')
}


/// Tickets Acardion


const accordionBtn = document.querySelectorAll('#aside-info__accordion-top');
const accordionList = document.querySelectorAll('.aside-info__accordion-list');
const accordionArrow = document.querySelectorAll('.aside-info__top-arrow');




accordionBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    accordionBtn[index].classList.toggle('accordion__top--active')
    accordionList[index].classList.toggle('accordion__list--active')
    accordionArrow[index].classList.toggle('accordion__arrow--active')

  })
})

const accordionFilterBtn = document.querySelectorAll('#aside-filter__accordion-top')
const accordionFilterList = document.querySelectorAll('.aside-filter__accordion-list')
const accordionFilterArrow = document.querySelectorAll('.aside-filter__top-arrow')

accordionFilterBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    accordionFilterBtn[index].classList.toggle('accordion__top--active')
    accordionFilterList[index].classList.toggle('accordion__list--active')
    accordionFilterArrow[index].classList.toggle('accordion__arrow--active')
  })
})
