/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('settings')

settings.SettingFormWin = Ext.extend(Ext.Window, {
	constructor: function(config) {
		this.setting = config.setting;
		settings.SettingFormWin.superclass.constructor.call(this, config);
	},
	initComponent: function () {
		var config = {
			layout: 'fit',
			width: 400,
			height: 300,
			closable: true,
			animCollapse: true,
			modal: true
		};
		this.setting_form = new settings.SettingForm({
			setting : this.setting,
            win : this
		});
		this.items = [ this.setting_form ];
		this.buttons = [
			{ text: "Chiudi", handler: this.close, scope: this }
		];
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		settings.SettingFormWin.superclass.initComponent.call(this);
	},
	resetForm: function () {
		this.setting_form.reset();
	},
	show : function(setting, target, callback, scope) {
		this.resetForm();
		if(setting){
			this.setting_form.setUpdate();
			this.setting_form.load(setting);
		}
		return settings.SettingFormWin.superclass.show.call(this, target, callback, scope);
	}
});
