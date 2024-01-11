"""
pgverify.py
This script reads the postgresql.conf file and outputs the settings to the console and a JSON file.
The JSON file is appended with the results of each run.
The script can be run with the following command:
python pgverify.py [path_to_postgresql.conf]
If no path is specified, the default path is used: /etc/postgresql/15/main/postgresql.conf
The script can be run on a single node or on all nodes in a cluster.

Rudy Rodarte
2024-01-11 - Initial version

"""
import re
import sys
import subprocess
import json

def get_node_name():
    # Try to get the cluster name using the `pg_lsclusters` command
    try:
        output = subprocess.check_output(['pg_lsclusters', '-h'], universal_newlines=True)
        # Extract the cluster name (which is typically "main" in default installations)
        cluster_name = output.splitlines()[1].split()[-1]
        return cluster_name
    except:
        return "Unknown"

def read_postgres_conf(file_path):
    # Define the settings we're interested in
    settings = [
        "listen_addresses", "port", "max_connections", "shared_buffers", 
        "work_mem", "maintenance_work_mem", "wal_level", "max_wal_size", "min_wal_size"
        "archive_mode", "log_statement", "log_duration", "hot_standby","synchronous_commit",
        "autovacuum", "log_timezone", "timezone", "ssl", "Password_encryption",
        "effective_cache_size","random_page_cost", "seq_page_cost", "shared_preload_libraries"
    ]
    
    # Initialize a dictionary with "Not Set" as default for all settings and empty comments
    values = {setting: {"value": "Not Set", "comment": ""} for setting in settings}

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Remove leading and trailing whitespaces
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                for setting in settings:
                    if line.startswith(setting):
                        # Extract the value and possible comment using a regular expression
                        match = re.search(r'^\s*{}\s*=\s*([^#\s]*)\s*(?:#\s*(.*))?'.format(setting), line)
                        if match:
                            values[setting]["value"] = match.group(1).strip("'\"")
                            if match.group(2):
                                values[setting]["comment"] = match.group(2).strip()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    return values

if __name__ == "__main__":
    default_path = "/etc/postgresql/15/main/postgresql.conf"
    output_file = "/tmp/linuxverification.json"
    
    if len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python pgverify.py [path_to_postgresql.conf]")
        print(f"Default path if not specified: {default_path}")
        print("Example: python pgverify.py /path/to/your/postgresql.conf")
    else:
        file_path = sys.argv[1] if len(sys.argv) > 1 else default_path
        values = read_postgres_conf(file_path)

        if values:
            # Get the node name
            node_name = get_node_name()
            output_data = {
                "Postgres Node Name": node_name,
                "Settings": values
            }

           # Output to the console
            print(f"Postgres Node Name: {node_name}\n")
            print("{:<20} | {:<15} | {}".format("Setting", "Current Value", "Comment"))
            print("-" * 65)
            for setting, data in values.items():
                print("{:<20} | {:<15} | {}".format(setting, data["value"], data["comment"]))
       

            # Append the results to the file in JSON format
            with open(output_file, 'a') as json_file:
                json_file.write(json.dumps(output_data, indent=4))
                json_file.write('\n')  # Separate entries by a newline

            print(f"Results appended to: {output_file}")