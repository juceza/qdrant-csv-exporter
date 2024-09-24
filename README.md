
# Qdrant CSV Exporter

A Python script to export data from a Qdrant collection to a CSV file. This script allows you to export points from a Qdrant collection, including their vectors and payloads, with options to customize the export process.

## Features

- Exports all points from a specified Qdrant collection.
- Includes vectors serialized as JSON strings in the CSV file.
- Expands payload keys into individual columns.
- Allows specifying payload keys to include, avoiding unnecessary scanning.
- Supports batch processing for efficient handling of large collections.
- Provides a progress bar and logging for monitoring the export process.
- Error handling for robust execution.

## Requirements

- Python 3.6 or higher
- `qdrant-client` library
- `tqdm` library

## Installation

1. **Clone the Repository**

   ```
   git clone https://github.com/yourusername/qdrant-csv-exporter.git
   cd qdrant-csv-exporter
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```
   pip install -r requirements.txt
   ```

   Alternatively, install the required packages directly:

   ```
   pip install qdrant-client tqdm
   ```

## Usage

The script can be run from the command line with various options:

```
python3 export_qdrant_to_csv.py \
    --host <QDRANT_HOST> \
    --port <QDRANT_PORT> \
    --collection <COLLECTION_NAME> \
    --output <OUTPUT_CSV_FILE> \
    [--batch_size <BATCH_SIZE>] \
    [--payload_keys <PAYLOAD_KEY1> <PAYLOAD_KEY2> ...]
```

### Arguments

- `--host`: Qdrant host address (required).
- `--port`: Qdrant port number (required).
- `--collection`: Name of the Qdrant collection to export (required).
- `--output`: Output CSV file name (required).
- `--batch_size`: Number of points to fetch per batch (optional, default is 100).
- `--payload_keys`: List of payload keys to include (optional). If not specified, the script scans the collection to determine payload keys.

### Examples

**Export with Specified Payload Keys**

If you know the payload keys you want to include, specify them using `--payload_keys`:

```
python3 export_qdrant_to_csv.py \
    --host localhost \
    --port 6333 \
    --collection my_collection \
    --output output.csv \
    --batch_size 500 \
    --payload_keys title author date
```

**Export Without Specifying Payload Keys**

If you don't specify `--payload_keys`, the script will perform an initial scan to collect all payload keys:

```
python3 export_qdrant_to_csv.py \
    --host localhost \
    --port 6333 \
    --collection my_collection \
    --output output.csv \
    --batch_size 500
```

## Script Details

The script performs the following steps:

1. **Initialization**

   - Configures logging to display progress and status messages.
   - Connects to the Qdrant instance using the provided host and port.

2. **Payload Keys Determination**

   - If `--payload_keys` are not specified, performs an initial scan to collect all unique payload keys.
   - If `--payload_keys` are specified, uses them directly, which can save time for large collections.

3. **Data Export**

   - Prepares the CSV headers, including `id`, `vector`, and the payload keys.
   - Retrieves points from the collection in batches, including vectors and payloads.
   - Vectors are serialized as JSON strings and stored in the `vector` column.
   - Payloads are expanded into individual columns based on the payload keys.
   - Progress is displayed using a progress bar.

4. **Completion**

   - Upon completion, logs the total number of points exported and the location of the output CSV file.

## Error Handling

The script includes error handling to manage exceptions that may occur during execution, such as:

- Connection errors to the Qdrant instance.
- Issues with writing to the output file.
- Interruptions by the user (e.g., pressing `Ctrl+C`).

## Notes

- **Vectors and Payloads**

  - Vectors are stored as JSON strings in the `vector` column.
  - Payload values are stored in their respective columns. If a payload value is a complex type (e.g., list or dictionary), it is serialized as a JSON string.

- **Performance Considerations**

  - Specifying `--payload_keys` can improve performance by avoiding the initial scan to collect payload keys.
  - Adjust `--batch_size` according to your system's capabilities and the size of the data.

- **Logging and Progress Bar**

  - The script provides detailed logging and a progress bar to monitor the export process.
  - Log messages are displayed without interfering with the progress bar.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your improvements.
