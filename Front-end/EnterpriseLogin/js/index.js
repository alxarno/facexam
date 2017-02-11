
// Toggle Function
$('.toggle').click(function(){
  // Switches the Icon
  $(this).children('i').toggleClass('fa-pencil');
  // Switches the forms  
  $('.form').animate({
    height: "toggle",
    'padding-top': 'toggle',
    'padding-bottom': 'toggle',
    opacity: "toggle"
  }, "slow");
    $('.tooltip').animate({
    opacity: "toggle"
  }, "slow");
});

$('#enter').click(function(){
      $.getJSON('/api/enter', {
            login: $('#loginEnter').val(),
            pass: $('#passEnter').val()
          }, function(data) {
              console.log(data.result)
        	}
 
		)
  	}
  )

$('#registr').click(function(){
      $.getJSON('/api/registr', {
            login: $('#regLogin').val(),
            pass: $('#regPass').val(),
            email: $('#regEmail').val()
          }, function(data) {
              console.log(data.result)
        	}
 
		)
  	}
  )
