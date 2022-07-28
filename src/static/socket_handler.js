let connection_error = false;

const socket = io();

socket.on('connect', function(){
    connection_error = false;
})

socket.on('connect_error', function(){
    connection_error = true;
})


function fetch_frame(frame_num){
    socket.emit('get_frame', {'game_id': game_id, 'frame_num': frame_num});
}

socket.on('frame', function(data){
    frameReceived(data);
})


function fetch_game_info(){
    socket.emit('get_game_info', {'game_id': game_id});
}

socket.on('game_info', function(data){
    gameInfoReceived(data);
})
