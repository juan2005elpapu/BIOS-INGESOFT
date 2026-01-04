import io
import logging
import os
import uuid

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from PIL import Image
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseStorage(Storage):
    FOLDER = "lotes"

    def __init__(self):
        self.client: Client | None = None
        self.bucket_name = getattr(settings, 'SUPABASE_BUCKET', 'batches')
        self._initialize_client()

    def _initialize_client(self):
        if not getattr(settings, 'USE_SUPABASE_STORAGE', False):
            return

        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            # Solo log en el proceso del reloader (evita duplicado)
            if os.environ.get('RUN_MAIN') == 'true':
                logger.info("Supabase storage client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def _compress_to_webp(
        self, content: File, max_size: int = 1200, quality: int = 80
    ) -> tuple[bytes, str]:
        """Comprime la imagen a formato WebP."""
        try:
            content.seek(0)
            image = Image.open(content)

            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            image.save(buffer, format="WEBP", quality=quality, optimize=True)
            buffer.seek(0)

            return buffer.getvalue(), "image/webp"
        except Exception as e:
            logger.warning(f"Could not compress image: {e}, using original")
            content.seek(0)
            return content.read(), getattr(
                content, 'content_type', 'application/octet-stream'
            )

    def _generate_name(self) -> str:
        return f"{uuid.uuid4().hex}.webp"

    def _save(self, name: str, content: File) -> str:
        if not self.client:
            raise ValueError("Supabase client not initialized")

        try:
            file_name = self._generate_name()
            file_path = f"{self.FOLDER}/{file_name}"
            file_bytes, content_type = self._compress_to_webp(content)

            self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )

            logger.info(f"File {file_path} uploaded to Supabase successfully")
            return file_path
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}")
            raise

    def url(self, name: str) -> str:
        if not name:
            return ""

        clean_name = name.lstrip("/")
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{clean_name}"

    def exists(self, name: str) -> bool:
        if not self.client or not name:
            return False

        try:
            clean_name = name.lstrip("/")
            parts = clean_name.rsplit("/", 1)
            folder = parts[0] if len(parts) > 1 else ""
            file_name = parts[-1]

            response = self.client.storage.from_(self.bucket_name).list(path=folder)
            return any(f.get("name") == file_name for f in response)
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False

    def delete(self, name: str):
        if not name or not self.client:
            return

        try:
            self.client.storage.from_(self.bucket_name).remove([name])
            logger.info(f"File {name} deleted from Supabase")
        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")

    def listdir(self, path: str):
        return [], []

    def size(self, name: str) -> int:
        return 0
