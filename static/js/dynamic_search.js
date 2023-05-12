  // Получаем элементы, которые нужно подсветить
  const listItems = document.querySelectorAll('#list li');

  // Получаем поле ввода
  const searchInput = document.querySelector('#search-input');

  // Обрабатываем событие ввода на поле ввода
  searchInput.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase().trim(); // Получаем введенный текст, удаляем пробелы в начале и конце и приводим к нижнему регистру

    // Если ничего не введено, убираем подсветку со всех элементов списка
    if (searchTerm === '') {
      listItems.forEach(item => item.classList.remove('highlight'));
      return;
    }

    // Проходим по всем элементам списка
    listItems.forEach(item => {
      const text = item.textContent.toLowerCase(); // Получаем текст элемента и приводим к нижнему регистру

      // Если текст содержит введенный символ, добавляем класс highlight, иначе удаляем
      if (text.includes(searchTerm)) {
        item.classList.add('highlight');
      } else {
        item.classList.remove('highlight');
      }
    });
  });