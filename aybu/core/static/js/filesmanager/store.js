/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('filesmanager')

Ext.Ajax.on("requestexception", function() {
	Ext.Msg.alert("Errore di comunicazione",
		"Si è verificato un errore nel contattare il server.\n" +
		"Si consiglia di provare nuovamente. Se il problema persiste si prega di contattare l'assistenza.");
});

filesmanager.files_store = new Ext.data.JsonStore({
	url : urls.list,
	root : 'data',
	storeId: 'filestore',
	successProperty: 'success',
	totalProperty: 'datalen',
	idProperty: 'id',
	fields : [{name: 'id', type: 'int' },'name', 'url', 'size', 'used_by'],
	sortInfo : { field: "name", direction: "ASC"},
	listeners : {
		remove : function (store, record, idx) {
			Ext.Ajax.request({
				url: urls.remove,
				params: { id : record.get("id") },
				failure : function () {}
			});
		}
	}
});
