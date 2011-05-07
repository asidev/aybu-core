<ul id="user">
	%if c.user:
	<li>
		<a href="${h.url('admin', action='index', lang=c.lang.lang, country=c.lang.country)}">
			Pannello di Controllo
		</a>
		&nbsp;|&nbsp;
	</li>
	<li>
		<a href="${h.url('logout')}">Logout</a>
	</li>
	%else:
	<li>
		<a href="${h.url('login-render', lang=c.lang.lang, country=c.lang.country)}">Login</a>
	</li>
	%endif
</ul>
