document.addEventListener('DOMContentLoaded', () => {
    const cities = ['New York', 'Los Angeles', 'San Francisco'];
    const container = document.getElementById('cities');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const suggestions = document.getElementById('suggestions');
    const toggle = document.getElementById('theme-toggle');
    let chartType = 'line';
    let detailChart = null;
    let currentCity = '';

    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
        }
    }

    applyTheme(localStorage.getItem('theme'));

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(t => new bootstrap.Tooltip(t));

    function fetchCityData(city) {
        fetch(`/data/${encodeURIComponent(city)}`)
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }
                renderCityCard(city, data);
            })
            .catch(err => console.error(err));
    }

    function fetchCityHistory(city, hrs = 24) {
        fetch(`/data/history/${encodeURIComponent(city)}?hours=${hrs}`)
            .then(r => r.json())
            .then(history => {
                const cardCanvas = document.querySelector(`canvas[data-city="${city}"]`);
                const labels = history.map(h => new Date(h.timestamp).toLocaleTimeString());
                const data = history.map(h => h.aqi);

                if (cardCanvas) {
                    const ctx = cardCanvas.getContext('2d');
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
                        options: { responsive: true,
                                   scales: { y: { beginAtZero: true } },
                                   animation: { duration: 1000 },
                                   interaction: { mode: 'index', intersect: false } }
                    });
                }

                const detailCanvas = document.getElementById('historyChart');
                if (detailCanvas) {
                    const ctx2 = detailCanvas.getContext('2d');
                    if (detailChart) detailChart.destroy();
                    detailChart = new Chart(ctx2, {
                        type: chartType,
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
                        options: { responsive: true,
                                   scales: { y: { beginAtZero: true } },
                                   animation: { duration: 1000 },
                                   interaction: { mode: 'index', intersect: false } }
                    });
                }

                updatePieChart(city, history);
                showPollutantBreakdown(city, history);
            });
    }

    function renderCityCard(city, data) {
        let card = document.querySelector(`[data-card="${city}"]`);
        if (!card) {
            const col = document.createElement('div');
            col.className = 'col-md-4 fade-in';
            col.innerHTML = `
                <div class="card" data-card="${city}">
                    <div class="card-body">
                        <h5 class="card-title">${city}</h5>
                        <p class="card-text">AQI: <span class="aqi">${data.aqi}</span></p>
                        <p class="small">PM2.5: <span class="pm25">${data.pm25 ?? 'N/A'}</span></p>
                        <p class="small">CO: <span class="co">${data.co ?? 'N/A'}</span></p>
                        <p class="small">NO2: <span class="no2">${data.no2 ?? 'N/A'}</span></p>
                        <canvas data-city="${city}"></canvas>
                    </div>
                </div>`;
            container.appendChild(col);
            card = col.querySelector('.card');
            card.addEventListener('click', () => openDetail(city));
            highlightCard(col);
            card.scrollIntoView({ behavior: 'smooth' });
        } else {
            card.querySelector('.aqi').textContent = data.aqi;
            card.querySelector('.pm25').textContent = data.pm25 ?? 'N/A';
            card.querySelector('.co').textContent = data.co ?? 'N/A';
            card.querySelector('.no2').textContent = data.no2 ?? 'N/A';
            highlightCard(card.parentElement);
        }
        fetchCityHistory(city, 24);
    }

    function highlightCard(element) {
        element.classList.add('highlight');
        setTimeout(() => element.classList.remove('highlight'), 2000);
    }

    function updatePieChart(city, history) {
        const counts = { good: 0, moderate: 0, bad: 0 };
        history.forEach(h => {
            if (h.aqi <= 50) counts.good++; else if (h.aqi <= 100) counts.moderate++; else counts.bad++;
        });
        const total = counts.good + counts.moderate + counts.bad;
        const ctx = document.getElementById('pieChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Good', 'Moderate', 'Bad'],
                datasets: [{
                    data: [counts.good, counts.moderate, counts.bad],
                    backgroundColor: ['green', 'yellow', 'red']
                }]
            },
            options: { animation: { animateScale: true, animateRotate: true } }
        });
        document.getElementById('bar-good').style.width = `${(counts.good/total)*100}%`;
        document.getElementById('bar-moderate').style.width = `${(counts.moderate/total)*100}%`;
        document.getElementById('bar-bad').style.width = `${(counts.bad/total)*100}%`;
        const advice = document.querySelector('#advice');
        let text = 'Nice! Your area is not polluted.';
        advice.classList.remove('neon-warning');
        if (counts.bad > counts.moderate && counts.bad > counts.good) {
            text = 'Warning! It\'s highly polluted in your area. It\'s recommended to wear a mask and stay indoors.';
            advice.classList.add('neon-warning');
        } else if (counts.moderate >= counts.good && counts.moderate >= counts.bad) {
            text = 'Pollution is moderate. Consider using public transport to help reduce pollution.';
        }
        typeAdvice(text);
    }

    function showPollutantBreakdown(city, history) {
        const pm25 = { good: 0, moderate: 0, bad: 0 };
        const co = { good: 0, moderate: 0, bad: 0 };
        const no2 = { good: 0, moderate: 0, bad: 0 };
        history.forEach(h => {
            categorize(h.pm25, pm25, 12, 35);
            categorize(h.co, co, 4, 9);
            categorize(h.no2, no2, 53, 100);
        });
        const ctx = document.getElementById('pollutantChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Good', 'Moderate', 'Bad'],
                datasets: [
                    { label: 'PM2.5', backgroundColor: 'rgba(75,192,192,0.6)', data: [pm25.good, pm25.moderate, pm25.bad] },
                    { label: 'CO', backgroundColor: 'rgba(255,99,132,0.6)', data: [co.good, co.moderate, co.bad] },
                    { label: 'NO2', backgroundColor: 'rgba(255,206,86,0.6)', data: [no2.good, no2.moderate, no2.bad] }
                ]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } }, animation: { duration: 1000 } }
        });
    }

    function categorize(value, obj, good, moderate) {
        if (value == null) return;
        if (value <= good) obj.good++; else if (value <= moderate) obj.moderate++; else obj.bad++;
    }

    function animateValue(el, to, duration) {
        const element = typeof el === 'string' ? document.getElementById(el) : el;
        if (!element) return;
        const start = 0;
        const increment = to / (duration / 20);
        let current = start;
        element.textContent = current.toFixed(0);
        const timer = setInterval(() => {
            current += increment;
            if (current >= to) {
                current = to;
                clearInterval(timer);
            }
            element.textContent = current.toFixed(0);
        }, 20);
    }

    function typeAdvice(text) {
        const el = document.querySelector('#advice');
        if (!el) return;
        el.textContent = '';
        let i = 0;
        const interval = setInterval(() => {
            el.textContent += text[i];
            i++;
            if (i >= text.length) clearInterval(interval);
        }, 50);
    }

    let detailDrawer;
    function openDetail(city) {
        if (!detailDrawer) {
            detailDrawer = new bootstrap.Offcanvas('#detailDrawer');
        }
        const title = document.getElementById('detailTitle');
        title.textContent = city;
        currentCity = city;

        const card = document.querySelector(`[data-card="${city}"]`);
        animateValue('detail-aqi', parseFloat(card.querySelector('.aqi').textContent), 800);
        animateValue('detail-pm25', parseFloat(card.querySelector('.pm25').textContent) || 0, 800);
        animateValue('detail-co', parseFloat(card.querySelector('.co').textContent) || 0, 800);
        animateValue('detail-no2', parseFloat(card.querySelector('.no2').textContent) || 0, 800);

        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(t => new bootstrap.Tooltip(t));

        document.getElementById('bar-good').style.width = '0%';
        document.getElementById('bar-moderate').style.width = '0%';
        document.getElementById('bar-bad').style.width = '0%';

        fetchCityHistory(city, 168);
        detailDrawer.show();
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

    const toggleBtn = document.getElementById('chartToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            chartType = chartType === 'line' ? 'bar' : 'line';
            if (currentCity) {
                fetchCityHistory(currentCity, 168);
            }
        });
    }

    document.getElementById('advice').addEventListener('click', () => {
        alert('See more tips on reducing exposure to air pollution.');
    });

    cities.forEach(city => {
        fetchCityData(city);
        setInterval(() => fetchCityData(city), 60000);
    });
});
