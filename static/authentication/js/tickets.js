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

//__________________________________

const btnNewTag = document.querySelector('#form__new-tag')

const popup = document.querySelector('.popup')
const popupClose = document.querySelector('.popup__close')
const popupInput = document.querySelector('#popup__input')

// ----------OPEN POPUP----------
btnNewTag.addEventListener('click', (e) => {
  // if (navList.classList.contains('header__menu--active')) menu()
  popup.classList.add('show')
  document.body.style.cssText = `overflow: hidden;`
})

// adding # to the beginning of input
popupInput.addEventListener('click', () => {
  popupInput.value = '#'
})

// close on click on overlay
popupClose.addEventListener('click', (e) => {
  popup.classList.remove('show')
  document.body.style.cssText = ''
})

// close on click on overlay
popup.addEventListener('click', (e) => {
  if (e.target === popup) {
    popup.classList.remove('show')
    document.body.style.cssText = ''
  }
})

// close on press of escape button
document.addEventListener('keydown', (e) => {
  if (e.code === 'Escape' && popup.classList.contains('show')) {
    popup.classList.remove('show')
    document.body.style.cssText = ''
  }
})