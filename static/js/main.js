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


function time() {
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];


  const day = new Date ();
  document.getElementById('day').innerHTML = day.getDate();
  document.getElementById('month').innerHTML = months[day.getMonth()];
  document.getElementById('date').innerHTML = days[day.getDay()];
}

time();

function moveElements() {
  if (window.innerWidth <= 768) {
    let titleDesctop = document.querySelector('.title__inner');
    let titleMobsle = document.querySelector('.mobile__title');
    while (titleDesctop.firstChild) {
      titleMobsle.appendChild(titleDesctop.firstChild);
    }
  }
}

window.onload = moveElements;
window.onresize = moveElements;
