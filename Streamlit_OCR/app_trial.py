
import os
import streamlit as st
import pandas as pd
import json
from pathlib import Path

from gemini_chained import model,process_document_from_file, convert_document_to_dictionary, json_structure, restructure_json, structured_dictionary, chained_prompts, create_chain, process_document_form_sample, process_document

def save_uploaded_file(uploaded_file):
    # Create a temporary directory to store the uploaded file
    temp_dir = "temp_upload_dir"
    os.makedirs(temp_dir, exist_ok=True)

    # Save the uploaded file to the temporary directory
    path = os.path.join(temp_dir, uploaded_file.name)
    with open(path, "wb") as file:
        file.write(uploaded_file.read())

    return path



def main():
    st.title("Handwriting Recognition")

    form_parser_input = None
    # Initialize session state for chains

    # Step 1: Upload Image and Details
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


    # Step 2: Run gemini_chained_cloned functions
    if st.button("Run") and uploaded_image is not None:
       
        path_of_file = save_uploaded_file(uploaded_image)
        processed_document = process_document_from_file(path_of_file)
    
        converted_output = convert_document_to_dictionary(processed_document)
        structured_json = json_structure(converted_output)
        restructured_json = restructure_json(structured_json)
        #using restructured_json to get final dictionary
        Dictionary = structured_dictionary(restructured_json)

        form_parser_input = json.dumps(Dictionary,indent=2)
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": Path(f"{path_of_file}").read_bytes()
            },
            ]


        
        def passf():
            pass
                # Assuming create_chain function takes a dictionary with the chain details
            #chain_output = chained_prompts(form_parser_input)
                #st.write(f"Chain {i} done.")
            
            # """###CHAIN-1"""

            # background = """
            #     Background: You are a skilled Data extractor and corrector
            #     """

            # problem = """
            #     Problem: From the images, Extract record for columns "SessionDate",  "SessionLocation" and corresponding value for "PeopleTrained". Extract these values from the INITIAL RESPONSE. Take note that "SessionDate" is a DATE. "SessionLocation" is the character string after the date from the "SessionDate" entry. For example: for the object   {
            #         "SessionDate": "8/9/23 PNC Word",
            #         "SessionLocation": "Paranjut\nN.O.",
            #         "ConductedByName": "",
            #         "PeopleTrained": "40"
            #     }
            #     "SessionDate" should be 8/9/23 and "SessionLocation" should be PNC Word do such formatting for similar entries.
            #     For  the value of "PeopleTrained" extract only the numerical part from each and every entry.
            #                 You would also encounter a field named "Facility Name". Get that data also.
            #     """

            # data_source_prompt = """
            #     Data Source: Image is provided below.

            #     """

            # task = """
            #     Task: Return the corrected output in the below JSON format:

            #                 {
            #                 "SessionDate": "Value",
            #                 "sessionLocation": "Value",
            #                 "ConductedByName": -1,
            #                 "ClassType": "-1",
            #                 "PhotoSent": "-1",
            #                 "FacilityName": "Value",
            #                 "peopleTrained": "Value",
            #             "recordNumber": FROM 1 TO last number.
            #                 }
            #                 Keep the Facility Name same for all the records that you extracted.
            #     RETURN ONLY THE JSON OUPUT
            #     """



            # chain_1 = create_chain(model_object = model,initial_response=form_parser_input, background=background, problem=problem ,data_source_prompt=data_source_prompt, image_parts=image_parts, task=task)
            # with open('chain_1.json', 'w') as f:
            #         json.dump(chain_1, f,indent=2)

            #     #print("Chain_1 Done")


            # """###CHAIN-2"""

            # background = """
            #     Background: You are a skilled spelling corrector.

            #     """

            # problem = """
            #     Problem: The INITIAL_RESPONSE has a column called "sessionLocation", the column has MANY SPELLING MISTAKES like ANC (OPD) is mistakenly written as ANC COPD in some records, PNC ward is written as PIIMC and many more.

            #     IMPORTANT:
            #     Ideally only 1 of the 4 words should appear in the "sessionLocation":
            #     1) ANC, 2) ANC (OPD), 3) PNC, 4) PNC (OPD).

            #     """

            # task = """
            #     Task: As a skilled spelling corrector, your task is to correct the spelling mistakes in the column "sessionLocation". If the spelling is already correct, leave it and move to next. Return the corrected INITIAL_RESPONSE as output in the same format as the input.
            #     DO NOT MODIFY ANY OTHER COLUMN.
            #     Return only the JSON output

            #     """

            # chain_2 = create_chain(model_object = model,initial_response=chain_1, background=background, problem=problem, image_parts=image_parts, task=task)

            # with open('chain_2.json', 'w') as f:
            #         json.dump(chain_2, f,indent=2)

            #     #print("Chain_2 Done")

            # """###CHAIN-3"""

            # background = """
            #     Background: You are a professional grade and accurate data extractor from images no matter the quality.

            #     """

            # problem = """
            #     Problem: The INITIAL_RESPONSE has correct number of record required but it has some columns valued as -1.


            #     """

            # data_source_prompt = """
            #     Data Source: The following is the data that you will require to solve the problem:


            #     """

            # task = """
            #     Task: Go through all the records in the image and modify the columns of INITIAL_RESPONSE which are valued as -1 EXCEPT THE COLUMN "ConductedByName". Return the final output that is the modified INITIAL_RESPONSE in the same format as the input. DO NOT MODIFY ANY OTHER COLUMN. Keep the number of records same as the INITIAL_RESPONSE.
            #     Return ONLY THE JSON OUTPUT

            #     """


            # chain_3 = create_chain(model_object = model,initial_response=chain_2, background=background, problem=problem, image_parts=image_parts, data_source_prompt=data_source_prompt, task=task)

            # with open('chain_3.json', 'w') as f:
            #         json.dump(chain_3, f,indent=2)

            #     #print("Chain_3 Done")

            # """###CHAIN-4"""

            # background = """
            #     Background: You are a skilled data corrector.

            #     """

            # problem = """
            #     Problem: The INITIAL_RESPONSE has the exact number of records as required but the columns "sessionLocation" and "ClassType" has MAJOR AMBIGUITY. The "ClassType" column is a TICKMARK column with the following options:
            #     1) ANC, 2)PNC, 3)SNCU, 4)NBBSU.
            #     Ideally the "ClassType" output and "sessionLocation" output should match.
            #     For examples:
            #     If the "sessionLocation" is ANC (OPD) then the "ClassType" should be ANC.
            #     If the "sessionLocation" is PNC (OPD) then the "ClassType" should be PNC.


            #     """

            # task = """
            #     Task: Your task is to remove this AMBIGUITY. Make the output of "ClassType" and "sessionLocation" SYNONIMOUS.
            #     Return the MODIFIED INITIAL_RESPONSE in the same format as input. ONLY MODIFY THE "ClassType" Column.
            #     ONLY RETURN THE JSON OUTPUT

            #     """

            # chain_4 = create_chain(model_object = model,initial_response=chain_3, background=background, problem=problem,image_parts=image_parts, task=task)

            # with open('chain_4.json', 'w') as f:
            #         json.dump(chain_4, f,indent=2)
            #     #The below 2 cells were running properly, if they also give error POST400, then above code is not wrong.
            #     #print("Chain_4 Done")

            # """###CHAIN-5"""

            # background = """
            #     Background: You are a skilled data extractor.

            #     """

            # problem = """
            #     Problem: The INITIAL_RESPONSE has messed up the "ConductedByName" column. All values are -1.

            #     """

            # data_source_prompt = """
            #     Data Source: Below is the image

            #     """

            # task = """
            #     Task: Your task is to correct the "ConductedByName" column based on the data provided. Return the modified INITIAL_RESPONSE in the same format as input.
            #     ONLY RETURN THE JSON OUTPUT

            #     """

            # chain_5 = create_chain(model_object = model,initial_response=chain_4, background=background, problem=problem,data_source_prompt=data_source_prompt,image_parts=image_parts, task=task)

            #with open('chain_5.json', 'w') as f:
            #        json.dump(chain_5, f,indent=2)

                #print(chain_5)
            # Combine all chain outputs into one JSON file for download
        
        output = chained_prompts(form_parser_input,image_parts)    
        final_output = json.dumps(output, indent=2)  # Ensure proper indentation for vertical formatting
        # convert json to pd dataframe
        
        
        with open('final_output.json', 'w') as f:
            f.write(output)
     
        with open('final_output.json') as json_file:
            data = json.load(json_file)
        df = pd.DataFrame(data)
        st.write(df)



        st.download_button(label="Download final Output", data=output, file_name="final_output.json", mime="application/json")
        st.success("All chains have been run and the output is ready for download.")

if __name__ == "__main__":
    main()
