/*
 * jQuery UI Nested Sortable
 * v 1.3.5 / 21 jun 2012
 * http://mjsarfatti.com/code/nestedSortable
 *
 * Depends on:
 *	 jquery.ui.sortable.js 1.8+
 *
 * Copyright (c) 2010-2012 Manuele J Sarfatti
 * Licensed under the MIT License
 * http://www.opensource.org/licenses/mit-license.php
 */

(function($) {

	$.widget("mjs.nestedSortable", $.extend({}, $.ui.sortable.prototype, {

		options: {
			tabSize: 20,
			disableNesting: 'mjs-nestedSortable-no-nesting',
			errorClass: 'mjs-nestedSortable-error',
			doNotClear: false,
			listType: 'ol',
			maxLevels: 0,
			protectRoot: false,
			rootID: null,
			rtl: false,
			isAllowed: function(item, parent) { return true; }
		},

		_create: function() {
			this.element.data('sortable', this.element.data('nestedSortable'));

			if (!this.element.is(this.options.listType))
				throw new Error('nestedSortable: Please check the listType option is set to your actual list type');

			return $.ui.sortable.prototype._create.apply(this, arguments);
		},

		destroy: function() {
			this.element
				.removeData("nestedSortable")
				.unbind(".nestedSortable");
			return $.ui.sortable.prototype.destroy.apply(this, arguments);
		},

		_mouseDrag: function(event) {

			//Compute the helpers position
			this.position = this._generatePosition(event);
			this.positionAbs = this._convertPositionTo("absolute");

			if (!this.lastPositionAbs) {
				this.lastPositionAbs = this.positionAbs;
			}

			var o = this.options;

			//Do scrolling
			if(this.options.scroll) {
				var scrolled = false;
				if(this.scrollParent[0] != document && this.scrollParent[0].tagName != 'HTML') {

					if((this.overflowOffset.top + this.scrollParent[0].offsetHeight) - event.pageY < o.scrollSensitivity)
						this.scrollParent[0].scrollTop = scrolled = this.scrollParent[0].scrollTop + o.scrollSpeed;
					else if(event.pageY - this.overflowOffset.top < o.scrollSensitivity)
						this.scrollParent[0].scrollTop = scrolled = this.scrollParent[0].scrollTop - o.scrollSpeed;

					if((this.overflowOffset.left + this.scrollParent[0].offsetWidth) - event.pageX < o.scrollSensitivity)
						this.scrollParent[0].scrollLeft = scrolled = this.scrollParent[0].scrollLeft + o.scrollSpeed;
					else if(event.pageX - this.overflowOffset.left < o.scrollSensitivity)
						this.scrollParent[0].scrollLeft = scrolled = this.scrollParent[0].scrollLeft - o.scrollSpeed;

				} else {

					if(event.pageY - $(document).scrollTop() < o.scrollSensitivity)
						scrolled = $(document).scrollTop($(document).scrollTop() - o.scrollSpeed);
					else if($(window).height() - (event.pageY - $(document).scrollTop()) < o.scrollSensitivity)
						scrolled = $(document).scrollTop($(document).scrollTop() + o.scrollSpeed);

					if(event.pageX - $(document).scrollLeft() < o.scrollSensitivity)
						scrolled = $(document).scrollLeft($(document).scrollLeft() - o.scrollSpeed);
					else if($(window).width() - (event.pageX - $(document).scrollLeft()) < o.scrollSensitivity)
						scrolled = $(document).scrollLeft($(document).scrollLeft() + o.scrollSpeed);

				}

				if(scrolled !== false && $.ui.ddmanager && !o.dropBehaviour)
					$.ui.ddmanager.prepareOffsets(this, event);
			}

			//Regenerate the absolute position used for position checks
			this.positionAbs = this._convertPositionTo("absolute");

      // Find the top offset before rearrangement,
      var previousTopOffset = this.placeholder.offset().top;

			//Set the helper position
			if(!this.options.axis || this.options.axis != "y") this.helper[0].style.left = this.position.left+'px';
			if(!this.options.axis || this.options.axis != "x") this.helper[0].style.top = this.position.top+'px';

			//Rearrange
			for (var i = this.items.length - 1; i >= 0; i--) {

				//Cache variables and intersection, continue if no intersection
				var item = this.items[i], itemElement = item.item[0], intersection = this._intersectsWithPointer(item);
				if (!intersection) continue;

				if(itemElement != this.currentItem[0] //cannot intersect with itself
					&&	this.placeholder[intersection == 1 ? "next" : "prev"]()[0] != itemElement //no useless actions that have been done before
					&&	!$.contains(this.placeholder[0], itemElement) //no action if the item moved is the parent of the item checked
					&& (this.options.type == 'semi-dynamic' ? !$.contains(this.element[0], itemElement) : true)
					//&& itemElement.parentNode == this.placeholder[0].parentNode // only rearrange items within the same container
				) {

					$(itemElement).mouseenter();

					this.direction = intersection == 1 ? "down" : "up";

					if (this.options.tolerance == "pointer" || this._intersectsWithSides(item)) {
						$(itemElement).mouseleave();
						this._rearrange(event, item);
					} else {
						break;
					}

					// Clear emtpy ul's/ol's
					this._clearEmpty(itemElement);

					this._trigger("change", event, this._uiHash());
					break;
				}
			}

			var parentItem = (this.placeholder[0].parentNode.parentNode &&
							 $(this.placeholder[0].parentNode.parentNode).closest('.ui-sortable').length)
				       			? $(this.placeholder[0].parentNode.parentNode)
				       			: null,
			    level = this._getLevel(this.placeholder),
			    childLevels = this._getChildLevels(this.helper);

      // To find the previous sibling in the list, keep backtracking until we hit a valid list item.
			var previousItem = this.placeholder[0].previousSibling ? $(this.placeholder[0].previousSibling) : null;
			if (previousItem != null) {
				while (previousItem[0].nodeName.toLowerCase() != 'li' || previousItem[0] == this.currentItem[0] || previousItem[0] == this.helper[0]) {
					if (previousItem[0].previousSibling) {
						previousItem = $(previousItem[0].previousSibling);
					} else {
						previousItem = null;
						break;
					}
				}
			}

      // To find the next sibling in the list, keep stepping forward until we hit a valid list item.
      var nextItem = this.placeholder[0].nextSibling ? $(this.placeholder[0].nextSibling) : null;
      if (nextItem != null) {
        while (nextItem[0].nodeName.toLowerCase() != 'li' || nextItem[0] == this.currentItem[0] || nextItem[0] == this.helper[0]) {
          if (nextItem[0].nextSibling) {
            nextItem = $(nextItem[0].nextSibling);
          } else {
            nextItem = null;
            break;
          }
        }
      }

			var newList = document.createElement(o.listType);

			this.beyondMaxLevels = 0;

			// If the item is moved to the left, send it to its parent's level unless there are siblings below it.
			if (parentItem != null && nextItem == null &&
					(o.rtl && (this.positionAbs.left + this.helper.outerWidth() > parentItem.offset().left + parentItem.outerWidth()) ||
					!o.rtl && (this.positionAbs.left < parentItem.offset().left))) {
				parentItem.after(this.placeholder[0]);
				this._clearEmpty(parentItem[0]);
				this._trigger("change", event, this._uiHash());
			}
			// If the item is below a sibling and is moved to the right, make it a child of that sibling.
			else if (previousItem != null &&
						(o.rtl && (this.positionAbs.left + this.helper.outerWidth() < previousItem.offset().left + previousItem.outerWidth() - o.tabSize) ||
						!o.rtl && (this.positionAbs.left > previousItem.offset().left + o.tabSize))) {
				this._isAllowed(previousItem, level, level+childLevels+1);
				if (!previousItem.children(o.listType).length) {
					previousItem[0].appendChild(newList);
				}
        // If this item is being moved from the top, add it to the top of the list.
        if (previousTopOffset && (previousTopOffset <= previousItem.offset().top)) {
          previousItem.children(o.listType).prepend(this.placeholder);
        }
        // Otherwise, add it to the bottom of the list.
        else {
				  previousItem.children(o.listType)[0].appendChild(this.placeholder[0]);
        }
				this._trigger("change", event, this._uiHash());
			}
			else {
				this._isAllowed(parentItem, level, level+childLevels);
			}

			//Post events to containers
			this._contactContainers(event);

			//Interconnect with droppables
			if($.ui.ddmanager) $.ui.ddmanager.drag(this, event);

			//Call callbacks
			this._trigger('sort', event, this._uiHash());

			this.lastPositionAbs = this.positionAbs;
			return false;

		},

		_mouseStop: function(event, noPropagation) {

			// If the item is in a position not allowed, send it back
			if (this.beyondMaxLevels) {

				this.placeholder.removeClass(this.options.errorClass);

				if (this.domPosition.prev) {
					$(this.domPosition.prev).after(this.placeholder);
				} else {
					$(this.domPosition.parent).prepend(this.placeholder);
				}

				this._trigger("revert", event, this._uiHash());

			}

			// Clean last empty ul/ol
			for (var i = this.items.length - 1; i >= 0; i--) {
				var item = this.items[i].item[0];
				this._clearEmpty(item);
			}

			$.ui.sortable.prototype._mouseStop.apply(this, arguments);

		},

		serialize: function(options) {

			var o = $.extend({}, this.options, options),
				items = this._getItemsAsjQuery(o && o.connected),
			    str = [];

			$(items).each(function() {
				var res = ($(o.item || this).attr(o.attribute || 'id') || '')
						.match(o.expression || (/(.+)[-=_](.+)/)),
				    pid = ($(o.item || this).parent(o.listType)
						.parent(o.items)
						.attr(o.attribute || 'id') || '')
						.match(o.expression || (/(.+)[-=_](.+)/));

				if (res) {
					str.push(((o.key || res[1]) + '[' + (o.key && o.expression ? res[1] : res[2]) + ']')
						+ '='
						+ (pid ? (o.key && o.expression ? pid[1] : pid[2]) : o.rootID));
				}
			});

			if(!str.length && o.key) {
				str.push(o.key + '=');
			}

			return str.join('&');

		},

		toHierarchy: function(options) {

			var o = $.extend({}, this.options, options),
				sDepth = o.startDepthCount || 0,
			    ret = [];

			$(this.element).children(o.items).each(function () {
				var level = _recursiveItems(this);
				ret.push(level);
			});

			return ret;

			function _recursiveItems(item) {
				var id = ($(item).attr(o.attribute || 'id') || '').match(o.expression || (/(.+)[-=_](.+)/));
				if (id) {
					var currentItem = {"id" : id[2]};
					if ($(item).children(o.listType).children(o.items).length > 0) {
						currentItem.children = [];
						$(item).children(o.listType).children(o.items).each(function() {
							var level = _recursiveItems(this);
							currentItem.children.push(level);
						});
					}
					return currentItem;
				}
			}
		},

		toArray: function(options) {

			var o = $.extend({}, this.options, options),
				sDepth = o.startDepthCount || 0,
			    ret = [],
			    left = 2;

			ret.push({
				"item_id": o.rootID,
				"parent_id": 'none',
				"depth": sDepth,
				"left": '1',
				"right": ($(o.items, this.element).length + 1) * 2
			});

			$(this.element).children(o.items).each(function () {
				left = _recursiveArray(this, sDepth + 1, left);
			});

			ret = ret.sort(function(a,b){ return (a.left - b.left); });

			return ret;

			function _recursiveArray(item, depth, left) {

				var right = left + 1,
				    id,
				    pid;

				if ($(item).children(o.listType).children(o.items).length > 0) {
					depth ++;
					$(item).children(o.listType).children(o.items).each(function () {
						right = _recursiveArray($(this), depth, right);
					});
					depth --;
				}

				id = ($(item).attr(o.attribute || 'id')).match(o.expression || (/(.+)[-=_](.+)/));

				if (depth === sDepth + 1) {
					pid = o.rootID;
				} else {
					var parentItem = ($(item).parent(o.listType)
											 .parent(o.items)
											 .attr(o.attribute || 'id'))
											 .match(o.expression || (/(.+)[-=_](.+)/));
					pid = parentItem[2];
				}

				if (id) {
						ret.push({"item_id": id[2], "parent_id": pid, "depth": depth, "left": left, "right": right});
				}

				left = right + 1;
				return left;
			}

		},

		_clearEmpty: function(item) {

			var emptyList = $(item).children(this.options.listType);
			if (emptyList.length && !emptyList.children().length && !this.options.doNotClear) {
				emptyList.remove();
			}

		},

		_getLevel: function(item) {

			var level = 1;

			if (this.options.listType) {
				var list = item.closest(this.options.listType);
				while (list && list.length > 0 && 
                    	!list.is('.ui-sortable')) {
					level++;
					list = list.parent().closest(this.options.listType);
				}
			}

			return level;
		},

		_getChildLevels: function(parent, depth) {
			var self = this,
			    o = this.options,
			    result = 0;
			depth = depth || 0;

			$(parent).children(o.listType).children(o.items).each(function (index, child) {
					result = Math.max(self._getChildLevels(child, depth + 1), result);
			});

			return depth ? result + 1 : result;
		},

		_isAllowed: function(parentItem, level, levels) {
			var o = this.options,
				isRoot = $(this.domPosition.parent).hasClass('ui-sortable') ? true : false,
				maxLevels = this.placeholder.closest('.ui-sortable').nestedSortable('option', 'maxLevels'); // this takes into account the maxLevels set to the recipient list

			// Is the root protected?
			// Are we trying to nest under a no-nest?
			// Are we nesting too deep?
			if (!o.isAllowed(this.currentItem, parentItem) ||
				parentItem && parentItem.hasClass(o.disableNesting) ||
				o.protectRoot && (parentItem == null && !isRoot || isRoot && level > 1)) {
					this.placeholder.addClass(o.errorClass);
					if (maxLevels < levels && maxLevels != 0) {
						this.beyondMaxLevels = levels - maxLevels;
					} else {
						this.beyondMaxLevels = 1;
					}
			} else {
				if (maxLevels < levels && maxLevels != 0) {
					this.placeholder.addClass(o.errorClass);
					this.beyondMaxLevels = levels - maxLevels;
				} else {
					this.placeholder.removeClass(o.errorClass);
					this.beyondMaxLevels = 0;
				}
			}
		}

	}));

	$.mjs.nestedSortable.prototype.options = $.extend({}, $.ui.sortable.prototype.options, $.mjs.nestedSortable.prototype.options);
})(yawdadmin.jQuery);

if (typeof JSON !== 'object') {
    JSON = {};
}

(function () {
    'use strict';

    function f(n) {
        // Format integers to have at least two digits.
        return n < 10 ? '0' + n : n;
    }

    if (typeof Date.prototype.toJSON !== 'function') {

        Date.prototype.toJSON = function (key) {

            return isFinite(this.valueOf())
                ? this.getUTCFullYear()     + '-' +
                    f(this.getUTCMonth() + 1) + '-' +
                    f(this.getUTCDate())      + 'T' +
                    f(this.getUTCHours())     + ':' +
                    f(this.getUTCMinutes())   + ':' +
                    f(this.getUTCSeconds())   + 'Z'
                : null;
        };

        String.prototype.toJSON      =
            Number.prototype.toJSON  =
            Boolean.prototype.toJSON = function (key) {
                return this.valueOf();
            };
    }

    var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        gap,
        indent,
        meta = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        },
        rep;


    function quote(string) {

// If the string contains no control characters, no quote characters, and no
// backslash characters, then we can safely slap some quotes around it.
// Otherwise we must also replace the offending characters with safe escape
// sequences.

        escapable.lastIndex = 0;
        return escapable.test(string) ? '"' + string.replace(escapable, function (a) {
            var c = meta[a];
            return typeof c === 'string'
                ? c
                : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
        }) + '"' : '"' + string + '"';
    }


    function str(key, holder) {

// Produce a string from holder[key].

        var i,          // The loop counter.
            k,          // The member key.
            v,          // The member value.
            length,
            mind = gap,
            partial,
            value = holder[key];

// If the value has a toJSON method, call it to obtain a replacement value.

        if (value && typeof value === 'object' &&
                typeof value.toJSON === 'function') {
            value = value.toJSON(key);
        }

// If we were called with a replacer function, then call the replacer to
// obtain a replacement value.

        if (typeof rep === 'function') {
            value = rep.call(holder, key, value);
        }

// What happens next depends on the value's type.

        switch (typeof value) {
        case 'string':
            return quote(value);

        case 'number':

// JSON numbers must be finite. Encode non-finite numbers as null.

            return isFinite(value) ? String(value) : 'null';

        case 'boolean':
        case 'null':

// If the value is a boolean or null, convert it to a string. Note:
// typeof null does not produce 'null'. The case is included here in
// the remote chance that this gets fixed someday.

            return String(value);

// If the type is 'object', we might be dealing with an object or an array or
// null.

        case 'object':

// Due to a specification blunder in ECMAScript, typeof null is 'object',
// so watch out for that case.

            if (!value) {
                return 'null';
            }

// Make an array to hold the partial results of stringifying this object value.

            gap += indent;
            partial = [];

// Is the value an array?

            if (Object.prototype.toString.apply(value) === '[object Array]') {

// The value is an array. Stringify every element. Use null as a placeholder
// for non-JSON values.

                length = value.length;
                for (i = 0; i < length; i += 1) {
                    partial[i] = str(i, value) || 'null';
                }

// Join all of the elements together, separated with commas, and wrap them in
// brackets.

                v = partial.length === 0
                    ? '[]'
                    : gap
                    ? '[\n' + gap + partial.join(',\n' + gap) + '\n' + mind + ']'
                    : '[' + partial.join(',') + ']';
                gap = mind;
                return v;
            }

// If the replacer is an array, use it to select the members to be stringified.

            if (rep && typeof rep === 'object') {
                length = rep.length;
                for (i = 0; i < length; i += 1) {
                    if (typeof rep[i] === 'string') {
                        k = rep[i];
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + (gap ? ': ' : ':') + v);
                        }
                    }
                }
            } else {

// Otherwise, iterate through all of the keys in the object.

                for (k in value) {
                    if (Object.prototype.hasOwnProperty.call(value, k)) {
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + (gap ? ': ' : ':') + v);
                        }
                    }
                }
            }

// Join all of the member texts together, separated with commas,
// and wrap them in braces.

            v = partial.length === 0
                ? '{}'
                : gap
                ? '{\n' + gap + partial.join(',\n' + gap) + '\n' + mind + '}'
                : '{' + partial.join(',') + '}';
            gap = mind;
            return v;
        }
    }

// If the JSON object does not yet have a stringify method, give it one.

    if (typeof JSON.stringify !== 'function') {
        JSON.stringify = function (value, replacer, space) {

// The stringify method takes a value and an optional replacer, and an optional
// space parameter, and returns a JSON text. The replacer can be a function
// that can replace values, or an array of strings that will select the keys.
// A default replacer method can be provided. Use of the space parameter can
// produce text that is more easily readable.

            var i;
            gap = '';
            indent = '';

// If the space parameter is a number, make an indent string containing that
// many spaces.

            if (typeof space === 'number') {
                for (i = 0; i < space; i += 1) {
                    indent += ' ';
                }

// If the space parameter is a string, it will be used as the indent string.

            } else if (typeof space === 'string') {
                indent = space;
            }

// If there is a replacer, it must be a function or an array.
// Otherwise, throw an error.

            rep = replacer;
            if (replacer && typeof replacer !== 'function' &&
                    (typeof replacer !== 'object' ||
                    typeof replacer.length !== 'number')) {
                throw new Error('JSON.stringify');
            }

// Make a fake root object containing our value under the key of ''.
// Return the result of stringifying the value.

            return str('', {'': value});
        };
    }


// If the JSON object does not yet have a parse method, give it one.

    if (typeof JSON.parse !== 'function') {
        JSON.parse = function (text, reviver) {

// The parse method takes a text and an optional reviver function, and returns
// a JavaScript value if the text is a valid JSON text.

            var j;

            function walk(holder, key) {

// The walk method is used to recursively walk the resulting structure so
// that modifications can be made.

                var k, v, value = holder[key];
                if (value && typeof value === 'object') {
                    for (k in value) {
                        if (Object.prototype.hasOwnProperty.call(value, k)) {
                            v = walk(value, k);
                            if (v !== undefined) {
                                value[k] = v;
                            } else {
                                delete value[k];
                            }
                        }
                    }
                }
                return reviver.call(holder, key, value);
            }


// Parsing happens in four stages. In the first stage, we replace certain
// Unicode characters with escape sequences. JavaScript handles many characters
// incorrectly, either silently deleting them, or treating them as line endings.

            text = String(text);
            cx.lastIndex = 0;
            if (cx.test(text)) {
                text = text.replace(cx, function (a) {
                    return '\\u' +
                        ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
                });
            }

// In the second stage, we run the text against regular expressions that look
// for non-JSON patterns. We are especially concerned with '()' and 'new'
// because they can cause invocation, and '=' because it can cause mutation.
// But just to be safe, we want to reject all unexpected forms.

// We split the second stage into 4 regexp operations in order to work around
// crippling inefficiencies in IE's and Safari's regexp engines. First we
// replace the JSON backslash pairs with '@' (a non-JSON character). Second, we
// replace all simple value tokens with ']' characters. Third, we delete all
// open brackets that follow a colon or comma or that begin the text. Finally,
// we look to see that the remaining characters are only whitespace or ']' or
// ',' or ':' or '{' or '}'. If that is so, then the text is safe for eval.

            if (/^[\],:{}\s]*$/
                    .test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, '@')
                        .replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']')
                        .replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {

// In the third stage we use the eval function to compile the text into a
// JavaScript structure. The '{' operator is subject to a syntactic ambiguity
// in JavaScript: it can begin a block or an object literal. We wrap the text
// in parens to eliminate the ambiguity.

                j = eval('(' + text + ')');

// In the optional fourth stage, we recursively walk the new structure, passing
// each name/value pair to a reviver function for possible transformation.

                return typeof reviver === 'function'
                    ? walk({'': j}, '')
                    : j;
            }

// If the text is not JSON parseable, then a SyntaxError is thrown.

            throw new SyntaxError('JSON.parse');
        };
    }
}());

(function($) {
	$(document).ready(function() {
		$('#sortables-view').click(function() {
			$this = $(this);
			$parent = $this.parent();
			$reorderUrl = $this.data('reorder');
			if(!$parent.hasClass('active')) {
				$parent.addClass('active').siblings().removeClass('active');
				$('#content-main .results').hide();
				$('#content-main .paginator-wrapper').hide();
				//$('#changelist-sortables').siblings().css('opacity', '0.5');
				$('<div class="sortables-list"><i class="loading-item"></i></div>').insertAfter('#changelist-top');
				$.get(this.href, function(data) {
					$('#content-main .sortables-list').html('<div class="save-bar"><a class="btn btn-success" href="'
							+$reorderUrl+'"><i class="icon-save"></i> '
							+gettext('Save order')+'</a></div>'+data);
					if (recursive_sorting) {
						$('#content-main .sortables-list .root').nestedSortable({
			            	handle: 'div',
			            	items: 'li',
			            	toleranceElement: '> div',
			            	placeholder: 'placeholder',
			            	forcePlaceholderSize: true
			        	});
					} else {
						$('#content-main .sortables-list .root').sortable({
							placeholder: 'placeholder',
							forcePlaceholderSize: true
						})
					}
					$('#content-main .sortables-list .save-bar a').click(function() {
						$savebar = $(this).parent(); 
						$savebar.append('<i class="loading-item"></i>');
						var collected = [];
						$('#content-main .sortables-list .root').find('li').each(function() {
							$this = $(this);
							collected.push({
									pk: $this.data('pk'),
									order: $this.index(),
									parent: $this.parent().closest('li, .root').data('pk')
							});
						});
						$.get(this.href, {data: JSON.stringify(collected)}, function(data) {
							$savebar.append('<span class="small">&#xa0;'+data.message+'</span>').find('i').remove();
							setTimeout(function(){ $savebar.find('span').remove();}, 3000);
						}, 'json');
						return false;
					});
				}, 'html');
			}
			return false;
		});
		$('#default-view').click(function() {
			$this = $(this);
			$parent = $this.parent();
			if(!$parent.hasClass('active')) {
				$parent.addClass('active').siblings().removeClass('active');
				//$('#changelist-sortables').siblings().css('opacity', '1');
				$('#content-main .sortables-list').remove();
				$('#content-main .results').html('<i class="loading-item"></i>').show();
				$.get(this.href, window.location.search.substring(1), function(data) {
					$('#content-main .results')
						.replaceWith($(data).find('.results'));
					$('#content-main .paginator-wrapper')
						.replaceWith($(data).find('.paginator-wrapper')).show();
					try {
						$("tr input.action-select").actions(); 
					} catch(err) { ; }
				});
			}
			return false;
		});
	});
})(yawdadmin.jQuery);