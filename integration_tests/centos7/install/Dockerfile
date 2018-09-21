FROM centos/systemd
ENV LANG=en_US.utf8
ENV TERM=xterm

LABEL name="mfdata installed" desc="Docker image with mfdata installed" version="1.0"

# Install wget
# FIXME remove which
RUN yum -y install wget xz ImageMagick vsftpd which sudo

# Metwork installation
ADD ./integration_tests/metwork.repo /etc/yum.repos.d/metwork.repo
RUN yum -y install metwork-mfdata

# Add xattrfile module to use in testing
ADD ./xattrfile/xattrfile /xattrfile
RUN export PYTHONPATH="${PYTHONPATH}:/xattrfile"

# Install pip then nosetests
RUN wget https://bootstrap.pypa.io/2.6/get-pip.py && python get-pip.py

RUN pip install nose redis mockredispy six python-magic
