#!/bin/bash

# Create Layerapi2 files
# Pass plugin name as parameter
function layerapi() {
cat > /home/mfdata/$1/.layerapi2_label <<EOF
    plugin_$1@mfdata
EOF
cat > /home/mfdata/$1/.layerapi2_dependencies <<EOF
root@mfdata
python3@mfdata
EOF
}

# Activate debug logging
sed -i "s/# default_level=INFO/default_level=DEBUG/g" /home/mfdata/config/config.ini

# Move trash instead of deleting it
mkdir /integration_tests/trashed
chmod -R 777 /integration_tests/trashed
sed -i "s/# switch_no_match_policy=delete/switch_no_match_policy=move/g" /home/mfdata/config/config.ini
sed -i "s/# switch_no_match_move_policy_dest_dir=\/dev\/null/switch_no_match_move_policy_dest_dir=\/integration_tests\/trashed\//g" /home/mfdata/config/config.ini

##### Archive plugin #####
plugin="test_archive"

# Archive all images
cond="( b\"image\" in x[\"latest.switch.main.system_magic\"] )"
printf '\n\n1\n\n\n\n\n\n' | bootstrap_plugin.py create --template=archive $plugin

# Edit config file
cd /home/mfdata/$plugin
layerapi $plugin
sed -i "s/switch_logical_condition = False/switch_logical_condition = $cond/g" config.ini
# Change archive directory
sed -i "s/arg_dest-dir = {{MODULE_RUNTIME_HOME}}\/var\/archive/arg_dest-dir = \/integration_tests\/archived\//g" config.ini
# Change archiving format
sed -i "s/arg_strftime-template = %Y%m%d\/{RANDOM_ID}/arg_strftime-template = {ORIGINAL_BASENAME}/g" config.ini

# Release plugin
make release
# Find the plugin file's name and install
plugin_arc_file=$(find -L . -name "$plugin*.plugin")
plugins.install $plugin_arc_file
cd /home/mfdata/


##### Ungzip plugin #####
plugin_unz_file=$(find -L /opt/metwork-mfdata/share/plugins/ -name 'ungzip*')
plugins.install $plugin_unz_file


##### Chained plugins (convert + move) #####
### Convert plugin ###
plugin="test_convert"
cond="( x[\"latest.switch.main.system_magic\"].startswith(b\"PNG image\") )"
printf '\n\n2\n\n\n\n\n\n' | bootstrap_plugin.py create --template=fork $plugin

# Script to convert image
cd /home/mfdata/$plugin
layerapi $plugin

# Edit config file
sed -i "s/switch_logical_condition = False/switch_logical_condition = $cond/g" config.ini
# Command template
sed -i "s/arg_command-template = /arg_command-template = {PLUGIN_DIR}\/convert.sh {PATH}/g" config.ini

# Release and install plugin
make release
# Find the plugin file's name
plugin_con_file=$(find -L . -name "$plugin*.plugin")
plugins.install $plugin_con_file
cd /home/mfdata/

### Move plugin ###
plugin="test_move"
printf '\n\n3\n\n\n\n\n\n\n\n' | bootstrap_plugin.py create --template=move $plugin

# Edit config file
cd /home/mfdata/$plugin
layerapi $plugin
sed -i "s/arg_dest-dir = /arg_dest-dir = \/integration_tests\/moved\//g" config.ini

# Release and install plugin
make release
# Find the plugin file's name
plugin_mov_file=$(find -L . -name "$plugin*.plugin")
plugins.install $plugin_mov_file
cd /home/mfdata/

##### FTP send #####
# Configure FTP plugin
plugin="test_ftp"
cond="True"
printf '\n\n3\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n' | bootstrap_plugin.py create --template=ftpsend $plugin

# Edit config file
cd /home/mfdata/$plugin
layerapi $plugin
sed -i "s/switch_logical_condition = False/switch_logical_condition = $cond/g" config.ini
sed -i "s/arg_machine = /arg_machine = localhost/g" config.ini
sed -i "s/arg_user = /arg_user = mfdata_ftp/g" config.ini
sed -i "s/arg_passwd = /arg_passwd = mfdata_ftp/g" config.ini

# Release and install plugin
make release
# Find the plugin file's name
plugin_mov_file=$(find -L . -name "$plugin*.plugin")
plugins.install $plugin_mov_file
cd /home/mfdata/

# Create the input directory
mkdir -p /home/mfdata/var/in/incoming
