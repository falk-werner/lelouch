FROM python:3.14-alpine

RUN pip install openai lelouch

COPY /examples/hello_agent.py /agent/agent.py

WORKDIR /workspace

ENTRYPOINT [ "python3", "/agent/agent.py" ]
