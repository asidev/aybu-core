/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns("imgmanager");

imgmanager.EditForm = Ext.extend(Ext.form.FormPanel, {
	constructor : function (config) {
		this.image_record = null;
		this.labelWidth = 75;
		this.frame = true;
		this.fileUpload = true;
		this.bodyStyle = 'padding:5px 5px 0',
		this.defaults = { width : 230 };
		this.defaultType = 'textfield';
		this.win = null;
		this.items  = [
			/*
			{
			 id : 'edit__image_name',
			 fieldLabel : 'Nome',
			 name: 'name',
			 allowBlank : true
			}
			*/
			{
			 xtype : 'fileuploadfield',
			 id : "file",
			 emptyText : "Selezionare un'immagine",
			 fieldLabel: 'Immagine',
			 input_name: 'file',
			 buttonText: '',
			 buttonCfg : { iconCls : 'silk-image_add'}
			}
		];
		this.buttons = [
			{ text: 'Salva',
			  iconCls : 'silk-disk',
			  scope : this,
			  handler: function () {
				this.getForm().submit({
					clientValidation : true,
					url: urls.update,
					params: {
						id: this.image_record.data.id
					},
					success: this.onSuccess,
					failure: this.onFailure
				});
			  }
			},
			{  text: 'Annulla',
			   iconCls : 'silk-cross',
			   scope : this,
			   handler : function (b, ev) {
					this.win.hide();
			   }
			}
		]
		imgmanager.EditForm.superclass.constructor.apply(this, arguments);
	},
	initComponent : function() {
		imgmanager.EditForm.superclass.initComponent.apply(this, arguments);
	},
	setImageRecord : function(record) {
		this.image_record = record;
		Ext.getCmp('edit__image_name').setValue(record.data.name);
	},
	setWindow : function(win) {
		this.win = win;
	},
	onSuccess : function(form, action) {
		imgmanager.dataview.getStore().reload();
		Ext.getCmp('editformwin').hide();
	},
	onFailure : function(form, action) {
		switch (action.failureType) {
            case Ext.form.Action.CLIENT_INVALID:
                Ext.Msg.alert('Errore', 'Form non valido');
                break;
            case Ext.form.Action.CONNECT_FAILURE:
                Ext.Msg.alert('Errore', 'Non è stato possibile contattare il server');
                break;
       }
	}

});

imgmanager.EditButton = Ext.extend(Ext.Button, {
	constructor: function (config) {
		this.editform = new imgmanager.EditForm(config.form_config);
		this.window = new Ext.Window({
			title : config.window_title || config.text || 'Edit Image',
			width : config.window_width || 380,
			height: config.window_height || 150,
			id : 'editformwin',
			modal: 'true',
			layout : 'fit',
			items : this.editform,
			closeAction : 'hide',
			listeners : {
				hide : function(window) {
						this.editform.getForm().reset();
				},
				scope : this
			}
		});
		this.handler = function () {
			this.window.show();
			this.editform.setWindow(this.window);
			this.editform.doLayout();
			this.editform.setImageRecord(imgmanager.dataview.getSelectedRecords()[0]);
		};

		imgmanager.EditButton.superclass.constructor.apply(this, arguments);
	}
});

Ext.reg('imgmanagereditbutton', imgmanager.EditButton);
