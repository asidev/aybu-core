<%def name="js()">
	${parent.js()}
	<script type="text/javascript">
		var urls = {
			add : "${url('files', action='add')}",
			list : "${url('files', action='list')}",
			remove : "${url('files', action='delete')}"
		}
	</script>
	${self.js_link('/js/lib/jquery/jquery.min.js')}
	% if c.settings.debug == True:
	<%include file="/admin/extjs-debug.mako"/>
	${self.js_link('/js/filesmanager/store.js')}
	${self.js_link('/js/filesmanager/uploader.js')}
	${self.js_link('/js/filesmanager/list.js')}
	${self.js_link('/js/filesmanager/panel.js')}
	${self.js_link('/js/filesmanager/main.js')}
	% else:
	<%include file="/admin/extjs.mako"/>
	${self.js_link('/js/filesmanager/store.min.js')}
	${self.js_link('/js/filesmanager/uploader.min.js')}
	${self.js_link('/js/filesmanager/list.min.js')}
	${self.js_link('/js/filesmanager/panel.min.js')}
	${self.js_link('/js/filesmanager/main.min.js')}
	% endif
	## application code
	% if c.tiny:
	## this is needed to get reference to the tinyMCE instance that opened us.
	${self.js_link('/js/lib/tiny_mce/tiny_mce_popup.js')}
	% else:
	## this is to avoid unreference errors
	<script type="text/javascript">
		var tinyMCE = null;
	</script>
	%endif
</%def>

<%def name="title()">
	${parent.title()}
	${self.title_part((_(u'Gestione Files'),h.url('admin', action='files')))}
</%def>

<%inherit file="/admin/admin_template.mako"/>

<h3>${_(u'Gestione Files')}</h3>

<p>
	${_(u"Questa sezione permette la gestione dei file da linkare nel sito.")}
</p>

<p>
	${_(u"Puoi fare l'upload al massimo di %s files." % c.settings['max_files'])}
</p>

<p>
	${_(u"Il tentativo di upload di file aggiuntivi fallirà.")}
</p>

<div id="extjs-main-panel-div"></div>
