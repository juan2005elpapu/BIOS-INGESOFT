import logging
from io import BytesIO
from typing import Optional

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseStorage(Storage):
    def __init__(self):
        self.client: Optional[Client] = None
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

    def _save(self, name: str, content: File) -> str:
        if not self.client:
            logger.warning("Supabase client not available, falling back to local storage")
            from django.core.files.storage import default_storage
            return default_storage.save(name, content)

        try:
            content.seek(0)
            file_bytes = content.read()
            
            self.client.storage.from_(self.bucket_name).upload(
                path=name,
                file=file_bytes,
                file_options={"content-type": content.content_type or "application/octet-stream"}
            )
            
            logger.info(f"File {name} uploaded to Supabase successfully")
            return name
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}. Falling back to local storage")
            from django.core.files.storage import default_storage
            return default_storage.save(name, content)

    def url(self, name: str) -> str:
        if not self.client or not name:
            from django.core.files.storage import default_storage
            return default_storage.url(name)

        try:
            response = self.client.storage.from_(self.bucket_name).get_public_url(name)
            return response
        except Exception as e:
            logger.error(f"Error getting public URL from Supabase: {e}")
            from django.core.files.storage import default_storage
            return default_storage.url(name)

    def exists(self, name: str) -> bool:
        if not self.client:
            from django.core.files.storage import default_storage
            return default_storage.exists(name)

        try:
            self.client.storage.from_(self.bucket_name).download(name)
            return True
        except:
            return False

    def delete(self, name: str):
        if not self.client:
            from django.core.files.storage import default_storage
            return default_storage.delete(name)

        try:
            self.client.storage.from_(self.bucket_name).remove([name])
            logger.info(f"File {name} deleted from Supabase")
        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")