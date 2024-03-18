FROM python:alpine

RUN pip install --no-cache-dir metrixpp

ENTRYPOINT [ "metrix++" ]

CMD [ "metrix++" ]