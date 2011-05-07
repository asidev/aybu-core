/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('settings')

Ext.util.Format.comboRenderer = function(combo){
    return function(value){
        var record = combo.findRecord(combo.valueField, value);
        return record ? record.get(combo.displayField) : combo.valueNotFoundText;
    }
}


settings.SettingTypeStore = Ext.extend(settings.BaseStore, {
	constructor: function(config) {
		if(!config){
			config = {};
		}
		settings.SettingTypeStore.superclass.constructor.call(this, Ext.apply(config, {
			proxy : new Ext.data.HttpProxy({
				api: {
					read : { url: urls.types, method: "GET" }
				}
			})
		}));
	}
});

settings.settings_type_store = new settings.SettingTypeStore({
	storeId : "SettingTypeStore",
	baseParams : {search : true, meta : 1}
});

settings.settings_type_store.load();

settings.SettingTypeCombo = Ext.extend(Ext.form.ComboBox, {
	initComponent: function() {
		var config = {
			typeAhead: true,
			//hideTrigger:true,
			mode : 'remote',
            triggerAction: 'all',
            editable: false,
			hiddenName: 'setting_type_name',
            emptyText : "Seleziona il tipo di impostazione",
			fieldLabel: "Tipo",
            lazyInit: false,
			store : settings.settings_type_store,
			valueField: "name",
			queryParam: "name",
			displayField: "name",
			loadingText: "Cerco...",
			forceSelection: true
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		settings.SettingTypeCombo.superclass.initComponent.call(this);
	}
});

//var SettingTypeCombo = new settings.SettingTypeCombo();
