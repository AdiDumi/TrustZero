import json
import os

LOG_FILE = '/var/log/apache2/modsec_audit.log'


def process_log_entry(entry):
    # Extract important information from the log entry
    ip_address = entry['transaction']['remote_address']
    request_method, request_uri = entry['request']['request_line'].split(' ', 1)
    status_code = entry['response']['status']
    message = entry['audit_data']['messages'][0] if entry['audit_data']['messages'] else "No message"

    return {
        'ip_address': ip_address,
        'request_method': request_method,
        'request_uri': request_uri,
        'status_code': status_code,
        'message': message
    }


def process_log_file():
    if not os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} does not exist.")
        return

    with open(LOG_FILE, 'r') as file:
        for line in file:
            try:
                entry = json.loads(line)
                processed_entry = process_log_entry(entry)
                print(json.dumps(processed_entry, indent=2))
            except json.JSONDecodeError:
                continue


if __name__ == "__main__":
    process_log_file()
