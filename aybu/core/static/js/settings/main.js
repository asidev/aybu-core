/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('settings');

Ext.onReady(function() {
	Ext.QuickTips.init();

	var store = new settings.SettingsStore({storeId: "SettingsStore"});
    store.load();

	var grid = new settings.SettingsGrid({
		store : store,
		autoHeight: true

	})

	grid.render('extjs-main-panel-div');

});
