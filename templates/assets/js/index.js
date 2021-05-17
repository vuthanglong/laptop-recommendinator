$(document).ready(function () {
  var mode = true
  $('#adjust_icon').click(function () {
    if (mode == true) {
      setTimeout(() => {
        document.documentElement.setAttribute('data-theme', 'dark')
      }, 50)
      mode = false
    } else {
      setTimeout(() => {
        document.documentElement.setAttribute('data-theme', 'light')
      }, 50)
      mode = true
    }
  })

  function scrollToEnd(){
    var scr = document.getElementById("messages_display");
    scr.scrollTop = scr.scrollHeight;
  }

  $("#question_selection_button").click(function() {
    if( $('#modal').css('display') == 'none' ) {
      setTimeout(() => {
        $("#modal").css('display' , 'block');
        $(".input").css('border-radius', '0 0 25px 25px')
      }, 50)
    }
    else {
      setTimeout(() => {
        $("#modal").css('display' , 'none');
        $(".input").css('border-radius', '25px')
      }, 50)
    }
  })

//
  function closeQuestionSelection(){
    if( $('#modal').css('display') == 'block' ) {
      setTimeout(() => {
        $("#modal").css('display' , 'none');
        $(".input").css('border-radius', '25px')
      }, 50)
    }
  }

  $("#overlay").click(function(){
    //close modal
    setTimeout(() => {
      $("#overlay").css('display' , 'none');
      $("#modal-info").css('display' , 'none');
      if($('#overlay').css('z-index') == '100') {
        $("#overlay").css('z-index' , '50');
      }
    }, 50)
  })

  $("#info-btn").click(function(){
    setTimeout(() => {
      $("#modal").css('display' , 'none');
      $(".input").css('border-radius', '25px')
      $("#modal-info").css('display' , 'block');
      $("#overlay").css('display' , 'block');
      $("#overlay").css('z-index' , '100');
      $("#modal-info").addClass('bottomToCenterAnimation')
    }, 50)
  })

  var socket = io.connect(
    window.location.protocol + '//' + document.domain + ':' + location.port
  )

  socket.on('connect', function () {
    socket.emit('connected', {
      data: 'User Connected',
    })
    var form = $('form').click('submit', function (e) {
      e.preventDefault()
      let message = $('input#message').val()
      console.log($('input#message').val())
      if (message)
        socket.emit('my event', {
          message,
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
})

