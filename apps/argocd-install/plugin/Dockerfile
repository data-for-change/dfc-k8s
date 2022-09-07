FROM quay.io/argoproj/argocd:v2.4.11
USER root
RUN apt update && apt install -y python3 python3-pip
RUN pip install kubernetes==24.2.0
USER 999
