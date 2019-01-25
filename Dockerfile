FROM continuumio/miniconda3

WORKDIR /app

COPY requirements.txt /app
COPY aemvl_backend /app

RUN conda create -n aemvl-backend python=3.6
RUN echo "source activate aemvl-backend" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

RUN conda install --file requirements.txt
ENV GDAL_DATA /opt/miniconda3/envs/aemvl-backend/share/epsg_csv

RUN pip install python-dotenv

ARG version
ARG secret
ENV VERSION=$version
ENV SECRET_KEY=$secret

ENV DOCKER True
ENV UPLOAD_FOLDER /data/uploads
ENV DOWNLOADS_FOLDER /data/downloads

VOLUME ["/data"]

#EXPOSE 8000
#CMD ["gunicorn",  "--config", "/app/src/config/gunicorn_config.py", "app:server"]
EXPOSE 8080
CMD ["python", "main.py"]
