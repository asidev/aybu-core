/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

var dropline_menu = {

	animate_time : {
		over : 0,
		out : 0
	}, //duration of slide in/ out animation, in milliseconds

	build : function(menu_selector) {
		jQuery(document).ready(function($){
			mains_li = $(menu_selector + ">li");
			mains_li.each(function(i){
				var cur_li = $(this);
				cur_li.css('width', cur_li.width() + 'px');
			});

			var main_menu = $(menu_selector);
			var headers = main_menu.find("ul").parent();
			headers.each(function(i){
				var cur_li = $(this);
				var sub_ul=$(this).find('ul:eq(0)');
				sub_ul.css('width', sub_ul.width() + 'px');
				cur_li.hover(
					function(e){
						var displayed_ul = $(menu_selector + ">li>a.active+ul");
						var sub_ul = $(this).find('ul:eq(0)')
						if(sub_ul!=displayed_ul){
							$(this).children('a').toggleClass('active coded');
							displayed_ul.slideUp(dropline_menu.animate_time.out);
							sub_ul.slideDown(dropline_menu.animate_time.over);
						}
					},
					function(e){
						$(this).children('a').toggleClass('active coded');
						var sub_ul = $(this).children("ul:eq(0)");
						var displayed_ul = $(menu_selector + ">li>a.active+ul");
						if(sub_ul!=displayed_ul){
							sub_ul.slideUp(dropline_menu.animate_time.out);
							displayed_ul.slideDown(dropline_menu.animate_time.over);
						}
					}
				);
			});

			var displayed_ul = $(menu_selector + ">li>a.active+ul");
			displayed_ul.slideDown(0);

		});
	}
}
