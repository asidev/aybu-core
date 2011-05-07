/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.BLANK_IMAGE_URL = "/static/aybu/js/lib/extjs/resources/images/default/s.gif";

Ext.ns('filesmanager');

Ext.onReady(function() {
	Ext.QuickTips.init();
	filesmanager.files_store.load();
	filesmanager.file_panel.render('extjs-main-panel-div');
});

filesmanager.select_file = function () {
	list = filesmanager.fileslist;
	record = list.getSelectedRecords()[0];
	if (tinyMCE != undefined) {
		var win = tinyMCEPopup.getWindowArg("win");
		var input = tinyMCEPopup.getWindowArg("input");
		var url = record.data.url;
		win.document.getElementById(input).value = url
		tinyMCEPopup.close();
	}
}
