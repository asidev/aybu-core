<ul>
	<li>
		<a href="${h.url('admin', action='index')}"
		   % if c.section=='admin' and c.page=='index':
		   class="active"
		   % endif
		>
			${_(u'Pannello di controllo')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='languages')}"
		   % if c.section=='admin' and c.page=='languages':
		   class="active"
		   % endif
		>
			${_(u'Gestione Lingue')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='structure')}"
		   % if c.section=='admin' and c.page=='structure':
		   class="active"
		   % endif
		>
			${_(u'Gestione Menu & Pagine')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='images')}"
		   % if c.section=='admin' and c.page=='images':
		   class="active"
		   % endif
		>
			${_(u'Gestione Immagini')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='files')}"
		   % if c.section=='admin' and c.page=='files':
		   class="active"
		   % endif
		>
			${_(u'Gestione Files')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='settings')}"
		   % if c.section=='admin' and c.page=='settings':
		   class="active"
		   % endif
		>
			${_(u'Gestione Impostazioni')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='banner_logo')}"
		   % if c.section=='admin' and c.page=='banner_logo':
		   class="active"
		   % endif
		>
			${_(u'Gestione Banner & Logo')}
		</a>
	</li>
	<li>
		<a href="${h.url('admin', action='password')}"
		   % if c.section=='admin' and c.page=='password':
		   class="active"
		   % endif
		>
			${_(u'Cambio Password')}
		</a>
	</li>
	<li>
		<a href="${h.url('logout')}">${_(u'Esci')}</a>
	</li>
</ul>
