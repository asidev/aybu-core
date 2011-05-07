/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('TreeManager')

Ext.onReady(function() {
	Ext.QuickTips.init();

	var tree = new TreeManager.TreeGrid();
	
	tree.render('extjs-main-panel-div');

});
