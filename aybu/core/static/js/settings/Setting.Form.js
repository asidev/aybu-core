/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('settings')


settings.SettingForm = Ext.extend(Ext.form.FormPanel, {

	constructor : function(config){
        this.win = config.win;
		this.setting = config.setting
		config.defaults = {
			anchor: "90%",
			xtype: "textfield"
		};
		settings.SettingForm.superclass.constructor.call(this, config);
		this.isUpdate = false;
		this.waitMsg = "Salvo...";
		this.submit_url = urls.create;
		this.related = [];
	},

	initComponent: function(){

		var config = {
			layout: 'form',
			padding : 10,
			labelWidth : 80
		};

		var name = new Ext.form.TextField({
			id : "name",
			name : "name",
			readOnly : true,
			fieldLabel : "Nome",
			allowBlank : false
		});

		if(this.setting.setting_type_name=='html'){
			var value = new Ext.form.HtmlEditor({
				id : "value",
				name : "value",
				fieldLabel : "Valore",
				allowBlank : false,
				enableLists : false
			});
		}else if(this.setting.setting_type_name=='txt' || this.setting.setting_type_name=='image'){
			if(this.setting.raw_type=='int'){
				 var value = new Ext.form.NumberField({
					id : "value",
					name : "value",
					fieldLabel : "Valore",
					allowBlank : false
				});
			}else {
				var value = new Ext.form.TextField({
					id : "value",
					name : "value",
					fieldLabel : "Valore",
					allowBlank : false
				});
			}
		}else if(this.setting.setting_type_name=='checkbox'){
			var value = new Ext.form.Checkbox({
				id : "value",
				name : "value",
				fieldLabel : "Valore",
				allowBlank : false
			});
		}

		this.items = [
			name,
			value
		];

		this.buttons = [
			{ id: "reset", text : "Reset", handler : this.reset, scope : this },
			{ id: "submit", text : "Salva", handler : this.submit, scope : this }
		];

		Ext.apply(this, Ext.apply(this.initialConfig, config));
		settings.SettingForm.superclass.initComponent.call(this);
	},
	reset : function(){
		if(this.isUpdate){
			this.load(this.id);
		} else {
			this.getForm().reset();
		}
	},
	submit: function(){
		this.getForm().submit({
			url : this.submit_url,
			success : this.submit_success,
			failure : this.submit_failure,
			scope: this,
			clientValidation: true,
			waitMsg : this.waitMsg
		});
	},
	submit_success : function(form, action){
        Ext.Msg.show({
            title : 'Impostazione Salvata',
            msg : "Impostazione salvata con successo.",
            icon : Ext.MessageBox.INFO,
            buttons : Ext.Msg.OK,
			fn: this.reload_window
        });
	},
	reload_window: function() {
		//this.grid.getStore().reload();
		//this.win.close();
		window.location.reload(true);
	},
	submit_failure: function(form, action){
		switch (action.failureType) {
			case Ext.form.Action.CLIENT_INVALID:
				Ext.Msg.alert('Validazione', 'Errore di validazione dei campi');
				break;
			default:
				Ext.Msg.alert('Richiesta fallita', action.result.errors.exception);
				break;
		}
	},
	load : function(setting){
		this.name = setting.name;
        this.setting = setting;
		options = {
			url : urls.info,
			params : { name : this.name },
			success : this.load_success,
			failure : this.load_error,
			scope : this,
			waitMsg : "Carico..."
		}
		this.getForm().load(options)
	},
	load_success : function(form, action) {

	},
	setUpdate : function(username) {
		this.isUpdate = true;
		this.waitMsg = "Aggiorno...";
		this.submit_url = urls.update;
		this.enable();
	}
});
