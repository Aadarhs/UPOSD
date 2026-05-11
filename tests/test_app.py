import unittest

from uposd import create_app, db


class UPOSDAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "WTF_CSRF_ENABLED": False,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SECRET_KEY": "test-secret",
                "INITIAL_ADMIN_USERNAME": "admin",
                "INITIAL_ADMIN_PASSWORD": "admin123",
            }
        )
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self):
        return self.client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=True,
        )

    def test_login_and_dashboard(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enterprise Cybersecurity Dashboard", response.data)

    def test_scan_api_requires_auth(self):
        response = self.client.post("/api/scans/start", json={"target": "127.0.0.1"})
        self.assertEqual(response.status_code, 302)

    def test_scan_api_with_auth(self):
        self.login()
        response = self.client.post("/api/scans/start", json={"target": "127.0.0.1"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["mode"], "safe-demo")


if __name__ == "__main__":
    unittest.main()
