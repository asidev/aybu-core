/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

msgbox_visible = false;

function validation_end(data, textStatus, xhr) {
	if (data.html.num_errors == 0 && data.links.broken.length == 0) {
		color = "#cfc";
		$('#top_message_box').css("background", "#cfc");
		message = "Page is valid HTML. No broken links";
	}
	else {
		message = "Page is " + data.html.status;
		if (data.html.num_errors > 0) {
			message += "<p>Errors:<ol>";
			for (i=0; i< data.html.num_errors; i++) {
				error = data.html.errors[i];
				message += "<li> Error at line " + error.line +" col " + error.col + " message: '"+ error.message + "' source: "+ error.source + "</li>";
			}
			message += "</ol></p>"
		}
		if (data.links.broken.length > 0) {
			message += "<p>Broken Links:<ol>";
			for (i=0; i < data.links.broken.length; i++) {
				link = data.links.broken[i];
				message += "<li>" + link + "</li>";
			}
		}
	}
	show_msgbox(message);
}

function show_msgbox(message) {
	$('#top_message_box_content').html(message);
	$('#top_message_box').animate({ top:"+=3px",opacity:100 }, "slow")
	msgbox_visible = true;
}

function hide_msgbox() {
	$('#top_message_box_content').html(" ");
	$('#top_message_box').animate({ top:"+=15px",opacity:0 }, "slow")
	msgbox_visible = false;
}

function validate() {
	show_msgbox("<p>Validating page and links</p>");
	$.ajax({
		url : "/validate.html",
		success : validation_end,
		async : true,
		dataType : "json",
		data: {
			url: $(location).attr("href")
		}
	});
}

$(document).ready(function() {
	$(window).scroll(function()	{
		if (msgbox_visible)
			$('#top_message_box').animate({top:$(window).scrollTop()+"px" },{queue: false, duration: 350});
	});
	$('#close_top_message_box').click(hide_msgbox);
	setTimeout("validate()", 3000);
	// validate();
});
