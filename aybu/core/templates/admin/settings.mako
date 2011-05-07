<%def name="css()">
	${parent.css()}
	${self.css_link('/js/lib/extjs/resources/css/ext-all-notheme.css')}
	${self.css_link('/js/lib/extjs/resources/css/xtheme-gray.css')}
	${self.css_link('/css/setting.css')}
</%def>

<%def name="js()">
	${parent.js()}
	<script type="text/javascript">
		var urls = {
			list : "${url('settings', action='list')}",
			create : "${url('settings', action='create')}",
			update : "${url('settings', action='update')}",
			destroy : "${url('settings', action='destroy')}",
			info : "${url('settings', action='info')}",
			types : "${url('settings', action='types')}"
		}
	</script>
	% if c.settings.debug == True:
	${self.js_link('/js/lib/extjs/adapter/ext-jquery-adapter-debug.js')}
	${self.js_link('/js/lib/extjs/ext-all-debug.js')}
	${self.js_link('/js/lib/extjs/locale/ext-lang-it.js')}
	${self.js_link('/js/lib/extjs/ux/CheckColumn.js')}
	${self.js_link('/js/lib/extjs/ux/RowExpander.js')}
	${self.js_link('/js/settings/BaseStore.js')}
	${self.js_link('/js/settings/Setting.Type.js')}
	${self.js_link('/js/settings/Setting.Store.js')}
	${self.js_link('/js/settings/Setting.Form.js')}
	${self.js_link('/js/settings/Setting.FormWindow.js')}
	${self.js_link('/js/settings/Setting.Grid.js')}
	${self.js_link('/js/settings/main.js')}
	% else:
	${self.js_link('/js/lib/extjs/adapter/ext-jquery-adapter.js')}
	${self.js_link('/js/lib/extjs/ext-all.js')}
	${self.js_link('/js/lib/extjs/locale/ext-lang-it.min.js')}
	${self.js_link('/js/lib/extjs/ux/CheckColumn.js')}
	${self.js_link('/js/lib/extjs/ux/RowExpander.js')}
	${self.js_link('/js/settings/BaseStore.min.js')}
	${self.js_link('/js/settings/Setting.Type.min.js')}
	${self.js_link('/js/settings/Setting.Store.min.js')}
	${self.js_link('/js/settings/Setting.Form.min.js')}
	${self.js_link('/js/settings/Setting.FormWindow.min.js')}
	${self.js_link('/js/settings/Setting.Grid.min.js')}
	${self.js_link('/js/settings/main.min.js')}
	% endif
</%def>


<%def name="title()">
	${parent.title()}
	${self.title_part((_(u'Impostazioni'), h.url('admin', action='settings')))}
</%def>

<%inherit file="/admin/admin_template.mako"/>

<h3>${_(u'Impostazioni')}</h3>

<p>
	${_(u"Questa sezione permette la gestione delle impostazioni del sito.")}
</p>

<div id="extjs-main-panel-div"></div>
