(function($){ 
	$(document).ready( function() {
		$('.help').popover({trigger : 'manual'}).click(function(e){
			$('.help').not(this).popover('hide');
			$(this).popover('toggle');
			e.preventDefault(); 
		});
		
		var ul = $('#language-codes');
		if (ul.length) {
			ul.append(ul.children("li").detach().sort(function(a, b) {
				if (a.children[0].text > b.children[0].text) return 1;
				return -1;
			}));
		}
	});
})(yawdadmin.jQuery);