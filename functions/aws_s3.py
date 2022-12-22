import boto3, os, glob
from botocore.exceptions import NoCredentialsError
from django.conf import settings

class AWSS3:
    "define methods to interact with the AWS S3 service"
    def __init__(self):
        "initialize the class with the required config"
        self.ACCESS_KEY = settings.AWSS3_ACCESS_KEY
        self.SECRET_KEY = settings.AWSS3_SECRET_KEY
        self.BUCKET_NAME = settings.AWSS3_BUCKET

    def uploadFileToS3(self, localFilePath, subDirectoryInBucket, fileNameInS3):
        "upload a file to the AWS S3 bucket"
        s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY, aws_secret_access_key=self.SECRET_KEY)
        try:
            s3.upload_file(localFilePath, self.BUCKET_NAME, subDirectoryInBucket, fileNameInS3)
            print("Upload to S3 Successful")
            return True
        except FileNotFoundError:
            print("The file was not found - AWS S3")
            return False
        except NoCredentialsError:
            print("Credentials not available - AWS S3")
            return False

    def WiteStringToS3(self, sContent, subDirectoryInBucket, fileName):
        "upload string to the AWS S3 bucket by defining the string as file object"
        fileList = glob.glob('*.json', recursive=False)
        for f in fileList:
            os.remove(f)
        s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY, aws_secret_access_key=self.SECRET_KEY)
        f = open(fileName, "wb") #open/create an empty temporary file to write bytes on it
        f.write(bytes(sContent,'utf-8')) #write bytes to the empty file
        f.close()
        try:
            read_file = open(fileName, "rb") #opening file in read binary mode
            s3.upload_fileobj(read_file, self.BUCKET_NAME, subDirectoryInBucket+'/'+fileName)
            read_file.close()
            print("Upload to S3 Successful")
            return True
        except FileNotFoundError:
            print("The file was not found - AWS S3")
            return False
        except NoCredentialsError:
            print("Credentials not available - AWS S3")
            return False
        except Exception as e:
            print('the AWS S3 exception is ', e)
        finally:
            pass                      