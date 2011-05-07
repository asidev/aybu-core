/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

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

$(document).ready(function() {
	$('#banner_logo').validate({
		submitHandler: onSubmit,
		invalidHandler: onInvalid,
		highlight: highlight_elements,
		rules : {
			banner_image: {
				accept : true
		    },
			logo_image: {
				accept : true
		    }
		}
	});
});
