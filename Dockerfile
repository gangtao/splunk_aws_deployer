FROM python:2.7-alpine
MAINTAINER gtao@splunk.com

# RUN apk --update --no-cache add py-pip
RUN pip install boto3

WORKDIR /root/dev

COPY ./deployer.py /root/dev

ENTRYPOINT ["python","deployer.py"]