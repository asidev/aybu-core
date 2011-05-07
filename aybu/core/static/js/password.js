/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

jQuery.extend(jQuery.validator.messages, {
	passwords_differ : "Passwords differ."
});

function onSubmit(form) {
	form.submit();
}


function highlight_elements(element, errorClass) {
	/*
    $(element).fadeOut(function() {
      $(element).fadeIn()
    })
	*/
}

function onInvalid(form, validator) {
  /*
  $(document).find("input.error").each(function () {
		alert($(this).offset().top);
  });
  */
}

function add_validator() {
	jQuery.validator.addMethod("pw_confim", function(value, element) {
		var v = $('#new_password').val();
		if(value != v){
			return false;
		}
		return true;
	}, jQuery.validator.messages.passwords_differ);
}

$(document).ready(function() {

	add_validator();

	$('#password').validate({
		submitHandler: onSubmit,
		invalidHandler: onInvalid,
		highlight: highlight_elements,
		rules : {
			old_password: {
				required : true
		    },
			new_password: {
				required : true,
		    	minlength : 6,
		    	maxlength : 16
		    },
			repeat_password: {
				required : true,
				pw_confim : true
		    }
		}
	});
});
