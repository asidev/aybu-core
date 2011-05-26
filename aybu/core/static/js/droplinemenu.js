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
				cur_li.css('width', cur_li.outerWidth() + 'px');
			});

			var main_menu = $(menu_selector);
			var headers = main_menu.find("ul").parent();
			headers.each(function(i){
				var cur_li = $(this);
				var sub_ul=$(this).find('ul:eq(0)');
				sub_ul.css('width', sub_ul.outerWidth() + 2 + 'px');
				cur_li.hover(
					function(e){
						var displayed_ul = $(menu_selector + ">li>a.active+ul");
						displayed_ul.addClass('displayed');
						var sub_ul = $(this).find('ul:eq(0)');
						if(!sub_ul.hasClass('displayed')){
							$(this).children('a').addClass('active coded');
							displayed_ul.slideUp(dropline_menu.animate_time.out);
							sub_ul.slideDown(dropline_menu.animate_time.over);
						}
						displayed_ul.removeClass('displayed');
					},
					function(e){
						if($(this).children('a').hasClass('coded')){
							$(this).children('a').removeClass('active coded');
						}
						var displayed_ul = $(menu_selector + ">li>a.active+ul");
						displayed_ul.addClass('displayed');
						var sub_ul = $(this).children("ul:eq(0)");
						if(!sub_ul.hasClass('displayed')){
							sub_ul.slideUp(dropline_menu.animate_time.out);
							displayed_ul.slideDown(dropline_menu.animate_time.over);
						}
						displayed_ul.removeClass('displayed');
					}
				);
			});

			var displayed_ul = $(menu_selector + ">li>a.active+ul");
			displayed_ul.slideDown(0);

		});
	}
}
