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


TreeManager.MenuItemListStore = Ext.extend(TreeManager.BaseStore, {
	constructor: function(config) {
		if(!config){
			config = {};
		}
		TreeManager.MenuItemListStore.superclass.constructor.call(this, Ext.apply(config, {
			proxy : new Ext.data.HttpProxy({
				api: {
					read : { url: urls.list, method: "GET" }
				}
			})
		}));
	}
});

TreeManager.menu_items_store = new TreeManager.MenuItemListStore({
	storeId: "PageTypeStore",
	baseParams:{search: true, meta:1}
});

TreeManager.menu_items_store.load();

TreeManager.MenuItemListCombo = Ext.extend(Ext.form.ComboBox, {
	initComponent: function() {
		var config = {
			typeAhead: true,
			//hideTrigger:true,
			mode : 'remote',
            triggerAction: 'all',
            editable: false,
            hiddenName: 'linked_to',
			emptyText : "Seleziona la voce di menu",
			fieldLabel: "Tipo",
            lazyInit: false,
			store : TreeManager.menu_items_store,
			valueField: "id",
			queryParam: "id",
			displayField: "button_label",
			loadingText: "Cerco...",
			forceSelection: true
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		TreeManager.MenuItemListCombo.superclass.initComponent.call(this);
	}
});

var menuItemListCombo = new TreeManager.MenuItemListCombo();
