#!/usr/bin/env bash

# Directory to watch
directory="/watch/"

# Watch for file changes indefinitely
while true; do
    # Use inotifywait to monitor directory for file changes
    change=$(inotifywait -m -q -e close_write --timeout 10 --include "\.md$" --format '%w%f' "$directory")

    echo "$change" | sort | uniq | tail -5 | while IFS= read -r line; do
        if [[ "$line" != "" ]]; then
            # Output the filename that triggered the change
            NOW=`date +"[%Y/%m/%d %H:%M:%S]"`
            echo "$NOW File '$line' was modified."

            # Add your custom logic here to respond to the file change
            ./jira_sync.py --ticket-file $line
            sleep 1
        fi
    done
done
