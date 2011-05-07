/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.BLANK_IMAGE_URL = "/static/aybu/js/lib/extjs/resources/images/default/s.gif";

Ext.ns('imgmanager');

Ext.onReady(function() {
	Ext.QuickTips.init();
	imgmanager.image_store.load();
	imgmanager.image_panel.render('extjs-main-panel-div');
});

imgmanager.select_image = function () {
	dv = imgmanager.dataview;
	record = dv.getSelectedRecords()[0];
	if (tinyMCE != undefined) {
		var win = tinyMCEPopup.getWindowArg("win");
		var input = tinyMCEPopup.getWindowArg("input");
		var url = record.data.url;
		win.document.getElementById(input).value = url
		// are we an image browser
		if (typeof(win.ImageDialog) != "undefined") {
			// we are, so update image dimensions...
			if (win.ImageDialog.getImageData)
				win.ImageDialog.getImageData();

			// ... and preview if necessary
			if (win.ImageDialog.showPreviewImage)
				win.ImageDialog.showPreviewImage(url);
		}
		tinyMCEPopup.close();
	}
}
