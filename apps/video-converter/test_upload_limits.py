import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


class UploadLimitsTest(unittest.TestCase):
    def test_legacy_settings_use_small_requests_and_replayed_chunks_assemble(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            env = {"CHUNK_UPLOAD_MB": "24", "DIRECT_UPLOAD_MB": "95",
                   "UPLOADS_DIR": str(root / "uploads"),
                   "DOWNLOAD_DIR": str(root / "downloads"),
                   "CHUNK_UPLOADS_DIR": str(root / "chunks"), "FILE_TTL_SECONDS": "0"}
            with patch.dict(os.environ, env):
                spec = importlib.util.spec_from_file_location("upload_limits_app", Path(__file__).with_name("app.py"))
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
            self.assertEqual(module.CHUNK_UPLOAD_MB, 4)
            self.assertEqual(module.DIRECT_UPLOAD_MB, 4)
            client = module.app.test_client()
            page = client.get("/").get_data(as_text=True)
            self.assertIn("const CHUNK_UPLOAD_MB = 4;", page)
            self.assertIn("const DIRECT_UPLOAD_MB = 4;", page)
            parts = [b"first part", b"second part"]
            for index in (0, 1, 1):
                response = client.post("/api/upload-chunk", data={
                    "upload_id": "test-small-request", "filename": "probe.mkv",
                    "chunk_index": str(index), "total_chunks": "2",
                    "chunk": (io.BytesIO(parts[index]), "probe.mkv")})
                self.assertEqual(response.status_code, 200)
            # Old tabs remain valid: request acceptance is not reduced to 4 MB.
            legacy = b"x" * (5 * 1024 * 1024)
            response = client.post("/api/upload-chunk", data={
                "upload_id": "legacy-tab", "filename": "legacy.mkv",
                "chunk_index": "0", "total_chunks": "1",
                "chunk": (io.BytesIO(legacy), "legacy.mkv")})
            self.assertEqual(response.status_code, 200)
            legacy_output = root / "legacy.mkv"
            module.assemble_upload("legacy-tab", legacy_output)
            self.assertEqual(legacy_output.read_bytes(), legacy)
            destination = root / "assembled.mkv"
            module.assemble_upload("test-small-request", destination)
            self.assertEqual(destination.read_bytes(), b"".join(parts))


if __name__ == "__main__":
    unittest.main()
