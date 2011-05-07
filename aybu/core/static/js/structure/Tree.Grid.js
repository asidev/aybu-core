/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('TreeManager')


TreeManager.TreeGrid = Ext.extend(Ext.ux.tree.TreeGrid, {

	selectedNode : null,

	initComponent : function() {

		var enabledColumn = new Ext.list.BooleanColumn ({
			header : 'Abilitato',
			dataIndex : 'enabled',
			align : 'center',
			tpl : '<div class="enabled_{enabled}">&nbsp;</div>',
			width : 45
		});

		var config = {
			rootVisible : false,
			title : 'Gestione Pagine',
			//width : 585,
			width : 560,
			enableSort : false,
			enableDD : true,
			dataUrl : urls.tree,
			columns:[
				{ header : 'Etichetta', dataIndex : 'button_label',  width : 170 },
				{ header : 'ID', dataIndex : 'id',  width : 25, hidden: true},
				{ header : 'Titolo', dataIndex : 'title', width : 170 },
				{ header : 'URL', dataIndex : 'url', width : 170 },
				enabledColumn
			],
			tbar : [
				{
					text: "Nuova",
					tooltip : "Aggiungi",
					iconCls: "silk-add",
					handler : this.show_form,
					ref : '../addButton',
					scope : this
				},
				'-',
				{
					text : "Modifica",
					tooltip : "Modifica",
					iconCls: 'silk-edit',
					handler : this.show_form,
					ref : '../editButton',
					disabled : true,
					scope : this
				},
				'-',
				{
					text : "Elimina",
					tooltip : "Rimuovi",
					iconCls : "silk-cross",
					handler : this.delete_button_clicked,
					ref : '../deleteButton',
					disabled : true,
					scope : this
				}
			]
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		TreeManager.TreeGrid.superclass.initComponent.call(this);
		this.addListener('dblclick', this.dblclick);
		this.addListener('click', this.click);
		this.addListener('nodedragover', this.nodedragover);
		this.addListener('dragdrop', this.dragdrop);
		this.getRootNode().allowChildren = false;
	},

	click : function(node, e) {
		this.selectedNode = node;
		this.editButton.enable();
		this.deleteButton.enable();
	},

	dblclick : function(node, e) {
		id = this.selectedNode.attributes.id;
		type = this.selectedNode.attributes.type;
		this.win = new TreeManager.FormWin({
			title : "Modifica"
		});
		this.win.show(id, type);
	},

	nodedragover : function(dragOverEvent) {
		type = dragOverEvent.target.attributes.type;
		console.log(dragOverEvent.target);
		if(type == 'Page' || type == 'Section' || type == 'Menu'){
			return true;
		}
		dragOverEvent.cancel = true;
		return false;
	},

	dragdrop : function(tree, node, dd, e){
		options = {
			url : urls.move,
			params : {
				moved_node_id : node.id,
				new_parent_id : node.parentNode.id,
				previous_node_id : node.previousSibling != null ? node.previousSibling.id : null,
				next_node_id : node.nextSibling != null ? node.nextSibling.id : null
			},
			success : function(response) {
				window.location.reload(true);
			},
			failure : function(response) {
				alert('Errore');
			},
			scope : this,
			waitMsg : "Elimino..."
		}

		Ext.Ajax.request(options);
	},

	show_form : function(btn, ev){
		if(btn == this.addButton){
			this.win = new TreeManager.FormWin({
				title : "Nuova"
			});
			this.win.show(null, 'page');
		}
		else if(btn == this.editButton){
			id = this.selectedNode.attributes.id;
			type = this.selectedNode.attributes.type;
			this.win = new TreeManager.FormWin({
				title : "Modifica"
			});
			this.win.show(id, type);
		}
	},

	delete_button_clicked : function(btn, ev){
		Ext.Msg.confirm(
			'Eliminare la pagina/sezione?',
			'Sei sicuro di voler eliminare la pagina/sezione selezionata? (non potrà essere recuperata)',
			this.delete_selected_pages,
			this
		);
	},

	delete_selected_pages : function(clicked_button_id){
		if(clicked_button_id != "yes"){
			return;
		}
		Ext.Msg.wait("Rimozione", "Rimozione in corso... ");
		// Insert code her to delete page/section

		options = {
			url : urls.destroy,
			params : { id : this.selectedNode.attributes.id },
			success : function(response) {
				window.location.reload(true);
			},
			failure : function(response) {
				alert('Errore');
			},
			scope : this,
			waitMsg : "Elimino..."
		}

		Ext.Ajax.request(options);
	}

});
