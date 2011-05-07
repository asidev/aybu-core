<%def name="title()">
	${parent.title()}
	${self.title_part((_(u'Pannello di controllo'), h.url('admin', action='index')))}
</%def>

<%def name="set_editable()">
	## don't want tinymce to kick in
	<% self.editable = False %>
</%def>

<%inherit file="/template.mako"/>

${next.body()}
