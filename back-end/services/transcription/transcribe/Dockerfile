FROM public.ecr.aws/lambda/python:3.11

RUN yum install -y git tar xz gzip bzip2 curl gcc g++ make && yum clean all

RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz && \
    tar -xJf /tmp/ffmpeg.tar.xz -C /tmp && \
    mv /tmp/ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ffmpeg && \
    chmod +x /usr/local/bin/ffmpeg && \
    rm -rf /tmp/ffmpeg*

RUN rm -rf /var/cache/yum

COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools && \
    pip install --only-binary=:all: tiktoken && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

COPY lambda.py ${LAMBDA_TASK_ROOT}

RUN mkdir -p /models && \
    python -c "import whisper; whisper.load_model('small')" || true

CMD ["lambda.lambda_handler"]
