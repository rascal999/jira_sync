#!/usr/bin/env python

import argparse
import configparser
import re
import requests
import sys
import uuid
from jira import JIRA

def main():
    parser = argparse.ArgumentParser(description="Create a new Jira ticket and work directory.")
    parser.add_argument("--config", required=False, default="/config/config.ini",
                         help="File containing configuration for Jira (see config.ini.example).")
    parser.add_argument("--ticket-title", required=False, default=None,
                         help="Title of new ticket.")

    parsed = parser.parse_args()

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(parsed.config)

    # Get the Jira parameters
    base_url = config['Jira']['base_url']
    username = config['Jira']['username']
    api_key = config['Jira']['api_key']
    project_key = config['Jira']['project_key']
    issue_type = config['Jira']['issue_type']

    # Jira auth
    client = JIRA(base_url, basic_auth=(username, api_key))

    if parsed.ticket_title != None:
        summary = parsed.ticket_title
    else:
        summary = input("New Jira ticket title: ")

    # Determine if ticket has UUID
    if re.search(r'( \([a-f0-9]{4}\)$)',summary):
        pass
    else:
        # Summary uuid
        generated_uuid = uuid.uuid4()
        summary_uuid = str(generated_uuid).split('-')[2]

        summary = summary + " (" + summary_uuid + ")"

    print("Creating ticket...")

    issue_key = client.create_issue(
        summary=summary,
        project=project_key,
        issuetype="Task",
        #priority=priority,
        #labels=['test'] + parsed.labels,
        description="placeholder",
    )

    print(issue_key)

if __name__ == "__main__":
    main()
