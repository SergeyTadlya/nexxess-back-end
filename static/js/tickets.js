'use strict'

//__________Mobile content arrow_____

//const contentBox = document.querySelectorAll('.content__body-box')
//const contentBtn = document.querySelectorAll('.content__body-btn')
//
//contentBtn.forEach((button, index) => {
//  button.addEventListener('click', (e) => {
//    contentBox[index].classList.toggle('content__body-activeBox')
//    contentBtn[index].classList.toggle('content__body-activeBtn')
//  })
//})
//
//
//
////_________*BLOCK*Cotent-top______
//
//const contentTopBox = document.querySelector('#content__showing-box')
//const contentTopList = document.querySelector('#content__showing-list')
//const contentTopNumber = document.querySelector('#content__showing-number')
//
//const contentTopItem = document.querySelectorAll('.content__showing-item')
//
//contentTopBox.addEventListener('click', () => {
//  contentTopList.classList.toggle('content__showing--active')
//})
//
//contentTopItem.forEach((item) => {
//  item.addEventListener('click', () => {
//    contentTopNumber.textContent = item.textContent
//  })
//})
//
//// ______CREATE TICKET_____
//const cteareBtn = document.querySelector('#content__create-btn')
//const contentForm = document.querySelector('#content__form')
//
//cteareBtn.addEventListener('click', () => {
//  contentForm.classList.toggle('content__form--active')
//})
//
////_________________POPUP *NEW TAG*_________________
//
//const btnNewTag = document.querySelector('#form__new-tag')
//
//const popup = document.querySelector('.popup')
//const popupClose = document.querySelector('.popup__close')
//const popupInput = document.querySelector('#popup__input')
//
//// ----------OPEN POPUP----------
//btnNewTag.addEventListener('click', (e) => {
//  // if (navList.classList.contains('header__menu--active')) menu()
//  popup.classList.add('show')
//  document.body.style.cssText = `overflow: hidden;`
//})
//
//// adding # to the beginning of input
//popupInput.addEventListener('click', () => {
//  popupInput.value = '#'
//})
//
//// close on click on overlay
//popupClose.addEventListener('click', (e) => {
//  popup.classList.remove('show')
//  document.body.style.cssText = ''
//})
//
//// close on click on overlay
//popup.addEventListener('click', (e) => {
//  if (e.target === popup) {
//    popup.classList.remove('show')
//    document.body.style.cssText = ''
//  }
//})
//
//// close on press of escape button
//document.addEventListener('keydown', (e) => {
//  if (e.code === 'Escape' && popup.classList.contains('show')) {
//    popup.classList.remove('show')
//    document.body.style.cssText = ''
//  }
//})

//__________BURGER AND FILTER__________

// const asideInfo = document.querySelector('.aside-info')
// const burger = document.querySelector('.burger')
// const asidefilter = document.querySelector('.aside-filter')
// const filterBtn = document.querySelector('.content__filter-btn')

// //____BURGER___
// burger.addEventListener('click', menu)

// function menu() {
//   if (burger.classList.contains('burger-filter--active')) {
//     burger.classList.remove('burger-filter--active')
//     asidefilter.classList.remove('aside-filter--active')
//     document.body.classList.remove('body--active')
//     return
//   }

//   burger.classList.toggle('burger--active')
//   asideInfo.classList.toggle('aside-info--active')
  
//   if(document.body.classList.contains('body--active') && !burger.classList.contains('burger--active')) {
//     document.body.classList.remove('body--active')
//   } else {
//     document.body.classList.add('body--active')
//   }
// }





//_____FILTER____

// filterBtn.addEventListener('click', filters)

// function filters() {
//   burger.classList.add('burger-filter--active')
//   asidefilter.classList.add('aside-filter--active')

//   if (document.body.classList.contains('body--active')) {
//     document.body.classList.remove('body--active')
//   } else {
//     document.body.classList.add('body--active')
//   }
// }

'use strict'

//________content__titles_____

const contentTitles = document.querySelectorAll('.content__titles-item');
let isBig = false;
let currentElement = null;

const savedState = localStorage.getItem('elementState');
if (savedState) {
  const { elementId, state } = JSON.parse(savedState);
  currentElement = document.getElementById(elementId);
  isBig = state;

  if (currentElement) {
    currentElement.classList.toggle('content__titles-big-to-small', isBig);
    currentElement.classList.toggle('content__titles-small-to-big', !isBig);
  }
}

for (let item of contentTitles) {
  item.addEventListener('click', function() {
    if (currentElement !== item) {
      if (currentElement) {
        currentElement.classList.remove('content__titles-big-to-small');
        currentElement.classList.remove('content__titles-small-to-big');
        currentElement.classList.add('content__titles-item');
      }
      currentElement = item;
      isBig = false;
    }

    console.log("Current element:", currentElement);

    if (isBig) {
      item.classList.remove('content__titles-big-to-small');
      item.classList.add('content__titles-small-to-big');
      isBig = false;
    } else {
      item.classList.remove('content__titles-small-to-big');
      item.classList.add('content__titles-big-to-small');
      isBig = true;
    }

    const stateToSave = {
      elementId: currentElement.id,
      state: isBig
    };
    localStorage.setItem('elementState', JSON.stringify(stateToSave));

    const ticketLink = document.getElementById(currentElement.id);
    const hrefValue = `?state=${isBig}&ticket_field=${currentElement.id}`;
    ticketLink.setAttribute('href', hrefValue);
  });
}