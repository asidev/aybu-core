
% if c.settings['google_analytics_code'] is not None and c.settings['google_analytics_code'].strip()!='':
<!-- Google Analytics Code -->
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try{
var pageTracker = _gat._getTracker("${c.settings['google_analytics_code']}");
pageTracker._trackPageview();
} catch(err) {}
</script>
<!-- END Google Analytics Code -->
% endif
