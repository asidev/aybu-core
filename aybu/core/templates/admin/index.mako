<%def name="js()">
	${parent.js()}
	% if c.settings.debug == True:
	${self.js_link('/js/cache.js')}
	% else:
	${self.js_link('/js/cache.min.js')}
	% endif
</%def>

<%def name="css()">
	${parent.css()}
	${self.css_link('/css/cache.css')}
</%def>

<%inherit file="/admin/admin_template.mako"/>

<h3>${_(u'Pannello di controllo')}</h3>

<p>
	${_(u'Questa sezione permette la gestione dei contenuti del sito.')}
</p>
<p>
	${_(u'Per modificare le singole pagine, è sufficiente navigare il sito fino alla pagina che si desidera cambiare, quindi premere sul bottone "Edit" appena sopra il contenuto.')}
</p>

% if c.cache_disabler:
<div id="toggle_cache">
	<h4>${_(u'Gestione cache')}</h4>
	<% state = _(u'Disabilitata') if c.cache_disabled else _(u'Abilitata') %>
	<p>
		${_(u'Stato cache attuale:')}
		<strong>${state}</strong>
	</p>
	<% value = _(u"Abilita") if c.cache_disabled else _(u"Disabilita") %>
	<form  onsubmit="return toggleCache('${h.url('admin', action='toggle_cache')}');">
		<fieldset >
			<input type="submit" value="${value}" />
		</fieldset>
	</form>
</div>
% endif

% if c.cache_purger:
<div id="purge_cache"
	% if c.cache_disabled:
		style="display:none;"
	% endif
	>
	<h4>${_(u'Pulizia cache')}</h4>
	<form onsubmit="return purgeCache('${h.url('admin', action='purge_cache')}');">
		<fieldset >
			<input type="submit" value="${_('Pulisci cache')}" />
		</fieldset>
	</form>
</div>
% endif
