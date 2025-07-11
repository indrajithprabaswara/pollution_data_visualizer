document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('favorites-body');
  let saved = JSON.parse(localStorage.getItem('savedCities') || '[]');
  const alerts = JSON.parse(localStorage.getItem('alerts') || '{}');

  function render() {
    tbody.innerHTML = '';
    saved.forEach(city => {
      const tr = document.createElement('tr');
      tr.dataset.city = city;
      tr.innerHTML = `
        <td>${city}</td>
        <td><input type="number" class="form-control alert-input" value="${alerts[city] || 150}"></td>
        <td><button type="button" class="btn btn-danger remove-btn">Remove</button></td>`;
      tr.querySelector('.remove-btn').addEventListener('click', () => {
        saved = saved.filter(c => c !== city);
        delete alerts[city];
        localStorage.setItem('savedCities', JSON.stringify(saved));
        localStorage.setItem('alerts', JSON.stringify(alerts));
        tr.remove();
      });
      tbody.appendChild(tr);
    });
  }

  document.getElementById('saveFavs').addEventListener('click', () => {
    document.querySelectorAll('#favorites-body tr').forEach(row => {
      const city = row.dataset.city;
      const alertVal = parseInt(row.querySelector('.alert-input').value, 10) || 150;
      alerts[city] = alertVal;
    });
    localStorage.setItem('alerts', JSON.stringify(alerts));
    showToast('Saved', 'success', 3000);
  });

  render();
});
