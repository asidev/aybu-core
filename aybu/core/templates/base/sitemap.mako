<%
	domain = request.host_url
%>\
<%self.seen_url = set() %>\
<%def name="menu_tree(tree, domain)">\
	% for page in tree.pages:
		% for translation in page.translations:
			% if translation.lang.enabled:
				% if translation.url not in self.seen_url:
					<url>
						<loc>${domain}${translation.url}</loc>
						<priority>${page.sitemap_priority}</priority>
					</url>
					<% self.seen_url.add(translation.url) %>\
				% endif
			%endif
		%endfor
	% endfor
</%def>\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.google.com/schemas/sitemap/0.84" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.google.com/schemas/sitemap/0.84 http://www.google.com/schemas/sitemap/0.84/sitemap.xsd">
	% for tree in c.menus:
		${self.menu_tree(tree, domain)}
	% endfor
</urlset>
