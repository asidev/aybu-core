% if c.rendering_type=='dynamic':
<%include file="/base/menu.mako" args="root=c.node.path[1], start_level=1, num_levels=c.settings['template_levels']"/>
% else:
&nbsp;
% endif:
