"""
test_file_validation.py
-----------------------
Unit tests for orchestrator/file_validation.py (Issue #90)

Tests cover all three functions:
- sanitize_filename()
- validate_file_content()
- validate_upload_stream()

Testing only — no logic changes made to file_validation.py
"""

import pytest
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from orchestrator.file_validation import (
    sanitize_filename,
    validate_file_content,
    validate_upload_stream,
    MAX_RESUME_SIZE_BYTES,
)

# sanitize_filename() tests


class TestSanitizeFilename:

    def test_normal_filename_unchanged(self):
        """Normal filename should pass through cleanly"""
        assert sanitize_filename("resume.pdf") == "resume.pdf"

    def test_path_traversal_unix_stripped(self):
        """../../etc/passwd should become passwd"""
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_path_traversal_windows_stripped(self):
        """Windows-style path traversal should be stripped"""
        result = sanitize_filename("..\\..\\windows\\system32\\cmd.exe")
        assert ".." not in result
        assert "\\" not in result

    def test_null_bytes_removed(self):
        """Null bytes in filename should be removed"""
        result = sanitize_filename("resume\x00.pdf")
        assert "\x00" not in result

    def test_special_characters_replaced(self):
        """Special chars like spaces, @ should become underscores"""
        result = sanitize_filename("my resume @2024.pdf")
        assert " " not in result
        assert "@" not in result

    def test_leading_dots_stripped(self):
        """Hidden file attack — leading dots should be stripped"""
        result = sanitize_filename(".hidden_file.pdf")
        assert not result.startswith(".")

    def test_empty_filename_returns_default(self):
        """Empty filename should return safe default"""
        assert sanitize_filename("") == "uploaded_file.bin"

    def test_none_filename_returns_default(self):
        """None filename should return safe default"""
        assert sanitize_filename(None) == "uploaded_file.bin"

    def test_very_long_filename_truncated(self):
        """Filename over 200 chars should be truncated"""
        long_name = "a" * 250 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_valid_characters_preserved(self):
        """Letters, numbers, dots, hyphens, underscores should be kept"""
        result = sanitize_filename("My_Resume-2024.pdf")
        assert result == "My_Resume-2024.pdf"


# validate_file_content() tests


class TestValidateFileContent:

    # Valid files

    def test_valid_pdf_accepted(self):
        """Valid PDF with correct magic bytes should be accepted"""
        content = b"%PDF-1.4 This is a valid PDF content"
        ok, msg = validate_file_content(content, "resume.pdf")
        assert ok is True
        assert msg == ""

    def test_valid_txt_accepted(self):
        """Valid UTF-8 text file should be accepted"""
        content = b"Hello, I am a candidate. Here is my resume."
        ok, msg = validate_file_content(content, "resume.txt")
        assert ok is True

    # Empty file

    def test_empty_file_rejected(self):
        """Empty file should be rejected"""
        ok, msg = validate_file_content(b"", "resume.pdf")
        assert ok is False
        assert "empty" in msg.lower()

    # Invalid extension

    def test_invalid_extension_rejected(self):
        """Unsupported extension like .exe should be rejected"""
        ok, msg = validate_file_content(b"MZ\x90\x00", "malware.exe")
        assert ok is False
        assert "extension" in msg.lower()

    def test_zip_extension_rejected(self):
        """ZIP file extension should be rejected"""
        ok, msg = validate_file_content(b"PK\x03\x04", "archive.zip")
        assert ok is False

    # Dangerous magic bytes

    def test_windows_exe_disguised_as_pdf_rejected(self):
        """Windows PE executable renamed to .pdf should be blocked"""
        content = b"MZ\x90\x00" + b"\x00" * 100
        ok, msg = validate_file_content(content, "resume.pdf")
        assert ok is False
        assert (
            "security" in msg.lower()
            or "malicious" in msg.lower()
            or "restricted" in msg.lower()
        )

    def test_linux_elf_disguised_as_pdf_rejected(self):
        """Linux ELF binary renamed to .pdf should be blocked"""
        content = b"\x7fELF" + b"\x00" * 100
        ok, msg = validate_file_content(content, "resume.pdf")
        assert ok is False

    def test_shell_script_disguised_as_txt_rejected(self):
        """Shell script renamed to .txt should be blocked"""
        content = b"#!/bin/bash\nrm -rf /"
        ok, msg = validate_file_content(content, "resume.txt")
        assert ok is False

    def test_php_script_disguised_as_pdf_rejected(self):
        """PHP script renamed to .pdf should be blocked"""
        content = b"<?php system('rm -rf /'); ?>"
        ok, msg = validate_file_content(content, "resume.pdf")
        assert ok is False

    # PDF specific

    def test_pdf_without_pdf_header_rejected(self):
        """PDF file without %PDF- header should be rejected"""
        content = b"This is just plain text pretending to be a PDF"
        ok, msg = validate_file_content(content, "resume.pdf")
        assert ok is False
        assert "PDF" in msg or "header" in msg.lower()

    # DOCX specific

    def test_docx_without_zip_signature_rejected(self):
        """DOCX without PK magic bytes should be rejected"""
        content = b"This is not a real docx file content"
        ok, msg = validate_file_content(content, "resume.docx")
        assert ok is False
        assert "DOCX" in msg or "ZIP" in msg

    # TXT specific

    def test_txt_with_null_bytes_rejected(self):
        """TXT file containing null bytes should be rejected"""
        content = b"Hello\x00World"
        ok, msg = validate_file_content(content, "resume.txt")
        assert ok is False
        assert "null" in msg.lower()

    def test_txt_with_unicode_content_accepted(self):
        """TXT file with valid unicode content should be accepted"""
        content = "My name is Kirti. I am a Python developer.".encode("utf-8")
        ok, msg = validate_file_content(content, "resume.txt")
        assert ok is True


# validate_upload_stream() tests


class TestValidateUploadStream:

    def _make_mock_file(self, content: bytes, chunk_size: int = 64 * 1024):
        """Helper — creates a mock UploadFile that streams content in chunks"""
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]
        chunks.append(b"")  # sentinel — signals end of stream

        mock_file = MagicMock()
        mock_file.read = AsyncMock(side_effect=chunks)
        return mock_file

    @pytest.mark.asyncio
    async def test_small_file_read_successfully(self):
        """File well under limit should be read completely"""
        content = b"%PDF-1.4 " + b"A" * 1000
        mock_file = self._make_mock_file(content)
        result = await validate_upload_stream(
            mock_file, max_bytes=MAX_RESUME_SIZE_BYTES
        )
        assert result == content

    @pytest.mark.asyncio
    async def test_file_exactly_at_limit_accepted(self):
        """File exactly at 5MB limit should be accepted"""
        content = b"A" * MAX_RESUME_SIZE_BYTES
        mock_file = self._make_mock_file(content)
        result = await validate_upload_stream(
            mock_file, max_bytes=MAX_RESUME_SIZE_BYTES
        )
        assert len(result) == MAX_RESUME_SIZE_BYTES

    @pytest.mark.asyncio
    async def test_file_exceeding_limit_raises_413(self):
        """File exceeding 5MB should raise HTTP 413"""
        content = b"A" * (MAX_RESUME_SIZE_BYTES + 1)
        mock_file = self._make_mock_file(content)
        with pytest.raises(HTTPException) as exc_info:
            await validate_upload_stream(mock_file, max_bytes=MAX_RESUME_SIZE_BYTES)
        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_empty_file_returns_empty_bytes(self):
        """Empty upload stream should return empty bytes"""
        mock_file = self._make_mock_file(b"")
        result = await validate_upload_stream(
            mock_file, max_bytes=MAX_RESUME_SIZE_BYTES
        )
        assert result == b""

    @pytest.mark.asyncio
    async def test_custom_size_limit_enforced(self):
        """Custom max_bytes limit should be respected"""
        content = b"A" * 200
        mock_file = self._make_mock_file(content)
        with pytest.raises(HTTPException) as exc_info:
            await validate_upload_stream(mock_file, max_bytes=100)
        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_413_error_message_contains_size_info(self):
        """413 error should mention the size limit in MB"""
        content = b"A" * (MAX_RESUME_SIZE_BYTES + 1)
        mock_file = self._make_mock_file(content)
        with pytest.raises(HTTPException) as exc_info:
            await validate_upload_stream(mock_file, max_bytes=MAX_RESUME_SIZE_BYTES)
        assert "5" in exc_info.value.detail  # 5 MB mentioned
