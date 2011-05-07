/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('TreeManager')

Ext.util.Format.comboRenderer = function(combo){
    return function(value){
        var record = combo.findRecord(combo.valueField, value);
        return record ? record.get(combo.displayField) : combo.valueNotFoundText;
    }
}


TreeManager.PageTypeStore = Ext.extend(TreeManager.BaseStore, {
	constructor: function(config) {
		if(!config){
			config = {};
		}
		TreeManager.PageTypeStore.superclass.constructor.call(this, Ext.apply(config, {
			proxy : new Ext.data.HttpProxy({
				api: {
					read : { url: urls.types, method: "GET" }
				}
			})
		}));
	}
});

TreeManager.pages_store = new TreeManager.PageTypeStore({
	storeId: "PageTypeStore",
	baseParams:{search: true, meta:1}
});

TreeManager.pages_store.load();

TreeManager.PageTypeCombo = Ext.extend(Ext.form.ComboBox, {
	initComponent: function() {
		var config = {
			typeAhead: true,
			//hideTrigger:true,
			mode : 'remote',
            triggerAction: 'all',
            editable: false,
            hiddenName: 'page_type_id',
			emptyText : "Seleziona il tipo di pagina",
			fieldLabel: "Tipo",
            lazyInit: false,
			store : TreeManager.pages_store,
			valueField: "id",
			queryParam: "id",
			displayField: "description",
			loadingText: "Cerco...",
			forceSelection: true
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		TreeManager.PageTypeCombo.superclass.initComponent.call(this);
	}
});

var pageTypeCombo = new TreeManager.PageTypeCombo();
