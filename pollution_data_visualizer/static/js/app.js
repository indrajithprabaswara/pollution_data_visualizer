document.addEventListener('DOMContentLoaded', () => {
    const cities = ['New York', 'Los Angeles', 'San Francisco'];
    const container = document.getElementById('cities');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const suggestions = document.getElementById('suggestions');
    const toggle = document.getElementById('theme-toggle');

    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
        }
    }

    applyTheme(localStorage.getItem('theme'));

    function fetchCityData(city) {
        fetch(`/data/${encodeURIComponent(city)}`)
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }
                renderCityCard(city, data.aqi);
                fetchCityHistory(city);
            })
            .catch(err => console.error(err));
    }

    function fetchCityHistory(city) {
        fetch(`/data/history/${encodeURIComponent(city)}`)
            .then(r => r.json())
            .then(history => {
                const canvas = document.querySelector(`canvas[data-city="${city}"]`);
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const labels = history.map(h => new Date(h.timestamp).toLocaleTimeString());
                const data = history.map(h => h.aqi);
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'AQI',
                            data: data,
                            borderColor: 'rgba(75,192,192,1)',
                            backgroundColor: 'rgba(75,192,192,0.2)',
                            fill: true
                        }]
                    },
                    options: { responsive: true, scales: { y: { beginAtZero: true } } }
                });
            });
    }

    function renderCityCard(city, aqi) {
        let card = document.querySelector(`[data-card="${city}"]`);
        if (!card) {
            const col = document.createElement('div');
            col.className = 'col-md-4 fade-in';
            col.innerHTML = `
                <div class="card" data-card="${city}">
                    <div class="card-body">
                        <h5 class="card-title">${city}</h5>
                        <p class="card-text">AQI: <span class="aqi">${aqi}</span></p>
                        <canvas data-city="${city}"></canvas>
                    </div>
                </div>`;
            container.appendChild(col);
            card = col.querySelector('.card');
        } else {
            card.querySelector('.aqi').textContent = aqi;
        }
    }

    searchInput.addEventListener('input', () => {
        showSuggestions(searchInput, suggestions);
    });

    searchForm.addEventListener('submit', e => {
        e.preventDefault();
        const city = searchInput.value.trim();
        if (city) {
            fetchCityData(city);
            searchInput.value = '';
            suggestions.innerHTML = '';
        }
    });

    toggle.addEventListener('click', () => {
        const light = document.body.classList.toggle('light-mode');
        localStorage.setItem('theme', light ? 'light' : 'dark');
    });

    cities.forEach(fetchCityData);
});
