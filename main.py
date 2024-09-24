import argparse
import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter
import csv
import json
from tqdm import tqdm

class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)  # Use tqdm.write() instead of print()
            self.flush()
        except Exception:
            self.handleError(record)

def export_qdrant_collection_to_csv(host, port, collection_name, output_file, batch_size=100, payload_keys=None):
    # Configure logging with the custom handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(TqdmLoggingHandler())

    # Suppress qdrant_client logging messages lower than WARNING
    logging.getLogger('qdrant_client').setLevel(logging.WARNING)

    logger.info('Starting export of collection: %s', collection_name)

    try:
        # Initialize the Qdrant client
        client = QdrantClient(host=host, port=port)

        # Initialize variables
        last_point_id = None
        total_points_exported = 0

        # If payload_keys are not provided, perform an initial scan to collect them
        if not payload_keys:
            payload_keys = set()
            logger.info('No payload keys specified. Scanning collection to determine payload keys.')
            while True:
                response = client.scroll(
                    collection_name=collection_name,
                    scroll_filter=None,      # Retrieve all points
                    limit=batch_size,        # Batch size
                    with_payload=True,
                    with_vectors=False,      # We don't need vectors in this pass
                    offset=last_point_id
                )

                points, next_page_offset = response

                if not points:
                    break

                for point in points:
                    if point.payload:
                        payload_keys.update(point.payload.keys())

                last_point_id = next_page_offset

                if next_page_offset is None:
                    break

            payload_keys = list(payload_keys)
            logger.info('Payload keys found: %s', payload_keys)
        else:
            logger.info('Using specified payload keys: %s', payload_keys)

        # Prepare CSV headers
        headers = ['id', 'vector'] + payload_keys

        # Re-initialize scrolling parameters for data export
        last_point_id = None

        # Open CSV file and write headers
        logger.info('Writing data to CSV file: %s', output_file)
        with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            collection_info = client.get_collection(collection_name)
            total_points = collection_info.points_count
            pbar = tqdm(unit='points', total=total_points)

            while True:
                response = client.scroll(
                    collection_name=collection_name,
                    scroll_filter=None,
                    limit=batch_size,
                    with_payload=True,
                    with_vectors=True,   # Now we retrieve vectors
                    offset=last_point_id
                )

                points, next_page_offset = response

                if not points:
                    break

                for point in points:
                    row = {'id': point.id}

                    # Serialize vector as JSON string
                    if point.vector is not None:
                        row['vector'] = json.dumps(point.vector)
                    else:
                        row['vector'] = ''

                    # Expand payload fields
                    if point.payload:
                        for key in payload_keys:
                            value = point.payload.get(key, '')
                            # If value is a complex type, serialize it as JSON string
                            if isinstance(value, (dict, list)):
                                value = json.dumps(value)
                            row[key] = value
                    else:
                        # If no payload, set empty strings for all payload keys
                        for key in payload_keys:
                            row[key] = ''

                    writer.writerow(row)
                    total_points_exported += 1
                    pbar.update(1)

                last_point_id = next_page_offset

                if next_page_offset is None:
                    break

            pbar.close()

        logger.info('Export completed. Total points exported: %d', total_points_exported)
        logger.info('Data saved to %s', output_file)

    except Exception as e:
        logger.error('An error occurred during export: %s', str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Qdrant collection to CSV.')
    parser.add_argument('--host', type=str, required=True, help='Qdrant host.')
    parser.add_argument('--port', type=int, required=True, help='Qdrant port.')
    parser.add_argument('--collection', type=str, required=True, help='Name of the collection to export.')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file name.')
    parser.add_argument('--batch_size', type=int, default=100, help='Batch size for scrolling. Default is 100.')
    parser.add_argument('--payload_keys', type=str, nargs='*', help='List of payload keys to include.')
    # To use filters, you would need to define them appropriately
    # parser.add_argument('--filter', type=str, help='Filter to apply when exporting points.')

    args = parser.parse_args()

    export_qdrant_collection_to_csv(
        host=args.host,
        port=args.port,
        collection_name=args.collection,
        output_file=args.output,
        batch_size=args.batch_size,
        payload_keys=args.payload_keys
    )
