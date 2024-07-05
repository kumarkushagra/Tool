# Provide Batch_Dir_path, anonymize_flag 
# generate a new_CSV (Master.csv) in Data dir, append new uploads from it
# Upload all Studies 
# Anonymize
# Delete orignal Study only
# Update User_CSV


import requests
import pandas as pd
from .UP_list_UHIDs import list_subdirectories
from .UP_generate_series_path import generate_all_series_path
from .UP_update_master_csv import update_csv
from .UP_upload_each_series import upload_dicom_files
from .UP_anonymize_given_study import anonymize_study
from .UP_append_to_mapping_csv import append_to_csv
from .UP_delete_study import delete_studies
from .UP_rename_studyID import rename_patient
from .UP_new_study_from_array import find_new_element

def log_message(log_file_path,message):
    with open(log_file_path, 'a') as file:
        file.write(message + '\n')

def Upload_Batch(log_filepath, batch_dir_path, anonymize_flag, User_CSV_path, batch_no, last_number):
    
    # Read the user CSV file
    df = pd.read_csv(User_CSV_path)
    
    # By default
    ORTHANC_URL = "http://localhost:8042"

    # generate list containing all the UHIDs  
    uhid_array=list_subdirectories(batch_dir_path)

    print(uhid_array)
    # Reocrd in log File
    msg = f"list containing all sub-directories inside the batch provided for upload: {uhid_array}"
    log_message(log_filepath,msg)

    
    # Iterate over each UHID
    for uhid in uhid_array:
        # Record all studies present before uploading
        old_studies = requests.get(f"{ORTHANC_URL}/studies").json()
        # print(old_studies)

        # Store full path of all DCM instances in an array
        series_array = generate_all_series_path(batch_dir_path, uhid)
        # Reocrd in log File
        msg = f"Series in UHID: >--{uhid}--< is {series_array}"
        log_message(log_filepath,msg)

        # iterate over each series
        for series in series_array:
            # will upload each series for a given UHID
            upload_success=upload_dicom_files(log_filepath,ORTHANC_URL,series)
            if not upload_success:
                print(f"Failed to upload series for UHID: {uhid}. Skipping to next UHID.")
                # Reocrd in log File
                msg = f"Failed to upload series for UHID: {uhid}. Skipping to next UHID."
                log_message(log_filepath,msg)
                continue
        

        # Record all Studies after uploading
        new_studies = requests.get(f"{ORTHANC_URL}/studies").json()
        # Reocrd in log File
        msg = f"New studies: {new_studies}"
        log_message(log_filepath,msg)

        # Find the study_ID of new UHID i.e. just uploaded
        uploaded_studyID = find_new_element(old_studies,new_studies)
        # Reocrd in log File
        msg = f"Uploaded study ID: {uploaded_studyID}"
        log_message(log_filepath,msg)
        
        old_studies = requests.get(f"{ORTHANC_URL}/studies").json()
        # Reocrd in log File
        msg = f"old study IDs: {old_studies}"
        log_message(log_filepath,msg)

        if anonymize_flag==True:
        
            anonymize_result = anonymize_study(log_filepath,ORTHANC_URL, str(uploaded_studyID[0]))
            
            anonymized_studies = requests.get(f"{ORTHANC_URL}/studies").json()
            # Delete Orignal_study
            delete_studies(uploaded_studyID)
            # Reocrd in log File
            msg = f"Deleting studyID: {uploaded_studyID}"
            log_message(log_filepath,msg)
        
            # find studyID of the anonymized function
        
            uploaded_studyID = find_new_element(old_studies,anonymized_studies)
            # Reocrd in log File
            msg =f"Anonymized studyID: {uploaded_studyID}"
            log_message(log_filepath,msg)

            #######################################################            
            """ 

            for a given UHID (in this loop), check the type of defect
            Verify this from an if-elif loop 
            construct new name on that basis

            """
            print("*********************************************")
            print(str(uhid),type(uhid))
            print(f"CSV FILE PATH: {User_CSV_path}")
            print(len(df))
            
            print(df['Patient ID (UHID)'].dtype)
            # print(df[df['Patient ID (UHID)'].str.equals(str(uhid))])
            print(df[df['Patient ID (UHID)'] == int(uhid)]['Bleed Sub-Category'])
            print(df[df['Patient ID (UHID)'] == int(uhid)]['Bleed Sub-Category'].values)
            # Fetch the Abnormality 
            major_abnormality = df[df['Patient ID (UHID)'] == int(uhid)]['Bleed Sub-Category'].values
            
            print("*********************************************")
 	    
            if major_abnormality == "Normal":
                last_number[1] += 1
                new_name = "Normal_" + str(last_number[1])
            elif major_abnormality == "Bleed-Epidural":
                last_number[2] += 1
                new_name = "Bleed_Epidural_" + str(last_number[2])
            elif major_abnormality == "Bleed-Subdural":
                last_number[3] += 1
                new_name = "Bleed_Subdural_" + str(last_number[3])
            elif major_abnormality == "Bleed-Subarachnoid":
                last_number[4] += 1
                new_name = "Bleed_Subarachnoid_" + str(last_number[4])
            elif major_abnormality == "Bleed-Contusion":
                last_number[5] += 1
                new_name = "Bleed_Contusion_" + str(last_number[5])
            elif major_abnormality == "Bleed-Intraventricular":
                last_number[6] += 1
                new_name = "Bleed_Intraventricular_" + str(last_number[6])
            elif major_abnormality == "Bleed-Others":
                last_number[7] += 1
                new_name = "Bleed_Others_" + str(last_number[7])
            elif major_abnormality == "Midline Shift":
                last_number[8] += 1
                new_name = "Midline_Shift_" + str(last_number[8])
            elif major_abnormality == "Cervical Spine":
                last_number[9] += 1
                new_name = "Cervical_Spine_" + str(last_number[9])
            elif major_abnormality == "Fracture":
                last_number[10] += 1
                new_name = "Fracture_" + str(last_number[10])
            else:
                new_name = f"NEW NAME CANT BE FOUND FOR UHID: {uhid}"
                print(new_name)
                continue

            # Renaming DONE HERE DELETE is also handeled by this function        
            final_study_id = rename_patient(log_filepath, uploaded_studyID[0], new_name)
        else:
            final_study_id =uploaded_studyID

        print(final_study_id)

        new_name =(requests.get(f'http://localhost:8042/studies/{final_study_id[0]}').json()['PatientMainDicomTags']['PatientName'])
            #########################################################
        append_to_csv(uhid, str(final_study_id),batch_no,new_name)
        # Reocrd in log File
        msg = f"appended to mapping.csv"
        log_message(log_filepath,msg)

        # Update the Master CSV
        # change value to "uploaded" == 1 
        ################### FOR TESTING, i have set upload == 0, before deployment, change it to i########
        update_csv(User_CSV_path,  uhid, 1)
        # Reocrd in log File
        msg =f"Updated Final.csv"
        log_message(log_filepath,msg)

if __name__=="__main__":
    batch_Dir_path="C:/Users/EIOT/Desktop/Unziped_dir"
    anon_flag=True
    User_CSV_path="D:/Final_Bleed.csv"
    batch_name="Batch1"
    log_filepath= "Logs/UHID error/sample.txt"
    last_number = [0,0,0,0,0,0,0,0,0,0,0]
    Upload_Batch(log_filepath, batch_Dir_path, anon_flag, User_CSV_path, batch_name, last_number)
