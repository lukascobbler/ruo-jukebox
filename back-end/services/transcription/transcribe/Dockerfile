FROM public.ecr.aws/lambda/python:3.11

RUN yum install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lambda.py ${LAMBDA_TASK_ROOT}

RUN mkdir -p /models && \
    python -c "import whisper; model = whisper.load_model('small'); model.save_pretrained('/models/small.pt')" || true

CMD ["lambda.lambda_handler"]
