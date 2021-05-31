export function prepareSocket() {
  var socket = io.connect(
    window.location.protocol + '//' + document.domain + ':' + location.port
  )
  var prefix = 'https://laptop88.vn/'
  socket.on('connect', function () {
    socket.emit('connected', {
      data: 'User Connected',
      session_id: socket.id,
    })
    $('#send_icon').click('submit', function (e) {
      e.preventDefault()
      let message = $('input#message').val()
      if (message)
        socket.emit('my event', {
          message,
          session_id: socket.id,
        })
      $('input#message').val('').focus()
    })
  })
  socket.on('my response', function (msg) {
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
      if (!msg.response[1] && !msg.response[2])
        $('#messages_display').append(`
        <div class="message message_AI">
          <div class="message_content">${msg.response[0]}</div>
          <div class="message_time">${msg.time}</div>
        </div>
    `)
      else {
        $('#messages_display').append(`
            <div class="message message_AI">
              <div class="message_content">${msg.response[0]}: </br>
              </div>
              <div class="message_time">${msg.time}</div>
              </div>
              `)
        msg.response[1].forEach(function (res, i) {
          $('#messages_display .message_AI .message_content').append(
            `<a href='${
              prefix + msg.response[2][i]
            }' target='_blank'>- ${res}</a> </br>`
          )
        })
      }
    }
    scrollToEnd()
  })
  $('.question_content').click(function (e) {
    if ($(this).text())
      socket.emit('my event', {
        message: $(this).text(),
        session_id: socket.id,
      })
    $('input#message').val('').focus()
  })
}

function scrollToEnd() {
  var scr = document.getElementById('messages_display')
  scr.scrollTop = scr.scrollHeight
}
