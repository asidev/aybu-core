<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>${_(u'Editor delle immagini')}</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta name="description" content="${_(u'Editor delle immagini')}" />
	<script type="text/javascript">
		var urls = {
			add : "${url('images', action='add')}",
			list : "${url('images', action='list')}",
			remove : "${url('images', action='remove')}",
			update : "${url('images', action='update')}"
		}
	</script>
	<script src="${h.static_url('/js/lib/jquery/jquery.min.js')}" type="text/javascript"></script>
	% if c.settings.debug == True:
	<%include file="/admin/extjs-debug.mako"/>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/store.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/edit_win.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/dataview.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/uploader.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/panel.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/main.js')}"></script>
	% else:
	<%include file="/admin/extjs.mako"/>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/store.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/edit_win.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/dataview.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/uploader.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/panel.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/imagemanager/main.min.js')}"></script>
	% endif
	## application code
	% if c.tiny:
	## this is needed to get reference to the tinyMCE instance that opened us.
	<script type="text/javascript" src="${h.static_url('/js/lib/tiny_mce/tiny_mce_popup.js')}"></script>
	% else:
	## this is to avoid unreference errors
	<script type="text/javascript">
		var tinyMCE = null;
	</script>
	%endif
</head>
<body>
	<div id="extjs-main-panel-div"></div>
</body>
</html>
