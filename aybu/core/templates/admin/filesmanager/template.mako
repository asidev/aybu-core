<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>${_(u'Editor dei files')}</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta name="description" content="${_(u'Editor dei files')}" />
	<script type="text/javascript">
		var urls = {
			add : "${url('files', action='add')}",
			list : "${url('files', action='list')}",
			remove : "${url('files', action='delete')}"
		}
	</script>
	<script src="${h.static_url('/js/lib/jquery/jquery.min.js')}" type="text/javascript"></script>
	% if c.settings.debug == True:
	<%include file="/admin/extjs-debug.mako"/>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/store.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/uploader.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/list.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/panel.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/main.js')}"></script>
	% else:
	<%include file="/admin/extjs.mako"/>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/store.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/uploader.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/list.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/panel.min.js')}"></script>
	<script type="text/javascript" src="${h.static_url('/js/filesmanager/main.min.js')}"></script>
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
