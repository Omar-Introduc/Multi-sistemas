// Manejo de gráficos
const Charts = {
  // Gráfico de balance
  createBalanceChart: (canvasId) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        datasets: [{
          label: 'Balance',
          data: [20000, 22000, 21000, 23000, 25000, 25430],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        }
      }
    });
  },

  // Gráfico de transacciones por categoría
  createTransactionChart: (canvasId) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Alimentación', 'Transporte', 'Servicios', 'Otros'],
        datasets: [{
          data: [45, 25, 20, 10],
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }
};

// Exportar para uso global
window.Charts = Charts;
