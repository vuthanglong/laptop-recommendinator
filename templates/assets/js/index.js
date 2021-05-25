import { prepareSocket } from './socket.js'

const hintQuestions = [
  'Hi em!',
  'Em ăn cơm chưa?',
  'Ngủ sớm vậy em?',
  'Anh rất chào em!',
  'Em muốn ăn gì nhỉ?',
  'Em ăn tối trưa?',
  'Em muốn chúng mình đi đâu?',
  'Em ơi xong chưa?',
  '"Cô ấy luôn luôn đúng và bạn là người sai."',
]

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
  hintQuestions.forEach(function (e) {
    $('.questions_container').append(`
      <div class="question_container">
        <div class="question_content">${e}</div>
      </div>
  `)
  })

  $('#question_selection_button').click(function () {
    if ($('#modal').css('display') == 'none') {
      setTimeout(() => {
        $('#modal').css('display', 'block')
        $('.input').css('border-radius', '0 0 25px 25px')
      }, 50)
    } else {
      setTimeout(() => {
        $('#modal').css('display', 'none')
        $('.input').css('border-radius', '25px')
      }, 50)
    }
  })

  //
  function closeQuestionSelection() {
    if ($('#modal').css('display') == 'block') {
      setTimeout(() => {
        $('#modal').css('display', 'none')
        $('.input').css('border-radius', '25px')
      }, 50)
    }
  }

  $('.question_content').click(function () {
    closeQuestionSelection()
  })

  $('#overlay').click(function () {
    //close modal
    setTimeout(() => {
      $('#overlay').css('display', 'none')
      $('#modal-info').css('display', 'none')
      if ($('#overlay').css('z-index') == '100') {
        $('#overlay').css('z-index', '50')
      }
    }, 50)
  })

  $('#info-btn').click(function () {
    setTimeout(() => {
      $('#modal').css('display', 'none')
      $('.input').css('border-radius', '25px')
      $('#modal-info').css('display', 'block')
      $('#overlay').css('display', 'block')
      $('#overlay').css('z-index', '100')
      $('#modal-info').addClass('bottomToCenterAnimation')
    }, 50)
  })
  prepareSocket()
})
