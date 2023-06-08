document.addEventListener('DOMContentLoaded', function() {
    const contentTopBox = document.querySelector('#content__showing-box');
    const contentTopList = document.querySelector('#content__showing-list');

  
    contentTopBox.addEventListener('click', () => {
      contentTopList.classList.toggle('content__showing--active');
    });
  });
  