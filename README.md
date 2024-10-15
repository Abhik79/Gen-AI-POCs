# Image to Task Generator

## Overview
The **Image to Task Generator** is a Python-based project that leverages Google Cloud's Vertex AI to convert images of flowcharts into structured step-by-step instructions. The output is formatted as a JSON structure and is saved to an Excel file. This project is particularly useful for automating the extraction of tasks from visual flowcharts.

## Features
- Uploads images from a Google Cloud Storage (GCS) bucket.
- Processes images using Vertex AI to generate textual descriptions.
- Formats the output in a JSON structure.
- Saves results in an Excel file with customized formatting.
- Implements logging for better tracking of operations.
- Introduces a delay between processing files to manage resource allocation.

## Requirements
To run this notebook, you will need the following libraries:
- `pandas`
- `google-cloud-storage`
- `google-cloud-aiplatform`
- `xlsxwriter`
- `logging`

## Setup Instructions

1. **Install Required Libraries**   
   The requirements.txt file is given. Make sure to run the cell.

2. **Configure Google Cloud Credentials**
   Set up your Google Cloud credentials to enable access to the storage and AI services. You may need to authenticate using a service account or user account with the necessary permissions.

3. **Configuration File**
   Create a configuration file named `config.ini` in the same directory as your Jupyter notebook. This file should contain the following parameters:
   ```ini
   [DEFAULT]
   project_name = your_project_name
   region = your_region
   bucket_name = your_bucket_name
   image_file_path = your_local_image_folder_path
   output_file_path = your_local_output_folder_path
   log_folder_path = your_local_log_folder_path
   output_file_name_prefix = your_output_file_name_prefix
   ```

## Usage Instructions

1. **Run the Notebook**
   Open the Jupyter notebook and execute the cells in order. You will be prompted to enter the context, task description, and output format. If you leave these fields blank, the program will use a default prompt.

2. **Processing Files**
   The notebook will:
   - Clear the specified local folder of previous images.
   - List and process images from the specified Google Cloud Storage bucket.
   - Generate text responses based on the content of the images.
   - Save the processed data into an Excel file with the specified formatting.

3. **Logging**
   All operations are logged, including any errors encountered during processing. The log file will be created in the specified log folder.

## Notes
- The code includes a sleep of 30 seconds between the processing of each file to manage resource usage.
- Ensure your Google Cloud project is properly configured with the necessary APIs enabled (e.g., Vertex AI, Cloud Storage).

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [Google Cloud AI Platform](https://cloud.google.com/ai-platform)
- [Pandas Documentation](https://pandas.pydata.org/)
- [XlsxWriter Documentation](https://xlsxwriter.readthedocs.io/)

This README provides a comprehensive guide for users to understand, set up, and use your Jupyter notebook effectively. Let me know if you need any adjustments!
