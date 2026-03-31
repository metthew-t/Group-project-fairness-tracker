import os
import zipfile
from io import BytesIO
from django.core.files.base import ContentFile
from contributions.models import Contribution

def merge_project_files(project):
    """
    Collects all files from all approved contributions in a project
    and zips them together.
    """
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        contributions = Contribution.objects.filter(
            task__project=project,
            status='approved'
        ).exclude(file_upload='')

        for contrib in contributions:
            if contrib.file_upload:
                file_path = contrib.file_upload.path
                file_name = os.path.basename(file_path)
                # Group by user/task for better organization
                folder_name = f"{contrib.user.username}/{contrib.task.title[:20]}"
                zip_file.write(file_path, arcname=f"{folder_name}/{file_name}")

    buffer.seek(0)
    return buffer
