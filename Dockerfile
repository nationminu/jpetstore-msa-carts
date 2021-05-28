# Set the base image
FROM python:3

LABEL maintainer="ssong. <mwsong@rockplace.co.kr>"

COPY ./ /usr/app/jpetstore

# Add ghost user
RUN useradd -m -s /bin/bash ghost && \
    mkdir -p /usr/app/jpetstore && \
    chown -R ghost:ghost /usr/app/jpetstore 

 
# Switch to ghost user
USER ghost:ghost
WORKDIR /usr/app/jpetstore 

RUN pip install -r requirement.txt && echo "python main.py" > /usr/app/jpetstore/entrypoint.sh && \ 
    chmod 700 /usr/app/jpetstore/entrypoint.sh 

ENTRYPOINT ["bash","-c","./entrypoint.sh"] 