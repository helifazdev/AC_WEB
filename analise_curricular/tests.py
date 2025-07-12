# tests.py
from django.core.files.uploadedfile import SimpleUploadedFile

class DocumentoTests(TestCase):
    def test_upload(self):
        arquivo = SimpleUploadedFile("test.pdf", b"file_content")
        response = self.client.post('/upload/', {'arquivo': arquivo})
        self.assertEqual(response.status_code, 200)