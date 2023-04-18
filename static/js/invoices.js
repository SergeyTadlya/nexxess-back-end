'use strict'

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

//_________*BLOCK*Cotent-top______

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

const asideInfo = document.querySelector('.aside-info')
const burger = document.querySelector('.burger')

burger.addEventListener('click', menu)

function menu() {
  burger.classList.toggle('burger--active')
  asidefilter.classList.remove('aside-filter--active')
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

//_______FILTER______

const asidefilter = document.querySelector('.aside-filter')
const filterBtn = document.querySelector('.content__filter-btn')
filterBtn.addEventListener('click', filters)

function filters() {
  // burger.classList.toggle('burger--active')
  asideInfo.classList.remove('aside-info--active')
  asidefilter.classList.toggle('aside-filter--active')

  if (document.body.classList.contains('body--active')) {
    document.body.classList.remove('body--active')
  } else {
    document.body.classList.add('body--active')
  }
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