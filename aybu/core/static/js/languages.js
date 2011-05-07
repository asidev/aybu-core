/*
 * Copyright © 2010 Asidev s.r.l. - www.asidev.com
 */

function changeLanguage(id){

	checked = $("#lang_" + id).attr('checked');
	action = (checked==true) ? "aggiungere" : "rimuovere";
	action = action + " la lingua " + $("#lang_" + id + " + img").attr("title");

	confirmed = confirm("Sei sicuro di voler " + action )

	if(confirmed){
		$.ajax({
			type : "POST",
			url: (checked==true) ? "/admin/language/enable" : "/admin/language/disable",
			data : {
				"lang_id" : id
			},
			success : function(r){
				alert(r.msg);
				if(!r.success){
					$("#lang_" + id).attr('checked', (!checked));
				}else{
					window.location.reload(true);
				}
			},
			error : function(){
				alert("Non è stato possibile "+ action );
				$("#lang_" + id).attr('checked', (!checked));
			}
		});
	}else{
		$("#lang_" + id).attr('checked', (!checked));
	}
}
