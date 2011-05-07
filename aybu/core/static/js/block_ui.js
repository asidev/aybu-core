/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

function block_ui(msg) {
	if (!msg)
		msg = "Salvataggio modifiche in corso";
	$.blockUI({
    	css: {
            border: 'none',
            top:  ($(window).height() - 200) /2 + 'px',
            left: ($(window).width() - 200) /2 + 'px',
            width: '200px',
            padding: '5px',
            backgroundColor: '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#fff'
    	},
    	message: msg
    });
}
