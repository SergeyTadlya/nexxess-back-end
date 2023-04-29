'use strict'

// _____Event click on the header icon___

const headerIcon = document.querySelectorAll('.header__box-icon')[0]
const headerLinks = document.querySelector('.header__box-links')

headerIcon.addEventListener('mouseenter', (e) => {
  e.preventDefault()
  headerLinks.style.display = 'flex'
})

headerIcon.addEventListener('mouseleave', (e) => {
  e.preventDefault()
  headerLinks.style.display = 'none'
})

headerLinks.addEventListener('mouseenter', (e) => {
  headerLinks.style.display = 'flex'
})

headerLinks.addEventListener('mouseleave', (e) => {
  headerLinks.style.display = 'none'
})

//______ACCORDION______

const accordionInfoBtn = document.querySelectorAll('#aside-info__accordion-top')
const accordionInfoList = document.querySelectorAll(
  '.aside-info__accordion-list'
)
const accordionInfoArrow = document.querySelectorAll('.aside-info__top-arrow')

accordionInfoBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    accordionInfoBtn[index].classList.toggle('accordion__top--active')
    accordionInfoList[index].classList.toggle('accordion__list--active')
    accordionInfoArrow[index].classList.toggle('accordion__arrow--active')
  })
})

const accordionFilterBtn = document.querySelectorAll(
  '#aside-filter__accordion-top'
)
const accordionFilterList = document.querySelectorAll(
  '.aside-filter__accordion-list'
)
const accordionFilterArrow = document.querySelectorAll(
  '.aside-filter__top-arrow'
)

accordionFilterBtn.forEach((button, index) => {
  button.addEventListener('click', (e) => {
    accordionFilterBtn[index].classList.toggle('accordion__top--active')
    accordionFilterList[index].classList.toggle('accordion__list--active')
    accordionFilterArrow[index].classList.toggle('accordion__arrow--active')
  })
})

//________BURGER_____

const asideInfo = document.querySelector('.aside-info')
const burger = document.querySelector('.burger')
const asidefilter = document.querySelector('.aside-filter')
const filterBtn = document.querySelector('.content__filter-btn')

burger.addEventListener('click', menu)

function menu() {
  if (burger.classList.contains('burger-filter--active')) {
    burger.classList.remove('burger-filter--active')
    asidefilter.classList.remove('aside-filter--active')
    document.body.classList.remove('body--active')
    return
  }

  burger.classList.toggle('burger--active')
  asideInfo.classList.toggle('aside-info--active')

  if (
    document.body.classList.contains('body--active') &&
    !burger.classList.contains('burger--active')
  ) {
    document.body.classList.remove('body--active')
  } else {
    document.body.classList.add('body--active')
  }
}
