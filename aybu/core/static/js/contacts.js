/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */


jQuery.extend(jQuery.validator.messages, {
	sender_name : "Digits or special character are not valid.",
	phone : "Please insert a valid phone number."
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
	jQuery.validator.addMethod("sender_name", function(value, element) {
		var user = /[(0-9\@\*\(\)\[\]\+\.\,\/\?\:\;\"\`\~\\#\$\%\^\&\<\>)+]/;
		if (!value.match(user)) {
			return true;
		} else {
			return false;
		}
	}, jQuery.validator.messages.sender_name);

	jQuery.validator.addMethod("phone", function(value, element) {
		var phone = /^(\+){0,1}([0-9-()]|( ))+$/;
		if (value.match(phone)) {
			return true;
		} else {
			return false;
		}
	}, jQuery.validator.messages.phone);
}



$(document).ready(function() {
	add_validator();
	$('#form').validate({
		submitHandler: onSubmit,
		invalidHandler: onInvalid,
		highlight: highlight_elements,
		rules : {
			name: {
				required: true,
				sender_name: true,
				minlength: 2
		    },
			surname: {
				required: true,
				sender_name: true,
				minlength: 2
		    },
		    phone: {
		    	required: true,
		    	phone: true
		    },
		    message: {
				required: true,
				minlength: 10
		   	},
		    email: {
				required: true,
				email: true
		   	},
		    agreement: {
				required: true
		    },
			captcha: {
				required: true
		    }
		}
	});
});
