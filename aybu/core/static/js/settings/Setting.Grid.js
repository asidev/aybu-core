/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('settings')

settings.SettingsGrid = Ext.extend(Ext.grid.EditorGridPanel, {
    initComponent : function() {

		var selectionmodel = new Ext.grid.CheckboxSelectionModel({
			listeners : {
				selectionchange : {
					fn : this.onselectionchange,
					scope : this
				}
			}
		});

		var config = {
			title : "Impostazioni",
			id : "SettingsGrid",
			loadMask : true,
			viewConfig : {
				forceFit: true
			},
			columnLines : true,
			stripeRows: true,
			cm : new Ext.grid.ColumnModel([
				selectionmodel,
				{
					id : "name",
					header : "Nome",
					dataIndex : "name",
					sortable : true,
					width : 80
				},
				{
					id : 'value',
					header : 'Valore',
					dataIndex : 'value',
					sortable : true,
					width : 80
				}/*,
				{
					id : 'ui_administrable',
					header : 'Amministrabile',
					dataIndex : 'ui_administrable',
					sortable : true,
					width : 50
				},
				{
					id : 'raw_type',
					header : 'Raw Type',
					dataIndex : 'raw_type',
					sortable : true,
					width : 40
				},
				{
					id : 'setting_type_name',
					header: "Tipo",
					dataIndex: 'setting_type_name',
					width: 40
				}
				 */
			]),
			bbar : new Ext.PagingToolbar({
				pageSize: this.getStore().pageSize,
				store : this.getStore(),
				displayInfo : true,
				displayMsg: 'Impostazioni {0} - {1} di {2}',
				emptyMsg : 'Nessuna impostazione trovata'
			}),
			tbar : [
				/*
				{
					text: "Nuova",
					tooltip : "Aggiungi un'impostazione",
					iconCls: "silk-add",
					handler : this.show_page_form,
					scope: this,
					ref : "../addButton"
				},"-",*/
				{
					text : "Modifica",
					tooltip : "Modifica l'impostazione selezionata",
					iconCls: 'silk-edit',
					ref : "../editButton",
					handler : this.show_page_form,
					scope : this,
					disabled: true
				}/*, "-", {
					text : "Elimina",
					handler: this.delete_button_clicked,
					scope: this,
					ref : "../deleteButton",
					tooltip : "Rimuovi l'impostazione selezionata",
					iconCls: "silk-cross",
					disabled : true
				}*/
			],
			sm : selectionmodel
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		settings.SettingsGrid.superclass.initComponent.call(this);
	},
	onselectionchange : function(sm) {
		if (sm.getCount()) {
			if (sm.getCount() > 1) {
				this.editButton.disable();
			} else {
				this.editButton.enable();
			}
			//this.deleteButton.enable();
		} else {
			this.editButton.disable();
			//this.deleteButton.enable();
		}
	},
	show_page_form : function(btn, ev) {
		sm = this.getSelectionModel();
		/*
		if(btn == this.addButton){
			this.win = new settings.SettingFormWin({title: "Aggiungi impostazione", animateTarget: btn, setting : null});
			this.win.show(null, btn)
		}
		else */if(btn == this.editButton){
			setting = sm.getSelected().data;
			this.win = new settings.SettingFormWin({title: "Modifica impostazione", animateTarget: btn, setting : setting});
			this.win.show(setting, btn);
		}
	}/*,
	delete_button_clicked : function(btn, ev){
	   Ext.Msg.confirm(
		   'Eliminare le impostazioni?',
		   'Sei sicuro di voler eliminare le impostazioni selezionate? (non potranno essere recuperate)',
		   this.delete_selected_pages,
		   this
	   );
	},
	delete_selected_pages : function(clicked_button_id){
	   if(clicked_button_id != "yes"){
		   return;
	   }
	   Ext.Msg.wait("Rimozione impostazioni", "Rimozione impostazioni in corso... ");
	   this.getStore().remove(this.getSelectionModel().getSelections());
	   this.getStore().reload_after_save = true;
	   this.getStore().save();
	}*/
});
