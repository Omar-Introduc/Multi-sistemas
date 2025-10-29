const amqp = require('amqplib/callback_api');

const RABBITMQ_HOST = process.env.RABBITMQ_HOST || 'amqp://localhost';

function sendMessage(queue, msg) {
  amqp.connect(RABBITMQ_HOST, function(error0, connection) {
    if (error0) {
      throw error0;
    }
    connection.createChannel(function(error1, channel) {
      if (error1) {
        throw error1;
      }
      channel.assertQueue(queue, {
        durable: false
      });
      channel.sendToQueue(queue, Buffer.from(msg));
      console.log(" [x] Sent %s", msg);
    });
    setTimeout(function() {
      connection.close();
    }, 500);
  });
}

module.exports = {
  sendMessage
};
