<%def name="css()">
	${parent.css()}
	${self.css_link('/css/form.css')}
</%def>

<%def name="title()">
	${parent.title()}
	${self.title_part((_(u'Login'),h.url('login-render')))}
</%def>

<%inherit file="/inner_layout.mako"/>

<h2>${_('Area Riservata')}</h2>

%if hasattr(c, 'message'):
<h3 class="error">
	${c.message}
</h3>
%endif

<form id="login_form" method="post"
	% if hasattr(c,'compiler'):
		action=${c.area_riservata_post_url}
	% else :
		action="${h.url('login-submit')}"
	% endif
	>
	<fieldset>
		<label for="username">${_('Username:')}</label>
		<input id="username" name="username" type="text" />
		<label for="password">${_('Password:')}</label>
		<input id="password" name="password" type="password" />

		<input class="submit" id="submit" value="${_('Accedi')}"
		  title="${_('Accedi')}" type="submit" />
	</fieldset>
</form>
