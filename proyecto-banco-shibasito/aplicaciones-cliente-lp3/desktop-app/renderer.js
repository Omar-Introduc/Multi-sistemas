const { sendMessage } = require('./src/services/RabbitMQClient');

document.getElementById('send-btn').addEventListener('click', () => {
  const message = 'Test Loan Application from Desktop';
  sendMessage('solicitud_prestamo', message);
});
