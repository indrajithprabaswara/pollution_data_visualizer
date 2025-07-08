const popularCities = [
  'New York',
  'Los Angeles',
  'Chicago',
  'Houston',
  'Phoenix',
  'Philadelphia',
  'San Antonio',
  'San Diego',
  'Dallas',
  'San Jose'
];

function showSuggestions(input, container) {
  const value = input.value.toLowerCase();
  container.innerHTML = '';
  if (!value) return;
  popularCities.filter(c => c.toLowerCase().startsWith(value)).forEach(city => {
    const item = document.createElement('a');
    item.className = 'list-group-item list-group-item-action';
    item.textContent = city;
    item.addEventListener('click', () => {
      input.value = city;
      container.innerHTML = '';
    });
    container.appendChild(item);
  });
}
