/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('TreeManager');

TreeManager.BaseStore = Ext.extend(Ext.data.JsonStore, {
	constructor: function(config){
		if(!config){
			config = {};
		}
		TreeManager.BaseStore.superclass.constructor.call(this,
			Ext.apply(config,
				{
					writer : new Ext.data.JsonWriter({
						encode : true,
						listful : true,
						writeAllFields: true
					}),
					autoSave: false,
					remoteSort : true
				}
			)
		);
		this.addListener('exception', this.exception_handler, this);
		this.addListener('update', this.update_handler, this);
		this.addListener('save', this.save_handler, this);
		this.reload_after_write = false;
	},
	defaultLoad : function(opts){
		var params = {start:0, meta:1};
		if(this.pageSize){
			params.limit = this.pageSize;
		}
		this.defaultOpts = {params:params};
		Ext.apply(this.defaultOpts, opts);
		this.load(this.defaultOpts);
	},
	exception_handler : function(proxy, type, action, options, res){
		if(type === 'remote'){
			Ext.Msg.show({
				title: 'Richiesta Fallita',
				msg: "Risposta del server : " + res.raw.message,
				icon: Ext.MessageBox.ERROR,
				buttons: Ext.Msg.OK
			});
		} else if(type == "response" ){
			Ext.Msg.show({
				title: 'REMOTE EXCEPTION',
				msg: "Internal Server Error (" + res.status + "): " + res.responseText,
				icon: Ext.MessageBox.ERROR,
				buttons: Ext.Msg.OK
			});
		}
		this.rejectChanges();
		/*
		this.reload();
		this.reload_after_write = false;
		*/
	},
	update_handler : function(store, record, operation){
		if(operation == Ext.data.Record.EDIT){
			this.save();
		}
	},
	save_handler : function(store, batch, data) {
		if(Ext.Msg.isVisible()){
			Ext.Msg.hide();
		}
		if(this.reload_after_write == true){
			this.reload();
			this.reload_after_write = false;
		}
	}
});
