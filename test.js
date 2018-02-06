// with ES6 import
var io = require('socket.io-client')

const socket = io('http://localhost:3000');
socket.on('connect', function(){
    console.log('connected');
});
socket.emit('chat message', 'test');
socket.emit('chat message', 'test');
socket.on('event', function(data){});
socket.on('disconnect', function(){});
