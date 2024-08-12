FROM python:3.11

RUN apt update -y && apt upgrade -y && \ 
    apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/* 
    
#RUN git clone https://github.com/Vishnu9783/Multi-FSub app
RUN git clone https://github.com/manchuriyan1/Multi-FSub-tkn app
WORKDIR app

RUN pip3 install -r requirements.txt

CMD ["bash", "start"]
