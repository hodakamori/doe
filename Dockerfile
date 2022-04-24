FROM python:3.8

ARG prj_dir="/DOE/"

WORKDIR $prj_dir

RUN apt-get update \
    && apt-get update \
    && apt-get install -y r-base \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt $prj_dir

RUN R -e "install.packages('AlgDesign',dependencies=TRUE, repos='http://cran.rstudio.com/')"

RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt \
    && rm -r ~/.cache/pip

COPY . $prj_dir