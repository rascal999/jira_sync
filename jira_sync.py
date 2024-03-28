#!/usr/bin/env python

import argparse
import configparser
import re
import requests
import sys
import uuid
from jira import JIRA

def main():
    parser = argparse.ArgumentParser(description="Update Jira when logseq files change.")
    parser.add_argument("--config", required=False, default="/config/config.ini",
                         help="File containing configuration for Jira (see config.ini.example).")
    parser.add_argument("--ticket-file", required=True,
                         help="File to use in order to create or update a Jira ticket.")

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

    # Read the contents of the file
    with open(parsed.ticket_file, 'r') as file:
        ticket_content = file.read()

    # Fetch summary and check if partial uuid present
    summary_check = ticket_content.strip().splitlines()[0].split('## ')[1]

    # Determine if ticket has UUID (probably exists in Jira)
    if re.search(r'( \([a-f0-9]{4}\)$)',summary_check):
        print("UUID found in summary")
        summary = summary_check
    else:
        # Summary uuid
        generated_uuid = uuid.uuid4()
        summary_uuid = str(generated_uuid).split('-')[2]

        summary = ticket_content.strip().splitlines()[0].split('## ')[1] + " (" + summary_uuid + ")"

        # Update md file to include UUID
        with open(parsed.ticket_file, 'r') as file:
            lines = file.readlines()

        if lines:
            lines[0] = "## " + summary + '\n'

            # Write the modified contents back to the file
            with open(parsed.ticket_file, 'w') as file:
                file.writelines(lines)

    cleaned_text = re.sub(r'(^##.*|:LOGBOOK:|CLOCK: .*|:END:|.*Ticket URL.*)', '', ticket_content)
    cleaned_text = re.sub(r'(\*\*)', '*', cleaned_text)
    output_text = '\n'.join(line for line in cleaned_text.splitlines() if line.strip())

    # Jira auth
    client = JIRA(base_url, basic_auth=(username, api_key))

    # JQL query to search for tickets by summary
    jql_query = f'project = {project_key} AND summary ~ "{summary}"'

    # Search for issues
    issues = client.search_issues(jql_query, maxResults=1)

    # Check if any issues were found
    if issues:
        issue = issues[0]
        print(f"Found matching issue: {issue.key}")

        # Update ticket description
        with open(parsed.ticket_file, 'r') as file:
            ticket_content = file.read()

        new_description = f"{output_text}"
        issue.update(description=new_description)
        print(f"Updating ticket {issue.key}.")
    else:
        print("Creating ticket.")

        issue_key = client.create_issue(
            summary=summary,
            project=JIRA_PROJECT_KEY,
            issuetype="Task",
            #priority=priority,
            #labels=['test'] + parsed.labels,
            description=f"{output_text}",
        )

if __name__ == "__main__":
    main()
