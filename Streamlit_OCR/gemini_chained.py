
#import formparser_json_output_script as fp
from pathlib import Path
import google.generativeai as genai
import os
#import necessary files
from typing import Optional, Sequence
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import streamlit as st
import sys




#this info will be extracted from google cloud
project_id = "YOUR_PROJECT_ID"                               # Format is "your-gcp-project-id"
location = "LOCATION"                                             # Format is "us" or "eu"
processor_id = "PROCESSOR_ID"                           # Create processor before running sample
processor_version = "PROCESSOR_VERSION"                                    # Refer to https://cloud.google.com/document-ai/docs/manage-processor-versions for more information
                                  # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types

#------------------------------------------------------------------------FUNCTION1----------------------------------------------------------------------------
def process_document_form_sample(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    file_path: str,
    mime_type: str,
) -> dict:

    # Online processing request to Document AI
    document = process_document(
        project_id, location, processor_id, processor_version, file_path, mime_type
    )

    # Read the table and form fields output from the processor
    # The form processor also contains OCR data. For more information
    # on how to parse OCR data please see the OCR sample.

    text = document.text

    for page in document.pages:


      
      for table in page.tables:
        num_columns = len(table.header_rows[0].cells)
        num_rows = len(table.body_rows)

        if table == page.tables[0]:

            header_row_text = ""
            for cell in table.header_rows[0].cells:
                cell_text = layout_to_text(cell.layout, text)
                header_row_text += f"{repr(cell_text.strip())} | " if cell_text.strip() else "'' | "

        for table_row in table.body_rows:
            row_text = ""
            for cell in table_row.cells:
                cell_text = layout_to_text(cell.layout, text)
                row_text += f"{repr(cell_text.strip())} | "

            formatted_output = {
                header_cell.strip(): row_cell.strip()
                for header_cell, row_cell in zip(header_row_text.split('|'), row_text.split('|'))
            }



        for field in page.form_fields:
            name = layout_to_text(field.field_name, text)
            value = layout_to_text(field.field_value, text)


        return document
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""## Functions for processing extracted text"""


def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    file_path: str,
    mime_type: str,
    process_options: Optional[documentai.ProcessOptions] = None,
) -> documentai.Document:
    # You must set the `api_endpoint` if you use a location other than "us".
    client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(
            api_endpoint=f"{location}-documentai.googleapis.com"
        )
    )

    # The full resource name of the processor version, e.g.:
    # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
    # You must create a processor before running this sample.
    name = client.processor_version_path(
        project_id, location, processor_id, processor_version
    )

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type),
        # Only supported for Document OCR processor
        process_options=process_options,
    )

    result = client.process_document(request=request)

    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    return result.document


def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document"s text. This function converts
    offsets to a string.
    """
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )



"""### Raw txt file"""


def convert_document_to_dictionary(document):

    converted_dict = {"pages": []}

    for page in document.pages:
        page_dict = {
            "page_number": page.page_number,
            "tables": [],
            "form_fields": [],
        }

        for table in page.tables:
            table_dict = {
                "columns": [layout_to_text(cell.layout, document.text).strip() for cell in table.header_rows[0].cells],
                "rows": [
                    [layout_to_text(cell.layout, document.text).strip() for cell in row.cells]
                    for row in table.body_rows
                ],
            }
            page_dict["tables"].append(table_dict)

        for field in page.form_fields:
            name = layout_to_text(field.field_name, document.text).strip()
            value = layout_to_text(field.field_value, document.text).strip()
            page_dict["form_fields"].append({name: value})

        converted_dict["pages"].append(page_dict)

    return converted_dict





def json_structure(dictionary):
    structured_output = {"pages": []}

    for page in dictionary['pages']:
        current_page = {'page_number': page['page_number'], 'tables': []}

        for table_index, table in enumerate(page['tables']):
            if table_index == 0:
                current_page['tables'].append({'columns': table['columns'], 'rows': []})
            else:
                current_page['tables'][0]['rows'].append(table['columns'])

            for row in table['rows']:
                current_page['tables'][0]['rows'].append(row)

        current_page['form_fields'] = page['form_fields']
        structured_output['pages'].append(current_page)

    return structured_output


#restructuring structured_json to keep only required columns-----------------------------------------------------------------------------------------------------------------
def restructure_json(original_json):
    restructured_data = {'pages': []}

    for page in original_json['pages']:
        restructured_page = {'page_number': page['page_number'], 'tables': []}

        for table in page['tables']:
            restructured_table = {'columns': table['columns'][:3] + ['PeopleTrained'], 'rows': []}

            for row in table['rows']:
                session_date, session_location, conducted_by_name, *rest = row
                people_trained = next((value for value in rest if value), None)

                restructured_row = [session_date, session_location, conducted_by_name, people_trained]
                restructured_table['rows'].append(restructured_row)

            restructured_page['tables'].append(restructured_table)

        if page['form_fields']:  # Check if 'form_fields' list is not empty
            for form_field, value in page['form_fields'][0].items():
                restructured_page['form_fields'] = [{form_field: value}]

        restructured_data['pages'].append(restructured_page)

    return restructured_data



#function to use restructured_json to make dictionary of required structure-------------------------------------------------------------------------------------------------
def structured_dictionary(final_json):
    result = []

    for page in final_json['pages']:
        for table in page['tables']:
            for row in table['rows']:
                session_date, session_location, conducted_by_name, people_trained = row
                entry_dict = {
                    'SessionDate': session_date,
                    'SessionLocation': session_location,
                    'ConductedByName': conducted_by_name,
                    'PeopleTrained': people_trained
                }
                result.append(entry_dict)

    return result

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import json
#to save restructured_json in json format
def save_to_json(structured_data, filename='outputjson.json'):
    with open(filename, 'w') as json_file:
        json.dump(structured_data, json_file, indent=2)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def process_document_from_file(file_path: str) -> documentai.Document:
    """
    Process a document specified by the file path.

    Args:
        file_path (str): The path to the input document.

    Returns:
        documentai.Document: The processed document.
    """
    # Define your project, location, processor_id, processor_version, and mime_type here
    project_id = "YOUR_PROJECT_ID"
    location = "LOCATION"
    processor_id = "PROCESSOR_ID"
    processor_version = "PROCESSOR_VERSION"
    mime_type = "image/jpeg"

    # Process the document form sample
    document = process_document_form_sample(
        project_id, location, processor_id, processor_version, file_path, mime_type
    )

    return document
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Get the file path from the user
              ################################################################################################




API_KEY = 'YOUR_API_KEY'

genai.configure(api_key=API_KEY)

# Set up the model
generation_config = {
  "temperature": 0.4,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro-vision",
                              generation_config=generation_config,
                              safety_settings=safety_settings)



# Validate that an image is present



def passable():
  pass
  # form_parser_input = """

  # [
  #   {
  #     "SessionDate": "3/9/23",
  #     "SessionLocation": "PNC",
  #     "ConductedByName": "Noury",
  #     "PeopleTrained": "27"
  #   },
  #   {
  #     "SessionDate": "4/9/23",
  #     "SessionLocation": "ANC(OPP)",
  #     "ConductedByName": "Manisha N/a.",
  #     "PeopleTrained": "55"
  #   },
  #   {
  #     "SessionDate": "4/9/23",
  #     "SessionLocation": "W\nPNC Ward",
  #     "ConductedByName": "Gurpreet\nParangt",
  #     "PeopleTrained": "20"
  #   },
  #   {
  #     "SessionDate": "419",
  #     "SessionLocation": "ANC COP)",
  #     "ConductedByName": "NoManisha",
  #     "PeopleTrained": "90"
  #   },
  #   {
  #     "SessionDate": "4/9/23",
  #     "SessionLocation": "PNC Ward",
  #     "ConductedByName": "Parangut Kou",
  #     "PeopleTrained": "22"
  #   },
  #   {
  #     "SessionDate": "5/9/23",
  #     "SessionLocation": "ANC OPD(M)",
  #     "ConductedByName": "Pargryntton",
  #     "PeopleTrained": "\u2713"
  #   },
  #   {
  #     "SessionDate": "5/9/23",
  #     "SessionLocation": "PNC",
  #     "ConductedByName": "N/ Paramjeet",
  #     "PeopleTrained": "50"
  #   },
  #   {
  #     "SessionDate": "5/9/23",
  #     "SessionLocation": "AN",
  #     "ConductedByName": "/Fermjest",
  #     "PeopleTrained": "25"
  #   },
  #   {
  #     "SessionDate": "5/9/23",
  #     "SessionLocation": "ANC OPD",
  #     "ConductedByName": "Paramgnt",
  #     "PeopleTrained": "102"
  #   },
  #   {
  #     "SessionDate": "5/9/23 ANC",
  #     "SessionLocation": "\"No Geekay's",
  #     "ConductedByName": "",
  #     "PeopleTrained": "25"
  #   },
  #   {
  #     "SessionDate": "5/9/23 prod",
  #     "SessionLocation": "Geetanjal\nHop",
  #     "ConductedByName": "",
  #     "PeopleTrained": "22\nELL"
  #   },
  #   {
  #     "SessionDate": "6/9/23 A\u0143C Ward",
  #     "SessionLocation": "1.0.cuter\nPart",
  #     "ConductedByName": "",
  #     "PeopleTrained": "25"
  #   },
  #   {
  #     "SessionDate": "6/9/23 ANCwand",
  #     "SessionLocation": "N.O. Cutajal\nParanyat",
  #     "ConductedByName": "",
  #     "PeopleTrained": "25\n20"
  #   },
  #   {
  #     "SessionDate": "OPD 6/9/23 ANCOR",
  #     "SessionLocation": "N.O. \nCructural\nP",
  #     "ConductedByName": "",
  #     "PeopleTrained": "15"
  #   },
  #   {
  #     "SessionDate": "6/9/23 ANC OPD",
  #     "SessionLocation": "N.o. Pareight",
  #     "ConductedByName": "",
  #     "PeopleTrained": "20"
  #   },
  #   {
  #     "SessionDate": "6/9/23 PNC Ward",
  #     "SessionLocation": "No. Parent\n\u0441\u0447\u0438\u043d\u0438\u0458\u0430\u043b",
  #     "ConductedByName": "",
  #     "PeopleTrained": "22"
  #   },
  #   {
  #     "SessionDate": "7/9/23 PMIC word",
  #     "SessionLocation": "Alo Shivani\nAuto Vwashi",
  #     "ConductedByName": "",
  #     "PeopleTrained": "23"
  #   },
  #   {
  #     "SessionDate": "8/9/23 ANC (OP2)",
  #     "SessionLocation": "N/o Manaha",
  #     "ConductedByName": "L",
  #     "PeopleTrained": "100"
  #   },
  #   {
  #     "SessionDate": "8/9/23 ANC (ORD",
  #     "SessionLocation": ") n/loMani",
  #     "ConductedByName": "",
  #     "PeopleTrained": "120"
  #   },
  #   {
  #     "SessionDate": "8/9/23 PNC Word",
  #     "SessionLocation": "Paranjut\nN.O.",
  #     "ConductedByName": "",
  #     "PeopleTrained": "40"
  #   }
  # """

def create_chain(image_parts,model_object,initial_response=None, background=None, problem=None ,data_source_prompt=None, task=None):
  prompt_parts = []
  if image_parts is None:
    user_inputs = [initial_response, background, problem, task]
  else:
    user_inputs = [initial_response, background, problem, data_source_prompt, image_parts[0], task]
  for user_input in user_inputs:
    if user_input is not None:
      prompt_parts.append(user_input)

  response = model_object.generate_content(prompt_parts)

  return response.text



"""###CHAIN-1"""
def chained_prompts(form_parser_input,image_parts):
    with st.status("Creating Chains..."):
        st.write("Chain 1 in progress...")


        background = """
        Background: You are a skilled Data extractor and corrector
        """

        problem = """
        Problem: From the images, Extract record for columns "SessionDate",  "SessionLocation" and corresponding value for "PeopleTrained". Extract these values from the INITIAL RESPONSE. Take note that "SessionDate" is a DATE. "SessionLocation" is the character string after the date from the "SessionDate" entry. For example: for the object   {
            "SessionDate": "8/9/23 PNC Word",
            "SessionLocation": "Paranjut\nN.O.",
            "ConductedByName": "",
            "PeopleTrained": "40"
        }
        "SessionDate" should be 8/9/23 and "SessionLocation" should be PNC Word do such formatting for similar entries.
        For  the value of "PeopleTrained" extract only the numerical part from each and every entry.
                    You would also encounter a field named "Facility Name". Get that data also.
        """

        data_source_prompt = """
        Data Source: Image is provided below.

        """

        task = """
        Task: Return the corrected output in the below JSON format:

                    {
                    "SessionDate": "Value",
                    "sessionLocation": "Value",
                    "ConductedByName": -1,
                    "ClassType": "-1",
                    "PhotoSent": "-1",
                    "FacilityName": "Value",
                    "peopleTrained": "Value",
                "recordNumber": FROM 1 TO last number.
                    }
                    Keep the Facility Name same for all the records that you extracted.
        RETURN ONLY THE JSON OUPUT
        """


       
        chain_1 = create_chain(image_parts,model_object = model,initial_response=form_parser_input, background=background, problem=problem ,data_source_prompt=data_source_prompt, task=task)
        with open('chain_1.json', 'w') as f:
            json.dump(chain_1, f,indent=2)

     

        st.write("Chain 2 in progress...")
        """###CHAIN-2"""

        background = """
        Background: You are a skilled spelling corrector.

        """

        problem = """
        Problem: The INITIAL_RESPONSE has a column called "sessionLocation", the column has MANY SPELLING MISTAKES like ANC (OPD) is mistakenly written as ANC COPD in some records, PNC ward is written as PIIMC and many more.

        IMPORTANT:
        Ideally only 1 of the 4 words should appear in the "sessionLocation":
        1) ANC, 2) ANC (OPD), 3) PNC, 4) PNC (OPD).

        """

        task = """
        Task: As a skilled spelling corrector, your task is to correct the spelling mistakes in the column "sessionLocation". If the spelling is already correct, leave it and move to next. Return the corrected INITIAL_RESPONSE as output in the same format as the input.
        DO NOT MODIFY ANY OTHER COLUMN.
        Return only the JSON output

        """
       
        chain_2 = create_chain(image_parts,model_object = model,initial_response=chain_1, background=background, problem=problem, task=task)

        with open('chain_2.json', 'w') as f:
            json.dump(chain_2, f,indent=2)

      
        """###CHAIN-3"""
        st.write("Chain 3 in progress...")
        background = """
        Background: You are a professional grade and accurate data extractor from images no matter the quality.

        """

        problem = """
        Problem: The INITIAL_RESPONSE has correct number of record required but it has some columns valued as -1.


        """

        data_source_prompt = """
        Data Source: The following is the data that you will require to solve the problem:


        """

        task = """
        Task: Go through all the records in the image and modify the columns of INITIAL_RESPONSE which are valued as -1 EXCEPT THE COLUMN "ConductedByName". Return the final output that is the modified INITIAL_RESPONSE in the same format as the input. DO NOT MODIFY ANY OTHER COLUMN. Keep the number of records same as the INITIAL_RESPONSE.
        Return ONLY THE JSON OUTPUT

        """

       
        chain_3 = create_chain(image_parts,model_object = model,initial_response=chain_2, background=background, problem=problem, data_source_prompt=data_source_prompt, task=task)

        with open('chain_3.json', 'w') as f:
            json.dump(chain_3, f,indent=2)

        

        """###CHAIN-4"""
        st.write("Chain 4 in progress...")
        background = """
        Background: You are a skilled data corrector.

        """

        problem = """
        Problem: The INITIAL_RESPONSE has the exact number of records as required but the columns "sessionLocation" and "ClassType" has MAJOR AMBIGUITY. The "ClassType" column is a TICKMARK column with the following options:
        1) ANC, 2)PNC, 3)SNCU, 4)NBBSU.
        Ideally the "ClassType" output and "sessionLocation" output should match.
        For examples:
        If the "sessionLocation" is ANC (OPD) then the "ClassType" should be ANC.
        If the "sessionLocation" is PNC (OPD) then the "ClassType" should be PNC.


        """

        task = """
        Task: Your task is to remove this AMBIGUITY. Make the output of "ClassType" and "sessionLocation" SYNONIMOUS.
        Return the MODIFIED INITIAL_RESPONSE in the same format as input. ONLY MODIFY THE "ClassType" Column.
        ONLY RETURN THE JSON OUTPUT

        """

        chain_4 = create_chain(image_parts,model_object = model,initial_response=chain_3, background=background, problem=problem, task=task)

        with open('chain_4.json', 'w') as f:
            json.dump(chain_4, f,indent=2)
       
       

        """###CHAIN-5"""
        st.write("Chain 5 in progress...")
        background = """
        Background: You are a skilled data extractor.

        """

        problem = """
        Problem: The INITIAL_RESPONSE has messed up the "ConductedByName" column. All values are -1.

        """

        data_source_prompt = """
        Data Source: Below is the image

        """

        task = """
        Task: Your task is to correct the "ConductedByName" column based on the data provided. Return the modified INITIAL_RESPONSE in the same format as input.
        ONLY RETURN THE JSON OUTPUT

        """
    
        chain_5 = create_chain(image_parts,model_object = model,initial_response=chain_4, background=background, problem=problem,data_source_prompt=data_source_prompt, task=task)

    with open('chain_5.json', 'w') as f:
        json.dump(chain_5, f,indent=2)


    return chain_5


