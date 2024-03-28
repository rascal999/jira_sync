FROM alpine:latest

COPY inotify.sh jira_sync.py /root
RUN apk add --no-cache bash inotify-tools python3 py3-pip
RUN pip install requests jira
ENTRYPOINT [ "/root/inotify.sh" ]
