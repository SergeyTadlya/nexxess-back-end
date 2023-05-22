'use strict'


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


const accordionBtnInfo = document.querySelector('.aside-info__box-top');
const accordionArrowInfo = document.querySelector('.aside-info__top-title-arrow');
const accordionHeightInfo = document.querySelector('.aside-info__box');

accordionBtnInfo.onclick = function () {
  accordionBtnInfo.classList.toggle('accordion__top--active');
  accordionArrowInfo.classList.toggle('accordion__arrow--active');
  accordionHeightInfo.classList.toggle('accordion__list--active');
}
