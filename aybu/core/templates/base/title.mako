<%page args="final_title" />

% if c.rendering_type!='dynamic':
<title>${' - '.join([path[0] for path in final_title])}</title>
% else:
<%	self.titles = [node[c.lang].title for node in c.node.path[1:]] %>
<title>${c.settings['site_title']} - ${' - '.join(self.titles)}</title>
% endif
