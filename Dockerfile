FROM ubuntu:14.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic tools and Python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    pkg-config \
    libgl1-mesa-glx \
    software-properties-common \
    python3 \
    python3-dev \
    python3-pip \
    python-numpy \
    python3-numpy \
    libjpeg-dev \
    libtiff-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libatlas-base-dev \
    gfortran \
    && apt-get clean

# Install SciPy
# RUN pip3 install scipy

# -------- Install Boost 1.59 --------
WORKDIR /opt
RUN wget https://sourceforge.net/projects/boost/files/boost/1.59.0/boost_1_59_0.tar.gz && \
    tar xzf boost_1_59_0.tar.gz && \
    cd boost_1_59_0 && \
    ./bootstrap.sh --with-libraries=filesystem,system,regex,python --with-python=python3 && \
    ./b2 install

# -------- Install OpenCV 2.4.9 --------
WORKDIR /opt
RUN wget https://github.com/opencv/opencv/archive/2.4.9.zip && \
    unzip 2.4.9.zip && \
    mkdir -p opencv-2.4.9/build && \
    cd opencv-2.4.9/build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
            -D CMAKE_INSTALL_PREFIX=/usr/local \
            -D PYTHON3_EXECUTABLE=/usr/bin/python3 \
            -D PYTHON3_INCLUDE_DIR=/usr/include/python3.4m \
            -D PYTHON3_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.4m.so \
            .. && \
    make -j$(nproc) && \
    make install && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf && \
    ldconfig




# Install Miniconda
RUN mkdir -p ~/miniconda3 \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh \
    && bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3 \
    && rm ~/miniconda3/miniconda.sh

# Set environment path
ENV PATH=~/miniconda3/bin:$PATH

# Create Python 3.11 environment and install packages with pip (with SSL fix)
RUN /bin/bash -c "source ~/miniconda3/etc/profile.d/conda.sh && \
    conda create -n usit python=3.11 -y && \
    conda activate usit && \
    python -m ensurepip && \
    pip install --upgrade pip certifi && \
    pip install --no-cache-dir scipy opencv-python matplotlib"


# # Activate environment by default in bash
RUN echo "source ~/miniconda3/etc/profile.d/conda.sh && conda activate usit" >> ~/.bashrc


WORKDIR /opt
COPY *.cpp version.h Makefile_linux.mak /opt/

RUN make -f Makefile_linux.mak install clean

ENV PATH=/root/bin:$PATH


# Clean up
RUN rm -rf /opt/*


# Set working directory
WORKDIR /app

CMD ["bash"]