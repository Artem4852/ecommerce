const labels = Object.keys(dailyRequests);
const data = Object.values(dailyRequests);

document.addEventListener('DOMContentLoaded', (event) => {
        const ctx = document.getElementById('requestsChart').getContext('2d');
        const labels = Object.keys(dailyRequests);
        const data = Object.values(dailyRequests);

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '',
                    data: data,
                    borderColor: 'rgba(227, 82, 186, 0.4)',
                    backgroundColor: 'rgba(227, 82, 186, 0.4)',
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });