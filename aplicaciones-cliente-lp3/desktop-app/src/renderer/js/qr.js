// Funciones para manejo de QR
const QRManager = {
  // Generar código QR
  generateQR: (data, canvasId) => {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    QRCode.toCanvas(canvas, JSON.stringify(data), {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    }, (error) => {
      if (error) console.error('Error generando QR:', error);
    });
  },

  // Escanear código QR usando cámara
  startScanner: (videoId, callback) => {
    const video = document.getElementById(videoId);
    if (!video) return;

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      .then(stream => {
        video.srcObject = stream;
        video.play();
        
        // Simular detección de QR
        setTimeout(() => {
          callback({
            type: 'payment',
            amount: 100,
            description: 'Pago de prueba',
            merchant: 'Banco LP3'
          });
          QRManager.stopScanner(videoId);
        }, 3000);
      })
      .catch(err => {
        console.error('Error accediendo a la cámara:', err);
        alert('No se pudo acceder a la cámara');
      });
  },

  // Detener scanner
  stopScanner: (videoId) => {
    const video = document.getElementById(videoId);
    if (video && video.srcObject) {
      const stream = video.srcObject;
      stream.getTracks().forEach(track => track.stop());
      video.srcObject = null;
    }
  },

  // Validar datos QR
  validateQRData: (data) => {
    try {
      const parsed = typeof data === 'string' ? JSON.parse(data) : data;
      return parsed && parsed.type === 'payment' && parsed.amount && parsed.description;
    } catch {
      return false;
    }
  }
};

// Exportar para uso global
window.QRManager = QRManager;
