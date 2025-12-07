"""
Módulo de gestión de Google Drive
"""
import io
import logging
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError

from config import (
    FOLDER_ENTRADA_NAME,
    FOLDER_PROCESADAS_NAME,
    FOLDER_ERRORES_NAME,
    FOLDER_REVISION_NAME
)

logger = logging.getLogger(__name__)


class DriveManager:
    """Gestor de operaciones con Google Drive"""
    
    def __init__(self, service):
        """
        Inicializa el gestor de Drive.
        
        Args:
            service: Servicio de Google Drive API
        """
        self.service = service
        self.folder_ids = {}
        
    def find_folder_by_name(self, folder_name, parent_id=None):
        """
        Busca una carpeta por nombre.
        
        Args:
            folder_name (str): Nombre de la carpeta
            parent_id (str, optional): ID de la carpeta padre
        
        Returns:
            str: ID de la carpeta encontrada, None si no existe
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            items = results.get('files', [])
            
            if items:
                folder_id = items[0]['id']
                logger.debug(f"Carpeta '{folder_name}' encontrada: {folder_id}")
                return folder_id
            else:
                logger.warning(f"Carpeta '{folder_name}' no encontrada")
                return None
                
        except HttpError as e:
            logger.error(f"❌ Error al buscar carpeta '{folder_name}': {e}")
            return None
    
    def initialize_folders(self, root_folder_name="MACROCENTRO"):
        """
        Inicializa y cachea los IDs de las carpetas necesarias.
        
        Args:
            root_folder_name (str): Nombre de la carpeta raíz
        
        Returns:
            bool: True si todas las carpetas fueron encontradas
        """
        logger.info(f"Buscando carpetas en Drive...")
        
        # Buscar carpeta raíz
        root_id = self.find_folder_by_name(root_folder_name)
        if not root_id:
            logger.error(f"❌ Carpeta raíz '{root_folder_name}' no encontrada")
            return False
        
        self.folder_ids['root'] = root_id
        logger.info(f"✅ Carpeta raíz encontrada: {root_id}")
        
        # Buscar subcarpetas
        required_folders = [
            FOLDER_ENTRADA_NAME,
            FOLDER_PROCESADAS_NAME,
            FOLDER_ERRORES_NAME,
            FOLDER_REVISION_NAME
        ]
        
        for folder_name in required_folders:
            folder_id = self.find_folder_by_name(folder_name, root_id)
            if not folder_id:
                logger.error(f"❌ Carpeta '{folder_name}' no encontrada")
                return False
            
            self.folder_ids[folder_name.lower()] = folder_id
            logger.info(f"✅ Carpeta '{folder_name}' encontrada: {folder_id}")
        
        return True
    
    def list_files_in_folder(self, folder_name, max_files=50):
        """
        Lista archivos en una carpeta.
        
        Args:
            folder_name (str): Nombre de la carpeta (entrada, procesadas, etc.)
            max_files (int): Máximo número de archivos a retornar
        
        Returns:
            list: Lista de diccionarios con info de archivos
        """
        folder_key = folder_name.lower()
        folder_id = self.folder_ids.get(folder_key)
        
        if not folder_id:
            logger.error(f"❌ Carpeta '{folder_name}' no inicializada")
            return []
        
        try:
            query = f"'{folder_id}' in parents and trashed=false and mimeType contains 'image/'"
            
            results = self.service.files().list(
                q=query,
                pageSize=max_files,
                fields='files(id, name, mimeType, createdTime, size)',
                orderBy='createdTime'
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"📁 {len(files)} archivos encontrados en '{folder_name}'")
            
            return files
            
        except HttpError as e:
            logger.error(f"❌ Error al listar archivos en '{folder_name}': {e}")
            return []
    
    def find_file_by_name(self, filename, folder_name):
        """
        Busca un archivo específico por nombre en una carpeta.
        
        Args:
            filename (str): Nombre exacto del archivo a buscar
            folder_name (str): Nombre de la carpeta donde buscar
        
        Returns:
            dict: Info del archivo si se encuentra, None si no
        """
        folder_key = folder_name.lower()
        folder_id = self.folder_ids.get(folder_key)
        
        if not folder_id:
            logger.error(f"❌ Carpeta '{folder_name}' no inicializada")
            return None
        
        try:
            # Escapar comillas simples en el nombre del archivo
            escaped_filename = filename.replace("'", "\\'")
            query = f"name='{escaped_filename}' and '{folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=1,
                fields='files(id, name, mimeType, createdTime, size)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]
            
            return None
            
        except HttpError as e:
            logger.error(f"❌ Error al buscar archivo '{filename}' en '{folder_name}': {e}")
            return None
    
    def download_file(self, file_id, destination_path):
        """
        Descarga un archivo de Drive.
        
        Args:
            file_id (str): ID del archivo en Drive
            destination_path (str): Ruta local donde guardar el archivo
        
        Returns:
            bool: True si la descarga fue exitosa
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
            
            logger.debug(f"✅ Archivo descargado: {destination_path}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error al descargar archivo {file_id}: {e}")
            return False
    
    def move_file(self, file_id, destination_folder_name):
        """
        Mueve un archivo a otra carpeta.
        
        Args:
            file_id (str): ID del archivo
            destination_folder_name (str): Nombre de la carpeta destino
        
        Returns:
            bool: True si el movimiento fue exitoso
        """
        folder_key = destination_folder_name.lower()
        destination_folder_id = self.folder_ids.get(folder_key)
        
        if not destination_folder_id:
            logger.error(f"❌ Carpeta destino '{destination_folder_name}' no inicializada")
            return False
        
        try:
            # Obtener padres actuales
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Mover archivo
            self.service.files().update(
                fileId=file_id,
                addParents=destination_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            logger.debug(f"✅ Archivo {file_id} movido a '{destination_folder_name}'")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error al mover archivo {file_id}: {e}")
            return False
    
    def get_file_link(self, file_id):
        """
        Obtiene el link de visualización de un archivo.
        
        Args:
            file_id (str): ID del archivo
        
        Returns:
            str: URL del archivo
        """
        return f"https://drive.google.com/file/d/{file_id}/view"
