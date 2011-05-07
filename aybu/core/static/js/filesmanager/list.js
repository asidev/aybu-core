/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('filesmanager')

function filter_list(search_text) {
	search_field.enable();
	filesmanager.fileslist.store.filter('name', search_text, true, false);
}

filesmanager.fileslist = new Ext.list.ListView({
	store : filesmanager.files_store,
	multiSelect: true,
	reserveScrollOffset: true,
	emptyText: "Nessun file",
	columns : [{
		header : "Nome",
		dataIndex : "name",
		width: .5
	},{
		header: 'URL',
		width: .35,
		dataIndex: 'url'
	},{
		header: 'Dimensione',
		dataIndex: 'size',
		tpl: '{size:fileSize}',
		align: 'right'
    }],
	listeners: {
		selectionchange : function (db, selections) {
			if (selections.length) {
				if (selections.length == 1)
					filesmanager.file_panel.getTopToolbar().getComponent('select').setDisabled(false);
				else
					filesmanager.file_panel.getTopToolbar().getComponent('select').setDisabled(true);
				filesmanager.file_panel.getTopToolbar().getComponent('delete').setDisabled(false);
			} else {
				filesmanager.file_panel.getTopToolbar().getComponent('select').setDisabled(true);
				filesmanager.file_panel.getTopToolbar().getComponent('delete').setDisabled(true);
			}
	   },
	   dblclick : function (dv, idx, node, evtObj) {
			filesmanager.select_file();
	   }
	}
});
