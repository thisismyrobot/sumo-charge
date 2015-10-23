$(document).ready(function(){

    var fps = 10;
    var req_timer = setInterval(function(){}, 1000);

    var socket = io.connect(
        '//' + document.domain + ':' + location.port + '/video'
    );

    socket.on('connect', function() {

        socket.on('frame', function (frame) {
            $('#video').attr(
                'src',
                'data:image/jpg;base64,' + frame.data
            );
        });

        clearInterval(req_timer);
        req_timer = setInterval(function() {
            socket.emit('request_frame');
        }, 1000 / fps);
    });

});
