<%page args="final_title, css, js" />

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	% if c.settings['head_info'] is not None:
	${h.literal(c.settings['head_info'])}
	% endif
	% if c.rendering_type=='dynamic':
	<meta name="description" content="${c.translation.meta_description}" />
	% if c.translation.head_content is not None:
	${h.literal(c.translation.head_content)}
	% endif
	% endif
	<%include file="/base/title.mako" args="final_title=final_title"/>
	<link rel="shortcut icon" href="/favicon.ico" type="image/icon" />
	${css()}
	${js()}
</head>
