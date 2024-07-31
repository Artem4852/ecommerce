function makeGraph(id, dict, type) {
    const ctx = document.getElementById(id).getContext('2d');
    const labels = Object.keys(dict);
    const data = Object.values(dict);

    new Chart(ctx, {
        type: type,
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
            tooltip: {
                enabled: false
            },
            cutout: '0%',
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: type === 'bar'
                    },
                    display: type === 'bar'
                },
                x: {
                    grid: {
                        display: type === 'bar'
                    },
                    display: type === 'bar'
                }
            }
        }
    });
}

// const dailyUniqueVisits = {{ dailyUniqueVisits | tojson }};
// const hourlyRequests = {{ hourlyRequests | tojson }};
// const utmSources = {{ utmSources | tojson }};
// const pageDistribution = {{ pageDistribution | tojson }};
// const regionDistribution = {{ regionDistribution | tojson }};
// const cityDistribution = {{ cityDistribution | tojson }};

// console.log(utmSources);

document.addEventListener('DOMContentLoaded', (event) => {
    makeGraph('requestsChart', dailyRequests, 'bar');
    makeGraph('uniqueVisitsChart', dailyUniqueVisits, 'bar');
    makeGraph('hourlyRequestsChart', hourlyRequests, 'bar');
    makeGraph('utmSourcesChart', utmSources, 'doughnut');
    makeGraph('pageDistributionChart', pageDistribution, 'doughnut');
    makeGraph('regionDistributionChart', regionDistribution, 'doughnut');
    makeGraph('cityDistributionChart', cityDistribution, 'doughnut');
});