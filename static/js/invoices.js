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

//_________________

const contentTopBox = document.querySelector('#content__top-box')
const contentTopList = document.querySelector('#content__top-list')
const contentTopNumber = document.querySelector('#content__top-number')

const contentTopItem = document.querySelectorAll('.content__top-item')

contentTopBox.addEventListener('click', () => {
  contentTopList.classList.toggle('top__list--active')
})

contentTopItem.forEach((item) => {
  item.addEventListener('click', () => {
    contentTopNumber.textContent = item.textContent
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

//_______MOBILE_____

const mobileBox = document.querySelectorAll('.content__mobile-box')
const mobileBtn = document.querySelectorAll('.content__mobile-btn')
// const mobileBtn = document.querySelectorAll('.content__mobile-btn')

mobileBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    mobileBox[index].classList.toggle('content__mobile-activeBox')
    mobileBtn[index].classList.toggle('content__mobile-activeBtn')
    // mobileBox[index].style.height = '125px'
    // console.log();
  })
})