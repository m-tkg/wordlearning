FROM centos:6
ENV HOME /
RUN yum -y update
RUN yum -y install epel-release 
RUN yum -y groupinstall "Development Tools" "Compatibility Libraries"
RUN yum -y install git curl bzip2 gcc make openssl-devel readline-devel zlib-devel rpmdevtools yum-utils libevent-devel mysql-devel openldap-devel vim sqlite-devel
RUN yum -y install cronie
RUN yum -y install mysql-server

WORKDIR /root/
RUN git clone https://github.com/tagomoris/xbuild.git
RUN sh /root/xbuild/python-install 3.6.0 /root/local/python-3.6.0
RUN echo 'export PATH=/root/local/python-3.6.0/bin:$PATH' >> /root/.bashrc

RUN service mysqld start && mysql -u root -e 'CREATE DATABASE wordlearning CHARACTER SET utf8;' && mysql -u root -e 'GRANT ALL PRIVILEGES ON wordlearning.* TO wordlearning@localhost IDENTIFIED BY "wordlearning";'
RUN PATH=/root/local/python-3.6.0/bin:$PATH; pip install beautifulsoup4 lxml django uwsgi mysqlclient readability-lxml


expose 8080
ENTRYPOINT service mysqld start; tail -f /dev/null
