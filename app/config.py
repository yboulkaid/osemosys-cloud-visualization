import random
import wget
import os
from zipfile import ZipFile


class Config:
    def __init__(self, input_string):
        self.input_string = input_string

    def csv_folder_path(self):
        return os.path.join(self.__base_folder_path(), 'csv')

    def data_file_path(self):
        return os.path.join(self.__base_folder_path(), 'data.txt')

    def __base_folder_path(self):
        if self.input_string in ['bolivia', 'ethiopia', 'vietnam', 'indonesia']:
            return os.path.join(os.getcwd(), 'data', self.input_string)
        else:
            raise NameError('NoFolderFound')
            # return __download_files(self.input_string)

    def __download_files(self, input_string):
        random_number = random.randint(1, 99999)
        zip_file_name = f'csv_{random_number}.zip'
        folder_name = f'csv_{random_number}'

        zip_path = os.path.join(os.getcwd(), 'tmp', zip_file_name)
        wget.download(input_string, zip_path)
        folder_path = os.path.join(os.getcwd(), 'tmp', folder_name)

        with ZipFile(zip_path, 'r') as zipObj:
            zipObj.extractall(folder_path)

        return os.path.join(os.getcwd(), 'tmp', folder_name, 'csv')
