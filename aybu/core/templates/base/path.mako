<%page args="final_title" />

% if c.rendering_type!='dynamic':

<ol id="path">
	% if len(c.languages) > 1:
	<li id="path_flag">
		<img src="${h.static_url('/flags/%s.png' % (c.lang.country.lower()))}"
			alt="${h.locale_from_language(c.lang).get_display_name().title()}"
			title="${h.locale_from_language(c.lang).get_display_name().title()}"
			/>
	</li>
	% endif
	% for i, path in enumerate(final_title):
	<li>
		<a href="${path[1]}">${path[0]}</a>
		% if i < (len(final_title)-1) :
			&nbsp;&raquo;&nbsp;
		% endif
	</li>
	% endfor
</ol>

% else:

<ol id="path">
	% if len(c.languages) > 1:
	<li id="path_flag">
		<img src="${h.static_url('/flags/%s.png' % (c.lang.country.lower()))}"
			alt="${h.locale_from_language(c.lang).get_display_name().title()}"
			title="${h.locale_from_language(c.lang).get_display_name().title()}"
			/>
	</li>
	% endif
	<li>
		<a href="${c.menus[1].pages[0][c.lang].url}">${c.settings['site_title']}</a>
		&nbsp;&raquo;&nbsp;
	</li>
	<% 	self.links = [node[c.lang] for node in c.node.path[1:]] %>
	% for i, link in enumerate(self.links):
	<li>
		<%
			url = link.url
			if not url and len(node.pages) > 0:
				url = node.pages[0][c.lang].url
		%>
		<a
			% if url:
			href="${url}"
			% endif
			>
			${link.title}
		</a>
		% if i < (len(self.links) - 1) :
			&nbsp;&raquo;&nbsp;
		% endif
	</li>
	% endfor
</ol>

% endif
