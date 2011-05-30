<%self.seen_css = set() %>\
<%def name="css_link(path, media='screen, projection', internal=True)">\
	% if path not in self.seen_css:
		% if internal:
			<% static_url = h.static_url(path) %>
			% if static_url:
			<link rel="stylesheet" type="text/css" href="${static_url}" media="${media}" />
			% endif
		% else:
		<link rel="stylesheet" type="text/css" href="${path}" media="${media}" />
		% endif
		<% self.seen_css.add(path) %>\
	% endif
</%def>\
<%def name="css()">\
	% if c.user and c.rendering_type=='dynamic':
	${css_link('/css/tynymce.css')}

	${css_link('/js/lib/uploadify/uploadify.css')}

	% endif
</%def>\
\
<%self.seen_js = set() %>\
<%def name="js_link(path, internal=True)">\
	% if path not in self.seen_js:
		% if internal:
			<% static_url = h.static_url(path) %>
			% if static_url:
			<script type="text/javascript" src="${static_url}"></script>
			% endif
		% else:
		<script type="text/javascript" src="${path}"></script>
		% endif
		<% self.seen_js.add(path) %>
	% endif
</%def>\
<%def name="js()">\
	${js_link('/js/lib/jquery/jquery-1.6.1.min.js')}
	% if c.user and c.rendering_type=='dynamic':

		${js_link('/js/lib/jquery/ui/jquery-ui.min.js')}

		<script type="text/javascript">
			var editableContentWidth = 600;
		</script>
		${js_link('/js/lib/tiny_mce/jquery.tinymce.js')}

		% if c.settings.debug == True:
		${js_link('/js/lib/tiny_mce/tiny_mce_src.js')}
		${js_link('/js/lib/jquery/jquery.blockUI.js')}
		% else:
		${js_link('/js/lib/tiny_mce/tiny_mce.js')}
		${js_link('/js/lib/jquery/jquery.blockUI.min.js')}
		% endif


		<script type="text/javascript">

			var admin = true;

			var c = {
				translation: { id : ${c.translation.id} },

				lang : "${c.lang.lang}",
				country : "${c.lang.country}",
				language : "${h.locale_from_language(c.lang).get_display_name().title()}",

				urls : {
					edit: '${url("edit")}',
					tinymce : '${h.static_url("/js/lib/tiny_mce/tiny_mce.js")}',
					spellchecker: '${url("spellchecker")}',
					images: {
						list: '${url("images", action="list")}',
						add : '${url("images", action="add")}',
						remove : '${url("images", action="remove")}',
						index : '${url("images", action="index", tiny="true")}'
					},
					files: {
						index : '${url("files", action="index", tiny="true")}'
					},

					link_list : '${url("structure", action="link_list")}',

					page_banners : '${h.url("admin", action="page_banners")}',
					remove_page_banners : '${h.url("admin", action="remove_page_banners")}'

				}

			};

		</script>

		% if c.settings.debug == True:
		<%include file="/admin/extjs-debug.mako"/>
		${js_link('/js/tinymce.js')}
		${js_link('/js/content.js')}
		${js_link('/js/image.js')}
		${js_link('/js/files.js')}
		${js_link('/js/block_ui.js')}
		${js_link('/js/banner.js')}
		${js_link('/js/main.js')}
		% else:
		<%include file="/admin/extjs.mako"/>
		${js_link('/js/tinymce.min.js')}
		${js_link('/js/content.min.js')}
		${js_link('/js/image.min.js')}
		${js_link('/js/files.min.js')}
		${js_link('/js/block_ui.min.js')}
		${js_link('/js/banner.min.js')}
		${js_link('/js/main.min.js')}
		% endif

	% endif
</%def>\
\
\
<%self.final_title = [] %>\
<%def name="title_part(t)">\
	<% self.final_title.append(t) %>\
</%def>\
<%def name="title()">\
	${self.title_part((c.settings['site_title'],h.url('/')))}
</%def>\
${self.title()}
\
\
<%self.final_keywords = [] %>\
<%def name="keywords_part(k)">\
	% if k not in self.final_keywords:
		<% self.final_keywords.append(k.title()) %>\
	% endif
</%def>
<%def name="keywords()" >\
	${self.keywords_part(u'')}
</%def>\
${self.keywords()}
\
${next.body()}
\
