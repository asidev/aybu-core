/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

function files_filebrowser_callback(field_name, url, win) {
	tinyMCE.activeEditor.windowManager.open({
		title: "Seleziona un file",
		file: c.urls.files.index,
		width: 600,
		height: 400,
		resizable : true,
		maximizable: true,
		inline : true,
		popup_css : false,
		translate_i18n : false,
		close_previous : true,
		scrollbars: true
	}, {
		win : win,
		input: field_name
	});
	return true;
}
