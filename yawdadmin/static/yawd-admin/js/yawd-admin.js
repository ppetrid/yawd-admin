function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = yawdadmin.jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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
            var $elem = yawdadmin.jQuery(elem);
            $elem.change();
            //handle inlines
            var $inline_group = $elem.closest('.inline-group');
            if ($inline_group.length) {
            	var $id = $elem.attr('id');
            	var keyw = $elem.closest('.inline-related').attr('id');
            	$inline_group.find('.inline-related').each(function() {
            		var $this = yawdadmin.jQuery(this);
            		var iter_elem_id = $id.replace(keyw, $this.attr('id')).replace('-empty', '-__prefix__');
            		if (iter_elem_id != $id) {
            			var iter_elem = $this.find('#'+iter_elem_id).get(0);
            			var iter_o = new Option(newRepr, newId);
            			iter_elem.options[iter_elem.options.length] = iter_o;
            		}
            	});
            }
        } else if (elemName == 'INPUT') {
            if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + newId;
            } else {
                elem.value = newId;
            }
        }
    } else {
        var toId = yawdadmin.jQuery.popupTriggeringLink + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    
    yawdadmin.jQuery.fancybox.close();
    yawdadmin.jQuery.popupTriggeringLink = null;
}

function showAddAnotherPopupInline(triggeringLink) { 
	yawdadmin.jQuery.popupInlineTriggeringLink = triggeringLink;
	return false;
}

function dismissAddAnotherPopupInline(win, newId, newRepr, can_delete) {
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var elem = (yawdadmin.jQuery.popupInlineTriggeringLink) ?
    		yawdadmin.jQuery.popupInlineTriggeringLink : null;
    if (elem) {
    	elem.parent().siblings('.inline_label').html(newRepr);
    	if (can_delete) {
    		elem.closest('.inline-modal-header').find('.inline-deletelink')
    			.attr('onlick','')
    			.unbind('click')
    			.addClass('inline-delete')
    			.attr('href', elem.data('delete-href').replace('0', newId))
    			.html(gettext('Delete'));
    	}
    	elem.closest('.inline-related-popup').data('pk', newId);
    	elem.closest('.inline-modal-header').find('.icon-trash').addClass('text-error');
        elem.attr('href', elem.data('edit-href').replace('0', newId)+"&_popup=1").html(gettext('Edit'));
    }
    yawdadmin.jQuery.fancybox.close();
    yawdadmin.jQuery.popupTriggeringLink = null;
}

function dismissEditPopupInline(win, newId, newRepr) {
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var elem = (yawdadmin.jQuery.popupInlineTriggeringLink) ?
    		yawdadmin.jQuery.popupInlineTriggeringLink : null;
    if (elem)
    	elem.parent().siblings('.inline_label').html(newRepr);
    yawdadmin.jQuery.fancybox.close();
    yawdadmin.jQuery.popupTriggeringLink = null;
}

var affix_offset = {
	top: function () {
		if (yawdadmin.jQuery('.affix-main:visible').length == 0)
			return yawdadmin.jQuery('.affix-sidebar').offset().top;
		return yawdadmin.jQuery('.affix-main:visible').offset().top - 60;
	}
};

function collapse_switcher(el, target_selector) {
	$target = yawdadmin.jQuery(target_selector).slideToggle();
	$icon = yawdadmin.jQuery(el).find('i.h2-icon');
	if ($icon.hasClass('icon-arrow-down')) $icon.addClass('icon-arrow-up').removeClass('icon-arrow-down');
	else $icon.addClass('icon-arrow-down').removeClass('icon-arrow-up');
}

(function($){ 
	$(document).ready( function() {
		$('.add-another, .related-lookup').each(function() {
			var href = this.href;
			var self = $(this);
			
			if (self.hasClass('add-another')) {
				href += (href.indexOf('?') == -1) ? '?_popup=1' : '&_popup=1';
			} else if (self.hasClass('related-lookup')) {
				//TODO: Drop support for old popup in next versions
				href += (href.indexOf('?') == -1) ? '?'+rel_lookup_popup_var+'=1' : '&'+rel_lookup_popup_var+'=1';
			}
			
			self.attr('data-fancybox-type','iframe').attr('href', href).fancybox();
		});
		
		$('body').popover({selector:'.help',
				html: true,
				trigger: 'click',
				placement: function (tip, element) {
					$container = $(element).closest('.modal');
					if ($container.length) {
						var eloffset = $(element).offset();
						var coffset = $container.offset();
						var offset = {top: eloffset.top - coffset.top,
								left: eloffset.left - coffset.left}
						height = $container.outerHeight();
						width = $container.outerWidth();
						vert = 0.5 * height - offset.top;
						vertPlacement = vert > 0 ? 'bottom' : 'top';
						horiz = 0.5 * width - offset.left;
						horizPlacement = horiz > 0 ? 'right' : 'left';
						placement = Math.abs(horiz) > Math.abs(vert) ?  horizPlacement : vertPlacement;
						return placement;
					}
					return 'right';
				}
		});
	});
})(yawdadmin.jQuery);
