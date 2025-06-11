document.addEventListener("DOMContentLoaded", () => {
    const allData = JSON.parse(document.getElementById('data-json').textContent);

    const chartConfigs = {
        luminosite: {
            label: "Taux de luminosité",
            field: "taux_luminosite",
            type: "line"
        },
        presence: {
            label: "Présence détectée",
            field: "presence_detected",
            type: "bar"
        },
        intensite: {
            label: ["Puissance", "Courant"],
            fields: ["puissance", "courant"],
            type: "line"
        }
    };

    Object.keys(chartConfigs).forEach(table => {
        const config = chartConfigs[table];
        const data = allData[table].json;
        const labels = data.map(row => row.timestamp);

        let datasets = [];

        if (Array.isArray(config.fields)) {
            config.fields.forEach((field, index) => {
                const color = index === 0 ? 'rgba(255, 206, 86, 1)' : 'rgba(54, 162, 235, 1)';
                const bgColor = index === 0 ? 'rgba(255, 206, 86, 0.2)' : 'rgba(54, 162, 235, 0.2)';
                datasets.push({
                    label: config.label[index],
                    data: data.map(row => row[field]),
                    backgroundColor: bgColor,
                    borderColor: color,
                    fill: false,
                    tension: 0.3
                });
            });
        } else {
            datasets.push({
                label: config.label,
                data: data.map(row => row[config.field]),
                backgroundColor: config.type === 'bar' ? 'rgba(75, 192, 192, 0.6)' : 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                fill: config.type === 'line',
                tension: 0.3
            });
        }

        new Chart(document.getElementById(`${table}Chart`).getContext('2d'), {
            type: config.type,
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });
});
