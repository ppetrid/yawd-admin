# -*- coding: utf-8 -*-
class PopupMiddleware(object):
    """
    This middleware must always be enabled when using yawd-admin WITH
    DJANGO < 1.6.
    Place it **before** the :class:`django.middleware.common.CommonMiddleware`
    in your ``MIDLEWARE_CLASSESS`` setting.

    yawd-admin builds upon the original django admin application.
    Some admin widgets open pop-up windows where yawd-admin uses
    a modal window. Since original AdminModel views attempt to return
    pop-up window values to the parent through the ``opener`` javascript
    variable, the iframes used in yawd-elfinder will not work as expected.
    This middleare implements an easy fix, replacing ``opener`` with
    the ``parent`` variable, which is appropriate for iframes.
    """
    def process_response(self, request, resp):
        """
        This method is called right after a view is processed and has
        returned an HttpResponse object.
        """

        #responses will not always have a content attribute starting
        #from Django 1.5
        if resp.status_code == 200 and \
            hasattr(resp, 'content') and \
            resp.content.startswith('<!DOCTYPE html><html><head>'
                                    '<title></title></head><body>'
                                    '<script type="text/javascript">'
                                    'opener.dismissAddAnotherPopup(window,'):

            resp.content = resp.content.\
                replace('<!DOCTYPE html><html><head><title></title></head>'
                        '<body><script type="text/javascript">'
                        'opener.dismissAddAnotherPopup(window,',
                        '<!DOCTYPE html><html><head><title></title></head>'
                        '<body><script>parent.dismissAddAnotherPopup(window,')
        return resp
