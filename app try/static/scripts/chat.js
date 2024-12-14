document.addEventListener('DOMContentLoaded', function () {
    // Now the DOM is loaded, so you can safely access elements
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // Listen for incoming messages and update the chat window
    socket.on('receive_message', function(data) {
        let messageContainer = document.getElementById('messages');
        let messageElement = document.createElement('div');
        messageElement.textContent = `${data.sender}: ${data.message} (${data.timestamp})`;
        messageContainer.appendChild(messageElement);
    });

    // Handle sending a message when the user clicks the send button
    document.getElementById('sendButton').addEventListener('click', function() {
        let message = document.getElementById('messageInput').value;
        let timestamp = new Date().toISOString();
        let username = 'User123';  // This should be dynamic based on the logged-in user

        // Check if the input message is empty
        if (message.trim() === '') {
            alert('Please enter a message.');
            return; // Stop the function if the message is empty
        }

        // Emit the message to the server via Socket.IO
        socket.emit('send_message', {
            message: message,
            timestamp: timestamp,
            username: username
        });

        // Clear the input field after sending the message
        document.getElementById('messageInput').value = '';
    });
});
