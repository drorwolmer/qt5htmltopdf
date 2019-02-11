FROM python:3.6.6-stretch

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libegl1-mesa \
        libxrandr2 \
        libxss1 \
        libxcursor1 \
        libxcomposite1 \
        libasound2 \
        libxi6 \
        libxtst6 \
        wkhtmltopdf \
        xvfb \
        libnss3 \
    && rm -rf /var/lib/apt/lists/*

RUN echo "#"'!'"/bin/bash\nxvfb-run -a --server-args=\"-screen 0, 1024x768x24\" /usr/bin/wkhtmltopdf -q "'$*' > /usr/bin/wkhtmltopdf.sh \
    && chmod a+x /usr/bin/wkhtmltopdf.sh \
    && ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf


RUN pip install PyQt5==5.11.3 xvfbwrapper==0.2.9

ENV QTWEBENGINE_CHROMIUM_FLAGS=--no-sandbox
ENV QTWEBENGINE_DISABLE_SANDBOX=1

COPY build_pdf.py .

ENTRYPOINT ["python", "./build_pdf.py"]
