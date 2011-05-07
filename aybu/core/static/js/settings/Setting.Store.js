/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('settings')


settings.SettingsStore = Ext.extend(settings.BaseStore, {
	constructor: function(config){
		if(!config){
			config = {};
		}
		settings.SettingsStore.superclass.constructor.call(this,
			Ext.apply(config, {
				proxy : new Ext.data.HttpProxy({
					api: {
						create : { url: urls.create, method: "POST" },
						update : { url: urls.update, method: "POST"},
						destroy : { url: urls.destroy, method: "POST"},
						read : { url: urls.list, method: "GET" }
					}
				})
			})
		);
		this.pageSize = 30;
		this.addListener('write', this.write_handler, this);
		this.addListener('save', this.save_handler, this);
	},
	write_handler : function(store, action, records, options, arg) {
		if(action == 'update'){
			window.location.reload(true);
		}
	},
	save_handler : function(store, bacth, data) {
		Ext.MessageBox.hide();
		window.location.reload(true);
	}

});
