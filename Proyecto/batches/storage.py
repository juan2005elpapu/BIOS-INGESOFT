import io
import logging
import uuid

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from PIL import Image
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseStorage(Storage):
    def __init__(self):
        self.client: Client | None = None
        self.bucket_name = settings.SUPABASE_BUCKET
        self._initialize_client()

    def _initialize_client(self):
        if not settings.USE_SUPABASE_STORAGE:
            return

        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Supabase storage client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def _compress_to_webp(self, content: File, max_size: int = 1200, quality: int = 80) -> tuple[bytes, str]:
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
            return content.read(), content.content_type or "application/octet-stream"

    def _generate_name(self) -> str:
        """Genera un nombre único para el archivo."""
        return f"{uuid.uuid4().hex}.webp"

    def _save(self, name: str, content: File) -> str:
        if not self.client:
            logger.warning("Supabase client not available, falling back to local storage")
            from django.core.files.storage import default_storage
            return default_storage.save(name, content)

        try:
            file_name = self._generate_name()
            file_bytes, content_type = self._compress_to_webp(content)

            self.client.storage.from_(self.bucket_name).upload(
                path=file_name,
                file=file_bytes,
                file_options={"content-type": content_type}
            )

            logger.info(f"File {file_name} uploaded to Supabase successfully")
            return file_name
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}. Falling back to local storage")
            content.seek(0)
            from django.core.files.storage import default_storage
            return default_storage.save(name, content)

    def url(self, name: str) -> str:
        if not name:
            return ""
            
        if not self.client:
            from django.core.files.storage import default_storage
            return default_storage.url(name)

        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{name}"

    def exists(self, name: str) -> bool:
        """Siempre retorna False para evitar llamadas innecesarias a la API."""
        return False

    def delete(self, name: str):
        if not name:
            return
            
        if not self.client:
            from django.core.files.storage import default_storage
            return default_storage.delete(name)

        try:
            self.client.storage.from_(self.bucket_name).remove([name])
            logger.info(f"File {name} deleted from Supabase")
        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")

    def listdir(self, path: str):
        return [], []

    def size(self, name: str) -> int:
        return 0
