/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('TreeManager')


TreeManager.FormWin = Ext.extend(Ext.Window, {
	constructor: function(config) {
		TreeManager.FormWin.superclass.constructor.call(this, config);
	},
	initComponent: function () {
		var config = {
			layout: 'fit',
			width: 600,
			height: 500,
			closable: true,
			animCollapse: true,
			modal: true
		};

		this.pageForm = new TreeManager.PageForm({
			title : "Pagina",
			type : 'Page',
			win : this
		});
		this.sectionForm = new TreeManager.SectionForm({
			title : "Sezione",
			type : 'Section',
			win : this
		});
		this.externalLinkForm = new TreeManager.ExternalLinkForm({
			title : "Link Esterno",
			type : 'ExternalLink',
			win : this
		});
		this.internalLinkForm = new TreeManager.InternalLinkForm({
			title : "Link Interno",
			type : 'InternalLink',
			win : this
		});
		this.forms = [
			this.pageForm,
			this.sectionForm,
			this.externalLinkForm,
			this.internalLinkForm
		];

		this.tabPanel = new Ext.TabPanel({
			deferredRender : false,
			activeTab : 0,
			items : this.forms
		});

		this.items = [
			this.tabPanel
		];

		this.buttons = [
			{ text: "Chiudi", handler: this.close, scope: this }
		];

		Ext.apply(this, Ext.apply(this.initialConfig, config));
		TreeManager.FormWin.superclass.initComponent.call(this);
	},
	resetForm: function () {
		for (i=0; i<this.forms.length; i++) {
			this.forms[i].reset();
			this.forms[i].enable();
		}
	},
	show : function(menu_item_id, type, target, callback, scope) {

		this.menu_item_id = menu_item_id;
		this.menu_item_type = type;

		this.resetForm();

		if(menu_item_id){
			for (i=0; i<this.forms.length; i++) {
				this.forms[i].disable();
			}
			if(this.menu_item_type == 'Page'){
				this.pageForm.enable();
				this.pageForm.setUpdate();
				this.pageForm.load(menu_item_id);
				this.tabPanel.activate(this.pageForm);
			}else if(this.menu_item_type == 'Section'){
				this.sectionForm.enable();
				this.sectionForm.setUpdate();
				this.sectionForm.load(menu_item_id);
				this.tabPanel.activate(this.sectionForm);
			}
			else if(this.menu_item_type == 'ExternalLink'){
				this.externalLinkForm.enable();
				this.externalLinkForm.setUpdate();
				this.externalLinkForm.load(menu_item_id);
				this.tabPanel.activate(this.externalLinkForm);
			}else if(this.menu_item_type == 'InternalLink'){
				this.internalLinkForm.enable();
				this.internalLinkForm.setUpdate();
				this.internalLinkForm.load(menu_item_id);
				this.tabPanel.activate(this.internalLinkForm);
			}
		}

		return TreeManager.FormWin.superclass.show.call(this, target, callback, scope);
	}
});
