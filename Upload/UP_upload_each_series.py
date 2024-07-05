import os 
import requests
def log_message(log_file_path,message):
    with open(log_file_path, 'a') as file:
        file.write(message + '\n')

def upload_dicom_files(log_filepath, orthanc_url, dir_path: str):
    """
    Uploads DICOM files to Orthanc.
    
    Parameters:
    orthanc_url (str): The URL of the Orthanc server.
    dir_path (str): The path to the DICOM series directory.
    
    Returns:
    dict: A dictionary with a status message.
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        # Reocrd in log File
        msg = f"Directory does not exist"
        log_message(log_filepath,msg)
        raise Exception("Directory does not exist")

    # Iterate over all files in the specified directory
    for file_name in os.listdir(dir_path):
        # Check if the file has a .dcm extension
        if file_name.lower().endswith('.dcm'):
            # Path to the DICOM file
            dicom_file_path = os.path.join(dir_path, file_name)
            dicom_file_path = dicom_file_path.replace("\\", "/")



            # UPLOADING BEGINS

            # Read the DICOM file in binary mode
            with open(dicom_file_path, 'rb') as f:
                dicom_data = f.read()

            # Upload the DICOM file
            orthanc_url_with_instances = orthanc_url.rstrip('/') + '/instances'
            response = requests.post(orthanc_url_with_instances, data=dicom_data, headers={'Content-Type': 'application/dicom'})



            # Check for Exceptions
            if response.status_code == 200:
                print(f'DICOM file {file_name} uploaded successfully')
                # Reocrd in log File
                msg =f'DICOM file {file_name} uploaded successfully'
                log_message(log_filepath,msg)
            else:
                print(f'Failed to upload DICOM file {file_name}. Status code: {response.status_code}')
                # Reocrd in log File
                msg = f'Failed to upload DICOM file {file_name}. Status code: {response.status_code}'
                log_message(log_filepath,msg)
                
                print('Response content:', response.content.decode('utf-8'))
                # Reocrd in log File
                msg = 'Response content:', response.content.decode('utf-8')
                log_message(log_filepath,msg)

    return {"detail": "DICOM files upload process completed"}




if __name__=="__main__":
    dir_path="C:/Users/EIOT/Desktop/Unziped_dir/105325641/2024/series1"
    orthanc_url = "http://localhost:8042"
    upload_dicom_files(orthanc_url,dir_path)
    