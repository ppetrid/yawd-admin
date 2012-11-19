(function($){ 
	$(document).ready( function() {
		$('.help').popover({trigger : 'manual'}).click(function(e){
			$('.help').not(this).popover('hide');
			$(this).popover('toggle');
			e.preventDefault(); 
		});
	});
})(yawdadmin.jQuery);