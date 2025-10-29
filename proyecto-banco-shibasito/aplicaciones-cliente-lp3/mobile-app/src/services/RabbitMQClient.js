// This would use a mobile-friendly AMQP library
// For example, react-native-amqp
// Since we don't have it, this is a placeholder
const RabbitMQClient = {
  sendMessage: (queue, message) => {
    console.log(`Sending message to ${queue}: ${message}`);
  }
};

export default RabbitMQClient;
