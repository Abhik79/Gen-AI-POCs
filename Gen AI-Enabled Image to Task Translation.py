import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.cloud import storage
import pandas as pd
from xlsxwriter.workbook import Workbook
from datetime import datetime
import configparser
import json
import logging
import os

def is_empty_or_whitespace(s):
    # Function to check if a string is empty or consists only of whitespace
    return s is None or s.isspace() or not s

def generate_text_response(client, gcs_path, context, task, output_format,default_prompt_flag):

    # Initialize Vertex AI
    vertexai.init(project=project_name_param, location=region)

    # Load the model
    multimodal_model = GenerativeModel("gemini-pro-vision")

    # Format the context, task, and output_format
    #context, task, output_format = f"Context: {context}", f"Task: {task}", f"Format: {output_format}"

    # CTF Format used in prompt
    default_prompt="""
            Context : Need to convert flowchart to Steps
            Task : - Generate a JSON structure representing a list of steps. Each step Desciption must have at least 10 words.
                   - Additional Steps can be created to highlight relation between each steps.
                   - Steps must be reference other steps if there are dependencies.
                   - Each step should be a dictionary with the following keys:
                    "Step number": an integer representing the step number.
                    "Step Description": a string describing the step with at least 10 words.
            Format :
                    [
                        {
                          "Step number":1,
                          "Step Description": "Discuss project concept with stakeholders."
                        },
                        {
                          "Step number":2,
                          "Step Description": "Do stakeholders approve of project concept?"
                        }
                    ]            
                    """

    # Use default prompt if any of the input values are empty or whitespace
    #if any(is_empty_or_whitespace(param.split(':')[1]) for param in [context, task, output_format]):
    if default_prompt_flag is True:
        prompt = default_prompt
    else:
        prompt = "\n".join([context, task, output_format])

    # Query the model
    response = multimodal_model.generate_content(
        [
            Part.from_uri(gcs_path, mime_type="image/jpeg"),
            # CTF Format used in prompt
            prompt
        ],
        # Output configuration
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        }
    )

    # Return the text part of the response
    return response.text


def process_image_file(client, bucket_name, file_name, local_file_path, writer):
    # Extracting the sheet name from the file name, truncating to 30 characters
    sheet_name = file_name.split('.')[0][:30]
    # Extracting the file name without the path
    file_name = file_name.split('/')[-1]
    logger.info(f"Processing file: {file_name} in bucket {bucket_name}")

    # Generating Google Cloud Storage and local file paths
    gcs_file_path = f"gs://{bucket_name}/{file_name}"
    local_image_path = f"{local_file_path}\\{file_name}"

    # Calling the function to generate text response based on the image content
    text = generate_text_response(client, gcs_file_path, context, task, output_format,default_prompt_flag)
    
    #print(text)
    try:
        # Evaluating the generated text as a Python expression
        final_dictionary = json.loads(text) 
        # Creating a pandas DataFrame from the dictionary
        df = pd.DataFrame(final_dictionary)

        # Writing the DataFrame to an Excel sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Formatting Excel sheet with header and cell styles
        num_rows, num_cols = df.shape
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'align': 'center',
            'fg_color': '#00FFFF',
            'border': 1,
            'font_size': 12,
            'font_color': 'black'
        })

        # Writing column headers to the Excel sheet
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Applying conditional formatting to the data cells
        cell_format = workbook.add_format({'border': 1})
        worksheet.conditional_format(1, 0, num_rows, num_cols - 1, {'type': 'no_blanks', 'format': cell_format})
        worksheet.autofit()

        # Downloading the image file and inserting it into the Excel sheet
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.download_to_filename(local_image_path)
        worksheet.insert_image(num_rows + 2, 0, local_image_path, {'x_offset': 15, 'y_offset': 10, 'x_scale': 0.2, 'y_scale': 0.2})
        logger.info(f"Processed file: {file_name}")

    except ValueError as e:
        # Handling JSON parsing error
        logger.error(f"Error parsing JSON: {e}")
        final_dictionary = None    
    except Exception as e:
        # Handling exceptions and printing an error message
        logger.error(f"An error occurred: {e}")
        final_dictionary = None

    # Checking the result of the evaluation
    if final_dictionary is not None:
        logger.info("Successfully evaluated the dictionary")
    else:
        logger.error(f"Failed to evaluate the dictionary for image file : {file_name}")
    
    print()


def image_to_task_generator(project_name_param, region, bucket_name_param, local_file_fixed_path, output_file_path,output_file_name_prefix,output_file_name_suffix, context, task, output_format):
    
    # Initializing Google Cloud Storage client and generating output file name
    client = storage.Client(project=project_name_param)
    extract_datetime = datetime.today().strftime("%Y%m%d_%H%M%S")
    output_file_name = f'{output_file_path}\\{output_file_name_prefix}_{extract_datetime}_{output_file_name_suffix}.xlsx'
    
    # Initializing Excel writer
    writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')

    
    blob_list = list(client.list_blobs(bucket_name_param))
    
    if not blob_list:
        logger.warning(f"No files found in the bucket: {bucket_name_param}")
    else:
    # Processing each file in the specified bucket
        for blob in blob_list:
            file_name = str(blob.name)
            _, file_extension = os.path.splitext(file_name)
    
            if file_extension.lower() in ['.jpg', '.jpeg', '.png']:
                process_image_file(client, bucket_name_param, file_name, local_file_fixed_path, writer)
            else:
                logger.warning(f"Invalid file format for {file_name}. Only jpg and png files are supported.")
            
        # Closing the Excel writer and printing the generated output file name
        writer.close()
        logger.info(f"Generated Output File: {output_file_name}")
        
    
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DEFAULT']
	


if __name__ == "__main__":
    try:
        config = load_config()
    
        project_name_param = config.get('project_name')
        region = config.get('region')
        bucket_name_param = config.get('bucket_name')
        local_file_fixed_path = config.get('local_file_path')
        output_file_path = config.get('output_file_path')
        log_folder_path = config.get('log_folder_path')
        output_file_name_prefix = config.get('output_file_name_prefix')
        default_prompt_flag=False
        
        # Configure the logging settings
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        
        # Create the log folder if it doesn't exist
        os.makedirs(log_folder_path, exist_ok=True)
        
        # Create a file handler with a dynamic log file name and folder path
        log_file_name = 'image_to_task_gen_app.log'
        log_file_path = os.path.join(log_folder_path, log_file_name)
        file_handler = logging.FileHandler(log_file_path, mode='a')
        file_handler.setLevel(logging.INFO)
        
        # Create a formatter and add it to the file handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the file handler to the logger
        logger.addHandler(file_handler)    
    
        # CTF Format used in prompt designing.Copy from here during custom input
        """
        Context : Need to convert Flowchart to Steps
        
        Task : Generate a JSON structure representing a list of steps. Each step Desciption must have at least 10 words.
                Each step should be a dictionary with the following keys:
                    "Step number": an integer representing the step number.
                    "Step Description": a string describing the step with at least 10 words.
            
        Format : 
                        [
                            {
                              "Step number":1,
                              "Step Description": "Discuss project concept with stakeholders."
                            },
                            {
                              "Step number":2,
                              "Step Description": "Do stakeholders approve of project concept?"
                            }
                        ]     
        """
        
                    
        # Uncomment the following lines for user input
        context = input("Enter the context: ")
        task = input("Enter the task description: ")
        output_format = input("Enter the output format (in JSON structure): ")
    
        if any(is_empty_or_whitespace(param) for param in [context, task, output_format]):
            logger.info("Proceeding with default_prompt")
            output_file_name_suffix = 'DefaultPrompt'
            default_prompt_flag=True
        else:
            logger.info("Proceeding with custom prompt")
            output_file_name_suffix = 'CustomPrompt'
        
        # Invoking the image_to_task_generator function with the specified parameters
        image_to_task_generator(
            project_name_param,
            region,
            bucket_name_param,
            local_file_fixed_path,
            output_file_path,
            output_file_name_prefix,
            output_file_name_suffix,
            context,
            task,
            output_format
        )
        
    except Exception as e:
        # Log the exception and any additional information you want
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        file_handler.close()
        logging.shutdown()