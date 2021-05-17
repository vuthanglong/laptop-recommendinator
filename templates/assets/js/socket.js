export function prepareSocket() {
  var socket = io.connect(
    window.location.protocol + '//' + document.domain + ':' + location.port
  )

  socket.on('connect', function () {
    socket.emit('connected', {
      data: 'User Connected',
      session_id: socket.id,
    })
    $('form').click('submit', function (e) {
      e.preventDefault()
      let message = $('input#message').val()
      console.log($('input#message').val())
      if (message)
        socket.emit('my event', {
          message,
          session_id: socket.id,
        })
      $('input#message').val('').focus()
    })
  })
  socket.on('my response', function (msg) {
    console.log(msg)
    if (typeof msg.message !== 'undefined') {
      $('#messages_display').append(`
        <div class="message message_client">
          <div class="message_content">${msg.message}</div>
          <div class="message_time">${msg.time}</div>
        </div>
    `)
    }
    scrollToEnd()
  })
  socket.on('bot response', function (msg) {
    if (typeof msg.response !== 'undefined') {
      $('#messages_display').append(`
        <div class="message message_AI">
          <div class="message_content">${msg.response}</div>
          <div class="message_time">${msg.time}</div>
        </div>
    `)
    }
    scrollToEnd()
  })
}

function scrollToEnd() {
  var scr = document.getElementById('messages_display')
  scr.scrollTop = scr.scrollHeight
}
