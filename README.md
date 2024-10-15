# Image-to-Task Generator

This project is a Python-based application that processes image files stored in a Google Cloud Storage (GCS) bucket, generates text responses using Vertex AI's generative models, and saves the output in an Excel file. The project is designed to convert flowchart images into structured JSON representations of steps.

## Features

- **Image Processing**: Downloads images from a specified GCS bucket and processes each image to generate a text-based description.
- **Text Generation**: Uses Vertex AI's multimodal generative models to convert flowchart images into structured JSON steps.
- **Excel Output**: Saves the generated JSON structure into an Excel sheet with formatting, including headers and cell borders.
- **Image Insertion**: Inserts the processed image directly into the Excel file.
- **Configurable Prompts**: Allows using a default or custom prompt to generate the JSON structure.
- **Error Handling**: Catches and logs errors during processing and saves logs to a file.

## Prerequisites

- **Python 3.x**
- **Google Cloud SDK**: For interacting with Google Cloud Storage.
- **Vertex AI Python SDK**: For using Vertex AI's generative models.
- **Pandas & XlsxWriter**: For creating and formatting Excel files.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/image-to-task-generator.git
    cd image-to-task-generator
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # For Windows, use venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application requires a `config.ini` file with the following structure:

```ini
[DEFAULT]
project_name = your-gcp-project-id
region = your-gcp-region
bucket_name = your-gcs-bucket-name
image_file_path = path/to/local/image/storage
output_file_path = path/to/local/output/files
log_folder_path = path/to/log/folder
output_file_name_prefix = output_file_prefix
```

Make sure to replace `your-gcp-project-id`, `your-gcp-region`, `your-gcs-bucket-name`, and other parameters as needed.

## Usage

Run the application using the following command:

```bash
python main.py
```

### Parameters

- **Context**: Enter the context for the prompt (e.g., "Need to convert flowchart to steps").
- **Task**: Enter a description of the task (e.g., "Generate a JSON structure representing a list of steps").
- **Output Format**: Specify the output format (in JSON structure).

If any of the inputs are empty, the application will proceed with a default prompt.

## Example

```
Context : Need to convert Flowchart to Steps
Task : Generate a JSON structure representing a list of steps. Each step should be a dictionary with the following keys:
  - "Step number": an integer representing the step number.
  - "Step Description": a string describing the step.
Format : JSON format
```

The generated output will look like:

```json
[
    {
        "Step number": 1,
        "Step Description": "Discuss project concept with stakeholders."
    },
    {
        "Step number": 2,
        "Step Description": "Do stakeholders approve of project concept?"
    }
]
```

The results, including the image and structured steps, are saved in an Excel file.

## Logging

- Logs are saved to a file named `image_to_task_gen_app.log` in the specified log folder.
- The logs include details about processed files, errors, and other events.

## Notes

- Supported image formats: `.jpg`, `.jpeg`, `.png`
- The script pauses for 30 seconds after processing each file to prevent overloading the API.

## Troubleshooting

- Ensure that the Google Cloud credentials are set up properly and accessible for the service account.
- Verify that the `config.ini` file has the correct project and bucket details.
- Check the log file for detailed error messages if the script fails.
