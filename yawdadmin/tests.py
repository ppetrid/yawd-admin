from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase, TestCase


class PatientWebDriver(WebDriver):
    
    def element_exists(self, css):
        """
        Checks if a certain element exists in the DOM Tree.
        """
        try:
            return self.find_element_by_css_selector(css)
        except NoSuchElementException:
            return False
    
    def find_css(self, css_selector):
        """
        Shortcut to find elements by CSS. Returns either a list or
        singleton
        """
        elems = self.find_elements_by_css_selector(css_selector)
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            raise NoSuchElementException(css_selector)
        return elems

    def wait_for_css(self, css_selector, timeout=7):
        """
        Shortcut for WebDriverWait
        """
        return WebDriverWait(self, timeout).until(lambda driver : driver.find_css(css_selector))


class BaseSeleniumTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.selenium = PatientWebDriver()
        super(BaseSeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(BaseSeleniumTestCase, cls).tearDownClass()

    def open(self, url):
        self.selenium.get("%s%s" % (self.live_server_url, url))

 
class YawdAdminBaseSeleniumTestCase(BaseSeleniumTestCase):
    username = ''
    password = ''

    def add_inline(self, prefix):
        last = int(self.selenium.find_css('#%s-wrapper .inline-related' % prefix)[-2].get_attribute('id').replace('%s-' % prefix, ''))
        self.selenium.find_css('#%s-wrapper .add-row a' % prefix).click()
        WebDriverWait(self.selenium, 10).until(lambda d: d.element_exists('#%s-%s' % (prefix, (last+1))))
        return last + 1

    def close_modal_inline(self, prefix):
        self.selenium.find_css('#modal-wrapper-%s .modal-footer button' % prefix).click()
        WebDriverWait(self.selenium, 10).until(lambda d: not d.find_css('#modal-wrapper-%s' % prefix).is_displayed())

    def fill_modal_inlines(self, prefix, callback, items, add=True):
        """
        if `add` is set to False, the modal form is expected to exist
        in the DOM, otherwise the 'Add another inline' link will be clicked.
        
        You can provide an empty dict among the items list. For example
        if you don't want the second inline to be edited, your items list
        could look like this:
        
        .. code-block:: python
            items = [{'title': 'whatever', ... },
                    {},
                    {'title': 'whatever'}]

        """
        c=0
        for i in items:
            if i:
                self.open_modal_inline('%s-%s' % (prefix, c))
                callback(inline_prefix=c, **i)
                self.close_modal_inline('%s-%s' % (prefix, c))
            if add:
                c = self.add_inline(prefix)
            else:
                c += 1

    def fill_input_text(self, el, value):
        el.clear()
        el.send_keys(value)

    def login(self):
        self.open(reverse('admin:index'))
        self.selenium.find_css('#id_username').send_keys(self.username)
        self.selenium.find_css('#id_password').send_keys(self.password)
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
        self.selenium.wait_for_css("#content-main")
        
    def logout(self):
        self.selenium.find_css('#logged-user-menu .dropdown-toggle').click()
        self.selenium.find_css('#logout-link').click()
        self.selenium.wait_for_css('.page-header')

    def open_modal_inline(self, prefix):
        self.selenium.find_element_by_xpath('//a[@class="inline-modal" and @href="#modal-wrapper-%s"]' % prefix).click()
        WebDriverWait(self.selenium, 10).until(lambda d: d.find_css('#modal-wrapper-%s' % prefix).is_displayed())

    def save_and_continue(self):
        self.selenium.find_css('input[name="_continue"]').click()
        self.selenium.wait_for_css("#content-main")

    def save(self):
        self.selenium.find_css('input[name="_save"]').click()
        self.selenium.wait_for_css("#content-main")
        
    def delete(self):
        self.selenium.find_element_by_xpath('//a[text()="Delete" and contains(@class, "deletelink")]').click()
        self.selenium.wait_for_css("#content-main")
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.selenium.wait_for_css("#content-main")
    
    def do_action(self, value):
        action_select = Select(self.selenium.find_css('select[name="action"]'))
        action_select.select_by_value(value)
        self.selenium.find_css('button[name="index"]').click()
        self.selenium.wait_for_css("#content-main")
        
    def check_selected_action(self, id):
        self.selenium.wait_for_css('input[name="_selected_action"]')
        self.selenium.find_element_by_xpath('//input[@value="%s" and @name="_selected_action"]' % id).click()
        
    def confirm_action(self):
        self.selenium.find_css('input[type="submit"]').click()
        self.selenium.wait_for_css('#content-main')

class PermissionTestCase(TestCase):
    """
    Check all standard admin views of a model, all expected to return
    a specific status (e.g. 200 on success, 403 on permission denied).
    """

    def naive_admin_check(self, model_prefix, expected_status, item=1):
        response = self.client.get(reverse('admin:%s_changelist' % model_prefix))
        self.assertEqual(response.status_code, expected_status)
        response = self.client.get(reverse('admin:%s_change' % model_prefix, args=(item,)))
        self.assertEqual(response.status_code, expected_status)
        response = self.client.get(reverse('admin:%s_history' % model_prefix, args=(item,)))
        self.assertEqual(response.status_code, expected_status)
        response = self.client.get(reverse('admin:%s_delete' % model_prefix, args=(item,)))
        self.assertEqual(response.status_code, expected_status)
        response = self.client.get(reverse('admin:%s_add' % model_prefix))
        self.assertEqual(response.status_code, expected_status)
