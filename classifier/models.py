from django.db import models
import pathlib, uuid

# Create your models here.

def submission_handler(instance, filename):
    fpath = pathlib.Path(filename)
    type = fpath.suffix
    allowed_types = ['.fasta', '.zip']

    if(type not in allowed_types):
        raise Exception(f"Invalid file type. Allowed file types: {allowed_types}")
    
    new_fname = str(uuid.uuid1())
    return f"fastas/{new_fname}{fpath.suffix}" #allows for privacy of filename

class Submission(models.Model):
    file = models.FileField(upload_to=submission_handler) #uploads to classifier/uploads/fastas

    def getFile(self):
        return self.file
