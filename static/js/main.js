'use strict'

const accordionBtn = document.querySelectorAll('#aside__accordion-top')
const accordionList = document.querySelectorAll('.aside__accordion-list')
const accordionArrow = document.querySelectorAll('.aside__top-arrow')

accordionBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    accordionBtn[index].classList.toggle('accordion__top--active')
    accordionList[index].classList.toggle('accordion__list--active')
    accordionArrow[index].classList.toggle('accordion__arrow--active')
  })
})

//________BURGER_____

const aside = document.querySelector('.aside')
const burger = document.querySelector('.burger')

burger.addEventListener('click', menu)

function menu() {
  burger.classList.toggle('burger--active')
  aside.classList.toggle('aside--active')

  const overflowValue = burger.classList.contains('burger--active')
    ? 'hidden'
    : 'auto'

  document.body.style.overflow = overflowValue
}
