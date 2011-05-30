/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

var uploader = new Ext.ux.PluploadButton({
	text: 'Cambia Immagine',
    iconCls: 'silk-add',
    window_width: 380,
    window_height: 300,
    clearOnClose: true,
    window_title: 'Aggiungi immagine',
    upload_config: {

		url: c.urls.page_banners,
		//runtimes: 'gears,flash,silverlight,html5,browserplus,html4',
		runtimes: 'html5, html4, flash',

		multiSelect: false,
		multipart: true,

		multipart_params: {
			nodeinfo_id : c.translation.id
		},

		max_file_size: '1mb',

		//flash_swf_url : '/static/aybu/js/lib/plupload/plupload.flash.swf',
		//silverlight_xap_url : '/static/aybu/js/lib/plupload/plupload.silverlight.xap',

		filters: [  {title : "Image files", extensions : "jpg,JPG,gif,GIF,png,PNG"} ],

		runtime_visible: false,

		addButtonCls: 'silk-add',
		uploadButtonCls: 'silk-arrow-up',
		cancelButtonCls: 'silk-stop',
		deleteButtonCls: 'silk-cross',

		addButtonText: 'Aggiungi',
		uploadButtonText: 'Upload',
		cancelButtonText: 'Termina upload',
		deleteButtonText: 'Rimuovi dalla coda',
		deleteSelectedText: '<b>selezionati</b>',
		deleteUploadedText: 'caricati',
		deleteAllText: 'tutti',

		statusQueuedText: 'In coda',
		statusUploadingText: 'Uploading ({0}%)',
		statusFailedText: '<span style="color: red">Fallito</span>',
		statusDoneText: '<span style="color: green">Ok</span>',

		statusInvalidSizeText: 'Le dimensioni del file sono oltre il massimo consentito',
		statusInvalidExtensionText: 'Tipo di file non valido',

		emptyText: '<div class="plupload_emptytext"><span>Coda vuota</span></div>',
		emptyDropText: '<div class="plupload_emptytext"><span>Trascina i file qui</span></div>',

		progressText: '{0}/{1} ({3} falliti) ({5}/s)',

		listeners: {
			uploadcomplete: function(uploadpanel, success, failures) {
				if(success.length) {
					window.location.reload(true);
				}

			}
    	}
  }
});


var remove_button = new Ext.Button({
	text: 'Rimuovi Immagine',
	handler: function() {
		Ext.Ajax.request({
			url: c.urls.remove_page_banners,
			params: {
				nodeinfo_id : c.translation.id
			},
			success: function(response){
				if(response.responseText.contains('true')){
					window.location.reload(true);
				}
			}
		});
	}
})

function banner() {
	try {
		$(banner_selector).prepend('<div id="upload"></div>');
		$('#upload').prepend('<div style="float:none; clear:both; width: 0px; height:0px;"></div>');
		$('#upload').prepend('<div id="remove_button" style="float:left;"></div>');
		$('#upload').prepend('<div id="add_button" style="float:left; margin-right:5px;"></div>');

	}
	catch(err) {
		return;
	}

	var p = $(banner_selector).position();

	$('#upload').css('position', 'fixed');
	$('#upload').css('top', p.top);
	$('#upload').css('left', p.left);

	uploader.render('add_button');
	uploader.hide();

	remove_button.render('remove_button');
	remove_button.hide();


	$(banner_selector).mouseenter(function() {
		$(banner_selector).css('opacity', '0.5');
		uploader.show();
		remove_button.show();
	});
	$(banner_selector).mouseleave(function() {
		$(banner_selector).css('opacity', '1');
		uploader.hide();
		remove_button.hide();
	});

}
