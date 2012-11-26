function html_unescape(text) {
    // Unescape a string that was escaped using django.utils.html.escape.
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&amp;/g, '&');
    return text;
}

function showRelatedObjectLookupPopup(triggeringLink) {
	yawdadmin.jQuery.popupTriggeringLink = triggeringLink.id.replace(/^lookup_/, '');
    return false;
}

function dismissRelatedLookupPopup(win, chosenId) {
    var elem = (yawdadmin.jQuery.popupTriggeringLink) ?
        	document.getElementById(yawdadmin.jQuery.popupTriggeringLink) : null;
    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        elem.value = chosenId;
    }
    
    yawdadmin.jQuery.fancybox.close();
    yawdadmin.jQuery.popupTriggeringLink = null;
}

//this function exists to not break the foreign key widget code
function showAddAnotherPopup(triggeringLink) { 
	yawdadmin.jQuery.popupTriggeringLink = triggeringLink.id.replace(/^add_/, '');
	return false;
}

function dismissAddAnotherPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var elem = (yawdadmin.jQuery.popupTriggeringLink) ?
    	document.getElementById(yawdadmin.jQuery.popupTriggeringLink) : null;
    if (elem) {
        var elemName = elem.nodeName.toUpperCase();
        if (elemName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elemName == 'INPUT') {
            if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + newId;
            } else {
                elem.value = newId;
            }
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    
    yawdadmin.jQuery.fancybox.close();
    yawdadmin.jQuery.popupTriggeringLink = null;
}

(function($){ 
	$(document).ready( function() {
		$('.add-another, .related-lookup').each(function() {
			var href = this.href;
			var self = $(this);
			
			if (self.hasClass('add-another')) {
				href += (href.indexOf('?') == -1) ? '?_popup=1' : '&_popup=1';
			} else if (self.hasClass('related-lookup')) {
				href += (href.indexOf('?') == -1) ? '?pop=1' : '&pop=1';
			}
			
			self.attr('data-fancybox-type','iframe').attr('href', href).fancybox();
		});
		
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