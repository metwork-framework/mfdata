#!/bin/bash

# Start Metwork services
/etc/init.d/metwork start

# Configure FTP server
sed -i "s/#chroot_local_user=YES/chroot_local_user=YES/g" /etc/vsftpd/vsftpd.conf
sed -i "s/anonymous_enable=YES/anonymous_enable=NO/g" /etc/vsftpd/vsftpd.conf

# Configure FTP directory
mkdir /integration_tests/ftped/

# Add FTP user
useradd -g metwork -d /integration_tests/ftped/ mfdata_ftp
printf 'mfdata_ftp\nmfdata_ftp' |passwd mfdata_ftp

chown mfdata_ftp:metwork /integration_tests/ftped/
chmod 777 /integration_tests/ftped/

# Start FTP
ver=$(rpm -qa \*-release | grep -Ei "oracle|redhat|centos" | cut -d"-" -f3)
if [ $ver -eq 6 ]
then
    service vsftpd start
else
    sudo systemctl start vsftpd
fi


#####################################
########## PLUGIN CREATION ##########
#####################################

su --command="/integration_tests/test_plugin_creations.sh" - mfdata

# Restart mfdata to take into account the config changes
/etc/init.d/metwork restart 

# Restart FTP
ver=$(rpm -qa \*-release | grep -Ei "oracle|redhat|centos" | cut -d"-" -f3)
if [ $ver -eq 6 ]
then
    service vsftpd restart
else
    sudo systemctl restart vsftpd
fi

####################################
########## TEST SCENARIOS ##########
####################################

chmod +x /integration_tests/convert.sh
chown mfdata:metwork /integration_tests/convert.sh
mv /integration_tests/convert.sh /home/mfdata/var/plugins/test_convert
/integration_tests/test_scenarios.sh

################################
########## UNIT TESTS ##########
################################
# Start Python unit tests to check if operations worked as intended
sleep 15
nosetests /integration_tests/unit_test.py
