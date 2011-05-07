<%def name="css()">
	${parent.css()}
	${self.css_link('/css/languages.css')}
</%def>

<%def name="js()">
	${parent.js()}
	% if c.settings.debug == True:
	${self.js_link('/js/languages.js')}
	% else:
	${self.js_link('/js/languages.min.js')}
	% endif
</%def>

<%def name="title()">
	${parent.title()}
	${self.title_part((_(u'Gestione Lingue'), h.url('admin', action='languages')))}
</%def>

<%inherit file="/admin/admin_template.mako"/>

<h3>${_(u'Gestione Lingue')}</h3>

<p>
	${_(u"Questa sezione permette l'aggiunta o la rimozione di una lingua al sito.")}
</p>
<div id="admin_languages">
	<ul>
	% for language in c.all_languages:
		<li>

			<input type="checkbox" id="lang_${language.id}" onchange="changeLanguage(${language.id})"
				% if language.enabled:
				   checked="checked"
				% endif
				/>

			<img src="${h.static_url('/flags/%s.png' % (language.country.lower()))}"
				alt="${h.locale_from_language(language).get_display_name().title()}"
				title="${h.locale_from_language(language).get_display_name().title()}" />

		</li>
	% endfor
	</ul>
	<div class="reset">&nbsp;</div>
</div>
