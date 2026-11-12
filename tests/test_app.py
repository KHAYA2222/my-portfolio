import os
import re
from smtplib import SMTPException
import unittest
from unittest.mock import patch

with patch.dict(os.environ, {
    'SECRET_KEY': 'test-only-not-for-deployment',
    'MAIL_USERNAME': 'portfolio@example.com',
    'MAIL_PASSWORD': 'test-only',
}):
    from app import app, mail


class ContactTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, CONTACT_ENABLED=True)
        self.client = app.test_client()
        self.send = self.enterContext(patch.object(mail, 'send'))

    def payload(self):
        response = self.client.get('/')
        token = re.search(
            r'name="csrf_token"[^>]*value="([^"]+)"',
            response.get_data(as_text=True),
        ).group(1)
        return {
            'csrf_token': token,
            'name': '  Portfolio Visitor  ',
            'email': 'visitor@example.com',
            'subject': '  Project opportunity  ',
            'message': 'Hello! I would like to discuss a project.',
        }

    def test_home_and_local_assets_render(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Cloud engineer. Backend developer.', html)
        assets = re.findall(r'(?:src|href)="(/static/[^"]+)"', html)
        self.assertEqual(len([url for url in assets if 'style.css' in url]), 1)
        for asset in assets:
            with self.subTest(asset=asset):
                with self.client.get(asset) as asset_response:
                    self.assertEqual(asset_response.status_code, 200)

    def test_valid_submission_sends_once_and_redirects(self):
        response = self.client.post('/submit', data=self.payload())
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.location.endswith('/#contact'))
        self.send.assert_called_once()
        message = self.send.call_args.args[0]
        self.assertEqual(message.reply_to, 'visitor@example.com')
        self.assertEqual(message.subject, 'New Contact Form Submission: Project opportunity')
        self.assertIn('Name: Portfolio Visitor\n', message.body)
        landing = self.client.get(response.location)
        self.assertIn(b'Thank you! Your message has been sent.', landing.data)
        self.client.get('/')
        self.send.assert_called_once()

    def test_invalid_fields_never_send(self):
        invalid_values = [
            ('name', ''), ('name', '   '), ('name', 'x' * 101),
            ('name', 'Name\r\nInjected'),
            ('email', 'not-an-email'), ('email', 'a@example.com\r\nBcc: b@example.com'),
            ('subject', '   '), ('subject', 'x' * 151),
            ('subject', 'Hello\r\nBcc: injected@example.com'),
            ('message', '   '), ('message', 'x' * 5001),
        ]
        for field, value in invalid_values:
            with self.subTest(field=field, value=value[:30]):
                payload = self.payload()
                payload[field] = value
                response = self.client.post('/submit', data=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn(f'id="{field}-error"'.encode(), response.data)
        self.send.assert_not_called()

    def test_missing_fields_are_reported_instead_of_bad_request_page(self):
        token = self.payload()['csrf_token']
        response = self.client.post('/submit', data={'csrf_token': token})
        self.assertEqual(response.status_code, 400)
        for field in ('name', 'email', 'subject', 'message'):
            self.assertIn(f'id="{field}-error"'.encode(), response.data)
        self.send.assert_not_called()

    def test_csrf_required_and_bound_to_browser_session(self):
        payload = self.payload()
        for token in ('', 'invalid-token', payload['csrf_token']):
            with self.subTest(token=token):
                other_client = app.test_client()
                response = other_client.post('/submit', data={**payload, 'csrf_token': token})
                self.assertEqual(response.status_code, 400)
                self.assertIn(b'could not be verified', response.data)
        self.send.assert_not_called()

    def test_delivery_failure_keeps_escaped_draft_and_reports_error(self):
        for error in (SMTPException('SMTP unavailable'), OSError('Connection failed')):
            with self.subTest(error=type(error).__name__):
                self.send.side_effect = error
                payload = self.payload()
                payload['message'] = '<script>alert("draft")</script>'
                with self.assertLogs(app.logger, level='ERROR'):
                    response = self.client.post('/submit', data=payload)
                self.assertEqual(response.status_code, 503)
                self.assertIn(b'Your message could not be sent.', response.data)
                self.assertIn(b'&lt;script&gt;', response.data)
                self.assertNotIn(b'<script>alert', response.data)
                self.assertNotIn(b'Thank you!', response.data)

    def test_unconfigured_mail_keeps_portfolio_available(self):
        with patch.dict(app.config, {'CONTACT_ENABLED': False}):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'contact form is currently unavailable', response.data)
            self.assertNotIn(b'id="contactForm"', response.data)
            response = self.client.post('/submit', data={})
            self.assertEqual(response.status_code, 503)
            self.send.assert_not_called()

    def test_oversized_request_has_helpful_response(self):
        response = self.client.post('/submit', data={'message': 'x' * 40000})
        self.assertEqual(response.status_code, 413)
        self.assertIn(b'Your message is too large.', response.data)
        self.send.assert_not_called()


if __name__ == '__main__':
    unittest.main()
