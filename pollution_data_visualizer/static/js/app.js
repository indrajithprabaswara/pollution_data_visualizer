document.addEventListener('DOMContentLoaded', () => {
    const cities = ['New York', 'Los Angeles', 'San Francisco', 'Paris', 'Delhi', 'Perth'];
    const container = document.getElementById('cities');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const toggle = document.getElementById('theme-toggle');
    const compareBtn = document.getElementById('compareBtn');
    let savedCities = JSON.parse(localStorage.getItem('savedCities') || '[]');
    let searchedCities = [];
    const alerts = JSON.parse(localStorage.getItem('alerts') || '{}');
    let chartType = 'line';
    let detailChart = null;
    let currentCity = '';
    const socket = io();
    const map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);
    const markers = {};
    let loadingToast = null;

    function showToast(message, type='info', delay=4000, autohide=true) {
        const container = document.getElementById('toast-container');
        const div = document.createElement('div');
        div.className = `toast align-items-center text-bg-${type} border-0`;
        div.role = 'alert';
        div.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div>` +
            `<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
        container.appendChild(div);
        const toast = new bootstrap.Toast(div, { delay: delay, autohide: autohide });
        toast.show();
        div.addEventListener('hidden.bs.toast', () => div.remove());
        return toast;
    }

    function showLoading(city) {
        loadingToast = showToast('Adding ' + city + '... please wait', 'secondary', 5000, false);
    }

    function hideLoading() {
        if (loadingToast) {
            loadingToast.hide();
            loadingToast = null;
        }
    }

    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
        }
    }

    applyTheme(localStorage.getItem('theme'));

    savedCities.forEach(c => fetchCityData(c, false));

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(t => new bootstrap.Tooltip(t));

    function addCityToList(city) {
        if (!cities.includes(city)) {
            cities.push(city);
            setInterval(() => fetchCityData(city), 1800000);
            searchedCities.push(city);
        }
    }

    function fetchWithTimeout(url, options = {}, timeout = 8000) {
        return Promise.race([
            fetch(url, options),
            new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), timeout))
        ]);
    }

    function fetchCityData(city, scroll=false) {
        document.getElementById('loading').style.display = 'inline-block';
        return fetchWithTimeout(`/data/${encodeURIComponent(city)}`)
            .then(r => r.json())
            .then(history => {
                if (history.error) {
                    console.error(history.error);
                    fetchCoords(city, null);
                    document.getElementById('loading').style.display = 'none';
                    return;
                }
                const latest = history[history.length - 1] || {};
                renderCityCard(city, latest, scroll); // updated to OpenAQ v3
                fetchCoords(city, latest.value);
                document.getElementById('loading').style.display = 'none';
            })
            .catch(err => {
                console.error(err);
                document.getElementById('loading').style.display = 'none';
                showToast('Failed to fetch data for ' + city, 'danger', 4000);
                fetchCoords(city, null);
            });
    }

    function fetchCityHistory(city, hrs = 48) {
        fetch(`/data/${encodeURIComponent(city)}`) // updated to OpenAQ v3
            .then(r => r.json())
            .then(history => {
                const cardCanvas = document.querySelector(`canvas[data-city="${city}"]`);
                const labels = history.map(h => new Date(h.utc_datetime).toLocaleTimeString()); // updated to OpenAQ v3
                const data = history.map(h => h.value); // updated to OpenAQ v3

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
                                   animation: { duration: 1000, easing: 'easeOutQuart' },
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
                                   animation: { duration: 1000, easing: 'easeOutQuart' },
                                   interaction: { mode: 'index', intersect: false } }
                    });
                }

                updatePieChart(city, history);
                showPollutantBreakdown(city, history);
            });
    }

    function renderCityCard(city, data, scroll) {
        const slug = city.toLowerCase().replace(/\s+/g, '');
        let card = document.querySelector(`[data-card="${city}"]`);
        if (!card) {
            const col = document.createElement('div');
            col.className = 'col-sm-6 col-md-4 fade-in';
            col.innerHTML = `
                <div class="card card-hover" data-card="${city}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                          <h5 class="card-title">${city}</h5>
                          <div>
                            <input class="form-check-input compare-check" type="checkbox" data-city="${city}">
                            <button class="btn btn-sm btn-outline-primary ms-2 save-btn" data-city="${city}">Save</button>
                          </div>
                        </div>
                        <p class="card-text">Value: <span class="aqi">${data.value}</span> ${data.unit}</p> // updated to OpenAQ v3
                        <p class="small">Location: <span class="location">${data.location}</span></p> // updated to OpenAQ v3
                        <p class="small">Time: <span class="utc">${new Date(data.utc_datetime).toLocaleString()}</span></p> // updated to OpenAQ v3
                        <canvas data-city="${city}"></canvas>
                    </div>
                </div>`;
            container.appendChild(col);
            card = col.querySelector('.card');
            card.addEventListener('click', () => openDetail(city));
            col.querySelector('.save-btn').addEventListener('click', e => {
                e.stopPropagation();
                saveCity(city);
            });
            highlightCard(col);
            if (alerts[city] && data.aqi >= alerts[city]) {
                col.querySelector('.card').classList.add('neon-warning');
                showToast(`${city} AQI exceeds ${alerts[city]}`, 'warning', 5000);
            }
            if (scroll) {
                card.scrollIntoView({ behavior: 'smooth' });
                showToast(`Done! See the pollution levels for ${city}`, 'success', 4000);
            }
        } else {
            card.querySelector('.aqi').textContent = data.value; // updated to OpenAQ v3
            const locEl = card.querySelector('.location');
            if (locEl) locEl.textContent = data.location; // updated to OpenAQ v3
            const timeEl = card.querySelector('.utc');
            if (timeEl) timeEl.textContent = new Date(data.utc_datetime).toLocaleString(); // updated to OpenAQ v3
            highlightCard(card.parentElement);
            if (alerts[city] && data.value >= alerts[city]) {
                card.classList.add('neon-warning');
                showToast(`${city} AQI exceeds ${alerts[city]}`, 'warning', 5000);
            } else {
                card.classList.remove('neon-warning');
            }
        }
        fetchCityHistory(city, 48);
    }

    function highlightCard(element) {
        element.classList.add('highlight');
        setTimeout(() => element.classList.remove('highlight'), 2000);
    }

    function updatePieChart(city, history) {
        const counts = { good: 0, moderate: 0, bad: 0 };
        history.forEach(h => {
            if (h.value <= 50) counts.good++; else if (h.value <= 100) counts.moderate++; else counts.bad++; // updated to OpenAQ v3
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
            options: {
                animation: { animateScale: true, animateRotate: true, duration: 1000, easing: 'easeOutQuart' },
                plugins: { tooltip: { enabled: true } }
            }
        });
        document.getElementById('bar-good').style.width = `${(counts.good/total)*100}%`;
        document.getElementById('bar-moderate').style.width = `${(counts.moderate/total)*100}%`;
        document.getElementById('bar-bad').style.width = `${(counts.bad/total)*100}%`;
        const advice = document.querySelector('#advice');
        const latest = history[history.length - 1]?.value || 0; // updated to OpenAQ v3
        let text = 'Nice! Your area is not polluted.';
        advice.classList.remove('neon-warning');
        if (latest > 100) {
            text = 'Warning! It\'s highly polluted in your area. It\'s recommended to wear a mask and stay indoors.';
            advice.classList.add('neon-warning');
        } else if (latest > 50) {
            text = 'Pollution is moderate. Consider using public transport to help reduce pollution.';
        }
        typeAdvice(text);
    }

    function showPollutantBreakdown(city, history) {
        const counts = { good: 0, moderate: 0, bad: 0 };
        history.forEach(h => {
            categorize(h.value, counts, 12, 35); // updated to OpenAQ v3
        });
        const ctx = document.getElementById('pollutantChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Good', 'Moderate', 'Bad'],
                datasets: [
                    { label: 'Value', backgroundColor: 'rgba(75,192,192,0.6)', data: [counts.good, counts.moderate, counts.bad] }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } },
                animation: { duration: 1000, easing: 'easeOutQuart' },
                plugins: { tooltip: { enabled: true } },
                interaction: { mode: 'index', intersect: false }
            }
        });
    }

    function categorize(value, obj, good, moderate) {
        if (value == null) return;
        if (value <= good) obj.good++; else if (value <= moderate) obj.moderate++; else obj.bad++;
    }

    function saveCity(city) {
        if (!savedCities.includes(city)) {
            savedCities.push(city);
            localStorage.setItem('savedCities', JSON.stringify(savedCities));
        } else {
            savedCities = savedCities.filter(c => c !== city);
            localStorage.setItem('savedCities', JSON.stringify(savedCities));
        }
        const current = alerts[city] || 150;
        const val = prompt('Alert threshold for ' + city, current);
        if (val) {
            alerts[city] = parseInt(val, 10);
            localStorage.setItem('alerts', JSON.stringify(alerts));
        }
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
        el.textContent = text;
        el.style.animation = 'none';
        void el.offsetWidth;
        el.style.animation = '';
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
        animateValue('detail-aqi', parseFloat(card.querySelector('.aqi').textContent), 800); // updated to OpenAQ v3

        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(t => new bootstrap.Tooltip(t));

        document.getElementById('bar-good').style.width = '0%';
        document.getElementById('bar-moderate').style.width = '0%';
        document.getElementById('bar-bad').style.width = '0%';

        fetchCityHistory(city, 168);
        detailDrawer.show();
    }

    initAutocomplete('#search-input');

    async function submitSearch() {
        const city = searchInput.value.trim();
        if (!city) return;
        if (searchInput.disabled) return;
        searchInput.disabled = true;
        showLoading(city);
        const enableTimer = setTimeout(() => {
            searchInput.disabled = false;
        }, 12000);
        try {
            await fetchCityData(city, true);
            addCityToList(city);
        } finally {
            clearTimeout(enableTimer);
            hideLoading();
            searchInput.disabled = false;
            searchInput.value = '';
        }
    }

    searchForm.addEventListener('submit', e => {
        e.preventDefault();
        submitSearch();
    });

    searchInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            e.preventDefault();
            submitSearch();
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

    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            const selected = Array.from(document.querySelectorAll('.compare-check:checked')).map(c => c.dataset.city);
            if (selected.length < 2) { alert('Select at least two cities'); return; }
            Promise.all(selected.map(c => fetch(`/data/${encodeURIComponent(c)}`))) // updated to OpenAQ v3
                .then(responses => Promise.all(responses.map(r => r.json())))
                .then(dataArr => {
                    const labels = dataArr[0].map(h => new Date(h.utc_datetime).toLocaleTimeString()); // updated to OpenAQ v3
                    const datasets = selected.map((city,i) => ({
                        label: city,
                        data: dataArr[i].map(h => h.value), // updated to OpenAQ v3
                        borderColor: ['red','blue','green','orange','purple'][i%5],
                        fill:false
                    }));
                    const ctx = document.getElementById('compareChart').getContext('2d');
                    if (window.compareChart) window.compareChart.destroy();
                    window.compareChart = new Chart(ctx, {
                        type: 'line',
                        data: { labels, datasets },
                        options: {
                            responsive: true,
                            animation: { duration: 1000, easing: 'easeOutQuart' },
                            interaction: { mode: 'index', intersect: false }
                        }
                    });

                    const barLabels = ['PM2.5', 'CO', 'NO2'];
                    const barData = selected.map((city,i) => {
                        const avg = dataArr[i].reduce((s,h)=>s+(h.value||0),0)/dataArr[i].length;
                        return {
                            label: city,
                            data: [avg, avg, avg], // updated to OpenAQ v3
                            backgroundColor: ['rgba(75,192,192,0.5)','rgba(255,99,132,0.5)','rgba(255,206,86,0.5)'][i%3]
                        };
                    });
                    const ctx2 = document.getElementById('comparePollutantChart').getContext('2d');
                    if (window.comparePollutantChart) window.comparePollutantChart.destroy();
                    window.comparePollutantChart = new Chart(ctx2, {
                        type: 'bar',
                        data: { labels: barLabels, datasets: barData },
                        options: {
                            responsive: true,
                            animation: { duration: 1000, easing: 'easeOutQuart' },
                            interaction: { mode: 'index', intersect: false },
                            scales: { y: { beginAtZero: true } }
                        }
                    });
                    new bootstrap.Modal(document.getElementById('compareModal')).show();
                });
        });
    }

    socket.on('update', data => {
        renderCityCard(data.city, data); // updated to OpenAQ v3
        fetchCoords(data.city, data.value);
    });

    function initMarkers() {
        fetch('/api/all_coords')
            .then(r => r.json())
            .then(coordMap => {
                [...cities, ...searchedCities].forEach(city => {
                    const coords = coordMap[city];
                    if (coords && !markers[city]) {
                        markers[city] = L.circleMarker([coords[0], coords[1]], {color: markerColor(null)}).addTo(map).bindPopup(`${city} AQI: N/A`);
                        markers[city].on('click', () => openDetail(city));
                    }
                });
            });
    }

    function fetchCoords(city, aqi) {
        fetch(`/api/coords/${encodeURIComponent(city)}`)
            .then(r => r.json())
            .then(coords => {
                if (coords.error) return;
                if (markers[city]) {
                    markers[city].setLatLng([coords.lat, coords.lon]);
                    markers[city].setStyle({color: markerColor(aqi)}).bindPopup(`${city} AQI: ${aqi}`);
                } else {
                    markers[city] = L.circleMarker([coords.lat, coords.lon], {color: markerColor(aqi)}).addTo(map).bindPopup(`${city} AQI: ${aqi}`);
                    markers[city].on('click', () => openDetail(city));
                }
            });
    }

    initMarkers();
    cities.forEach(city => {
        fetchCoords(city, null);
        fetchCityData(city, false);
        setInterval(() => fetchCityData(city), 1800000);
    });
});
