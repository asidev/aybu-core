/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

Ext.ns('filesmanager')

var search_field = new Ext.form.TextField({
	emptyText : "Cerca (nel nome)",
	id : "search",
	width: 100,
	enableKeyEvents : true,
});

search_field.on(
	"specialkey",
	function(field, e) { filter_list(this.getValue()); },
	search_field,
	{ buffer: 50 }
);

search_field.on(
	"keypress",
	function(field, e) { filter_list(this.getValue()); },
	search_field,
	{ buffer: 50 }
);

filesmanager.file_panel = new Ext.Panel({
	id: 'file-panel',
	autoScroll : true,
	region: 'center',
	tbar : new Ext.Toolbar({
		items : [ { text: "Seleziona",
				    itemId : 'select',
					disabled: 'true',
					iconCls : 'silk-attach',
					handler: function() { filesmanager.select_file();}
				}," ",
				filesmanager.plup_add_btn,
				{ text: 'Rimuovi',
				   itemId: 'delete',
				   disabled: true,
				   iconCls : "silk-cross",
				   handler: function () {
						selected = filesmanager.fileslist.getSelectedRecords();
						removable = new Array();
						used = 0;
						for (i=0; i < filesmanager.fileslist.getSelectionCount(); i++) {
							if ( selected[i].data.used_by.length > 0) {
								used++;
							} else {
								removable.push(selected[i]);
							}
						}
						if (removable.length > 0 ) {
							msg = "Rimuovere " + selected.length + " files?";
							Ext.Msg.confirm("Conferma rimozione", msg,
											function (btn) {
												if (btn == "yes")
													filesmanager.fileslist.store.remove(selected);
											}
							);
						} else {
							Ext.Msg.alert("Files in uso", "Uno o più file selezionati non possono essere rimossi in quanto in uso");
						}

				   }
				}, '->', search_field,
				{ text: "",
				  itemId : 'clearsearch',
				  iconCls: 'silk-clear',
				  handler: function() {
					search_field.setValue("");
					filter_list("");
				  }
				}]
	}),
	items: [ filesmanager.fileslist   ]
});
