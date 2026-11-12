import threading
import unittest
from unittest.mock import patch

from playwright.sync_api import sync_playwright, expect
from werkzeug.serving import make_server

from test_app import app, mail


class BrowserChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, CONTACT_ENABLED=True)
        cls.mail_patch = patch.object(mail, 'send')
        cls.send = cls.mail_patch.start()
        cls.addClassCleanup(cls.mail_patch.stop)
        cls.server = make_server('127.0.0.1', 0, app)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def setUp(self):
        self.send.reset_mock(side_effect=True)
        self.context = self.browser.new_context()
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('console', lambda message: self.errors.append(message.text)
                     if message.type == 'error' else None)

    def test_responsive_layout_and_local_assets(self):
        for width in (320, 375, 768, 1024, 1440):
            with self.subTest(width=width):
                self.page.set_viewport_size({'width': width, 'height': 900})
                self.page.goto(self.url)
                self.assertTrue(self.page.evaluate(
                    'document.documentElement.scrollWidth <= window.innerWidth'
                ))
                self.page.locator('#projects').scroll_into_view_if_needed()
                expect(self.page.locator('.project-card').first).to_have_css('opacity', '1')
                self.assertTrue(self.page.locator('.project-card').evaluate_all(
                    '(cards) => cards.every(card => card.getBoundingClientRect().width >= 270)'
                ))
                self.page.locator('#contact').scroll_into_view_if_needed()
                expect(self.page.get_by_role('textbox', name='Email', exact=True)).to_be_visible()
                self.assertTrue(self.page.locator('img').evaluate_all(
                    '(images) => images.every(image => image.complete && image.naturalWidth > 0)'
                ))
        self.assertEqual(self.errors, [])

    def test_mobile_menu_and_back_to_top(self):
        self.page.set_viewport_size({'width': 375, 'height': 812})
        self.page.goto(self.url)
        toggle = self.page.get_by_role('button', name='Toggle navigation', include_hidden=True)
        menu = self.page.locator('#navLinks')
        expect(menu).to_be_hidden()
        toggle.click()
        expect(menu).to_be_visible()
        expect(toggle).to_have_attribute('aria-expanded', 'true')
        self.page.keyboard.press('Escape')
        expect(menu).to_be_hidden()
        expect(toggle).to_be_focused()
        toggle.click()
        menu.get_by_role('link', name='Projects', exact=True).click()
        expect(menu).to_be_hidden()
        expect(toggle).to_have_attribute('aria-expanded', 'false')
        expect(self.page.get_by_role('link', name='Back to top')).to_be_visible()
        self.page.get_by_role('link', name='Back to top').click()
        self.page.wait_for_function('window.scrollY < 100')
        toggle.click()
        self.page.set_viewport_size({'width': 1024, 'height': 900})
        expect(toggle).to_have_attribute('aria-expanded', 'false')
        self.page.set_viewport_size({'width': 375, 'height': 812})
        expect(menu).to_be_hidden()
        self.assertEqual(self.errors, [])

    def test_no_javascript_and_reduced_motion(self):
        with self.browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 800}) as context:
            page = context.new_page()
            page.goto(self.url)
            expect(page.locator('#navLinks')).to_be_visible()
            expect(page.locator('.nav-toggle')).to_be_hidden()
            expect(page.locator('.hero-role')).to_contain_text('Cloud engineer.')
            for selector in ('.about-text', '.project-card', '.timeline-item', '.contact-form'):
                expect(page.locator(selector).first).to_have_css('opacity', '1')
            self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            expect(page.get_by_label('Name', exact=True)).to_have_attribute('required', '')
        self.page.emulate_media(reduced_motion='reduce')
        self.page.goto(self.url)
        expect(self.page.locator('.reveal-pending')).to_have_count(0)
        expect(self.page.locator('html')).to_have_css('scroll-behavior', 'auto')
        self.assertEqual(self.errors, [])

    def test_contact_browser_validation_and_success(self):
        self.page.goto(f'{self.url}/#contact')
        button = self.page.get_by_role('button', name='Send Message')
        button.click()
        self.send.assert_not_called()
        self.page.get_by_label('Name', exact=True).fill('Browser Visitor')
        self.page.get_by_role('textbox', name='Email', exact=True).fill('visitor@example.com')
        self.page.get_by_label('Subject', exact=True).fill('Portfolio opportunity')
        self.page.get_by_label('Message', exact=True).fill('Hello from the browser regression check.')
        button.click()
        expect(self.page.get_by_role('status')).to_contain_text('Your message has been sent.')
        expect(self.page.get_by_role('status')).to_be_in_viewport()
        self.send.assert_called_once()
        expect(self.page.get_by_label('Message', exact=True)).to_have_value('')
        self.page.reload()
        self.send.assert_called_once()
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
