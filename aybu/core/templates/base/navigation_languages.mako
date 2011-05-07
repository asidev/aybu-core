% if len(c.languages) > 1:
<ul id="languages">
	% for language in c.languages:
	<%
		if c.rendering_type!='dynamic':
			url = h.url(request.environ['PATH_INFO'], lang=language.lang,
						country=language.country)
		else:
			try:
				url = c.node[language].url
			except:
				url = '#'
	%>
	<li>
		<a href="${url}"
			% if language.id == c.lang.id:
			class="active"
			% endif
			style="background-image: url(${h.static_url('/flags/%s.png' % (language.country.lower()))})"
			>
			${h.locale_from_language(language).get_display_name().title()}
		</a>
	</li>
	% endfor
</ul>
% endif
