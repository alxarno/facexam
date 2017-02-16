
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
             if(data.result == 'Error'){
             	  $(".ErrorMessageEnter").animate({
             	  	opacity: 0.8
             	  }, 'slow')
             }else{
             	$(".ErrorMessageEnter").animate({
             	  	opacity: 0
             	  }, 'slow')
             	window.location.replace('http://'+window.location.hostname+':'+window.location.port+data.result)
             }
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
