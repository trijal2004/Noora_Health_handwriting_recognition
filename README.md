
## Noora_Health_handwriting_recognition
![Logo](https://i.postimg.cc/VNLcvBfn/iitkconsult-cover-1.jpg)

 
## Project Overview:

This repository is for Handwriting recognition of what nurses enter and pulling the text out digitally.

We experimented using various **processors** available in Document AI on google cloud platform. 

- Results obtained from CustomeExtractor are present in ```CustomeExtractor.ipynb```  
- Results obtained using FormParser are present in ```FormParser.ipynb```

To train CustomExtracter several images were used for both training and testing and these images have been seprately stored in their respective folders(```Test_Attendance_Sheets``` AND ```Train_Attendance_Sheets```).  Labels for all the images could be found on Google Cloud platform. 

The ```Unused_images``` are stored seprately for future use. 

## Installation

All the ipynb notebooks could be run using **google colab**.  

For running the files locally:  
* Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk/?hl=en_US&_ga=2.96937945.-752482749.1702469365&_gac=1.3460740.1703278465.EAIaIQobChMIl7mj0_ajgwMVZI9LBR2ypQLIEAAYASAAEgLuc_D_BwE) installed.  
* Follow the setup instructions in the [Process documents by using client libraries](https://cloud.google.com/document-ai/docs/process-documents-client-libraries?_ga=2.96937945.-752482749.1702469365&_gac=1.3460740.1703278465.EAIaIQobChMIl7mj0_ajgwMVZI9LBR2ypQLIEAAYASAAEgLuc_D_BwE) 

 

If running for some other project you'll need to change these parameters written on the top of both notebooks.   
The path of image for which we need the output need to be passed in ```file_path```.

```python
project_id = "attendanceextractor"
location = "us"
processor_id = "12bf41b9e4b98255"
processor_version = "rc"
file_path = "/content/MAHENDRAGARH_NEO_121023_4.jpeg"
mime_type = "image/jpeg"
```

## Usage 
Using **FormParser**

![image sample](https://i.postimg.cc/T3G4RVfx/sample.jpg)

Using **CustomeExtractor**

![image](https://i.postimg.cc/pXvZ8P7Y/Screenshot-from-2023-12-29-14-43-32.png)


## Project Status

Currently we have written the code for a single images to show the results and confirm if they are of any use or not.  
In future if we continue with these processors only we will automate the complete process and will generate end outcomes all stored in one ```JSON``` file.
