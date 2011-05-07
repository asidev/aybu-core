/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

var content_old_html = "";
var content_tinymce = null;

function content_reset() {
	$('#content_edit').after("<div id='editable_content'>" + content_old_html + "</div>").remove();
	$('#edit_button').show();
}

function content_on_save_success() {
	if (content_tinymce) {
		content_tinymce.setProgressState(0);
		content_old_html = content_tinymce.getContent();
		content_reset();
	}
}

function content_on_save_error(obj, msg, excp) {
	// fixme print error message
	content_tinymce.setProgressState(0);
	alert("Si sono verificati degli errori durante il salvataggio dei dati");
}

function content_on_init_tinymce() {
	$.unblockUI();
	$('#edit_area_parent').show();
}

function content_save_changes(obj) {
	content_tinymce = obj;
	content_tinymce.setProgressState(1);
	var editor = $('#edit_area');
	var html = editor.tinymce().getContent();
	$.ajax({
		cache: false,
		data : {
			translation_id: c.translation.id,
			translation_lang : c.lang,
			translation_country: c.country,
			translation_html : html
		},
		dataType : "json",
		error : content_on_save_error,
		success: content_on_save_success,
		type: "POST",
		url: c.urls.edit
	});
	return false;
}

function content_start_edit(obj) {
	/* callback for the "save button" of tinyMCE */
	block_ui("Caricamento....");
	var content_div = $('#editable_content');
	var revert = content_div.html();//.trim();
	var textarea = '<div id="content_edit"><textarea spellcheck="false" class="admin_control" id="edit_area">' + revert + '</textarea>';
	content_div.after(textarea).remove();
	$('#edit_button').hide();
	$('#edit_area').hide();
	content_old_html = revert;
	tinymce_show('#edit_area', content_on_init_tinymce, content_save_changes, content_reset);
	//fix_content_height();
}

function content_main() {
	var content_div = $('#editable_content');
	if (content_div.length == 0) {
		//console.log('editable_content lenght = 0');
		return;
	}
	$("#content").prepend('<div id="admin_controls" class="admin_control"><input class="admin_control" type="button" value="Edit" id="edit_button" /></div>');
	$("#edit_button").click(content_start_edit);
}
