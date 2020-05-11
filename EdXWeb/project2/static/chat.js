document.addEventListener('DOMContentLoaded', () => {

    alert("hello from chat js");
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit vote" event
        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {
                alert('Button clicked');
                const chatname = document.querySelector('#chatname').value;
                socket.emit('create chat', {'chatname': chatname});
            };
        });
    });

    // When a new vote is announced, add to the unordered list
    socket.on('chat created', data => {
        const litest = document.createElement('li');
        litest.innerHTML = "We got here";
        document.querySelector('#chats').append(litest);

        const li = document.createElement('li');
        li.innerHTML = `New Chat added: ${data.chatname}`;
        document.querySelector('#chats').append(li);
    });
});
