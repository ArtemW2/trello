import io, logging, uuid, re, environ, os

from core.settings import BASE_DIR

env = environ.Env(
    DEBUG = (bool, False)
)

env.read_env(os.path.join(BASE_DIR, '.env'))

from task.models import File

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from task.services.redis_service import RedisService

logger = logging.getLogger(__name__)

class UploadFileService:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = env("SERVICE_ACCOUNT_FILE")

    @staticmethod
    def get_drive_service():
        credentials = service_account.Credentials.from_service_account_file(
            UploadFileService.SERVICE_ACCOUNT_FILE, scopes = UploadFileService.SCOPES
        )
        return build("drive", "v3", credentials=credentials, cache_discovery=False)

    @staticmethod
    def upload_files_to_google_drive(file, filename, mimetype="application/octet-stream", folder_id=env("folder_id")):
        drive_service = UploadFileService.get_drive_service()
        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        media = MediaIoBaseUpload(
            file, mimetype=mimetype, resumable=True
        )
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id, webContentLink").execute()
        return file.get('webContentLink')


    @staticmethod
    def upload_files_to_task(task, files):
        file_instances = []
        redis_client = RedisService()
        for file in files:
            redis_key = file["key"]
            filename = file["filename"]
            mime_type = file["content_type"]
            file_content = redis_client.get(redis_key)

            if not file_content:
                logger.error(f"Файл с ключом {redis_key} не найден в Redis")
                continue

            file_obj = io.BytesIO(file_content)

            logger.info(f"Загрузка файла {filename} с типом {mime_type} для задачи {task.id}")
            try:
                google_drive_url = UploadFileService.upload_files_to_google_drive(
                    file_obj, filename, mime_type
                )
                file_instance = File(task=task, url=google_drive_url)
                file_instance.save()
                file_instances.append(file_instance)
            except Exception as e:
                logger.error(f"Ошибка при загрузке файла {filename}: {e}")
                raise e
            finally:
                redis_client.connection.delete(redis_key)
        return file_instances
    
    @staticmethod
    def upload_files_to_redis(files):
        redis_keys = []
        redis_client = RedisService()
        for file in files:
            file_content = file.read()
            key = f"Upload_File: {uuid.uuid4()}"
            redis_client.set(key, file_content)
            redis_keys.append({
                "key": key,
                "filename": file.name,
                "content_type": file.content_type
            })

        return redis_keys

    @staticmethod
    def delete_file_from_google_drive(file_id):
        service = UploadFileService.get_drive_service()
        service.files().delete(fileId = file_id).execute()
            

    @staticmethod
    def get_file_id_from_url(url):
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        return None
    