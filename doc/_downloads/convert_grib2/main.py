#!/usr/bin/env python3
import os
import re
import subprocess

from acquisition.step import AcquisitionStep
from mfutil import mkdir_p_or_die
from netCDF4 import Dataset
from xattrfile import XattrFile


class Convert_grib2MainStep(AcquisitionStep):
    plugin_name = "convert_grib2"
    step_name = "main"

    def __init__(self):
        self.grib_to_netcdf_options_default = "-k 3 -d 0 -D NC_FLOAT"
        self.grib_to_netcdf_options = os.environ.get("MFDATA_PLUGIN_CONVERT_GRIB2_GRIB_TO_NETCDF_OPTIONS",
                                                     self.grib_to_netcdf_options_default)

    def init(self):
        super().init()
        if self.args.netcdf_dest_dir is None:
            raise Exception('you have to set a netcdf-dest-dir')
        mkdir_p_or_die(self.args.netcdf_dest_dir)

    def add_extra_arguments(self, parser):
        # Call the parent add_extra_arguments
        super().add_extra_arguments(parser)

        parser.add_argument('--netcdf-dest-dir', action='store',
                            default=None,
                            help='Netcdf destination directory')
        parser.add_argument('--keep-tags', action='store',
                            type=bool, default=True,
                            help='keep tags/attributes into another file ?')
        parser.add_argument('--keep-tags-suffix', action='store',
                            default=".tags",
                            help='if keep-tags=True, suffix to add to the '
                                 'filename to keep tags')

    def grib_to_netcdf_command(self, grib_file_path, netcdf_file_path):
        """
        Convert GRIB file to Netcdf File
        :param grib_file_path: GRIB file path to convert
        :param netcdf_file_path: output NetCDF file path to convert
        :raise: Exception if something wrong happens
        """

        # Build the 'grib_to_netcdf' command
        command_grib_to_netcdf = list()
        command_grib_to_netcdf.append("grib_to_netcdf")
        command_grib_to_netcdf.append(grib_file_path)
        command_grib_to_netcdf.extend(self.grib_to_netcdf_options.split(' '))
        command_grib_to_netcdf.append("-o")
        command_grib_to_netcdf.append(netcdf_file_path)

        self.debug(command_grib_to_netcdf)

        try:

            # Run the the 'grib_to_netcdf' command
            result_grib_to_netcdf = subprocess.check_call(command_grib_to_netcdf)

            if result_grib_to_netcdf != 0:
                msg = 'Unable to execute command {}. Result is: {}.'.format(command_grib_to_netcdf,
                                                                            result_grib_to_netcdf)
                raise Exception(msg)

        except subprocess.CalledProcessError as e:
            msg = 'Unable to execute command {}. Reason: {}'.format(command_grib_to_netcdf, str(e))
            raise Exception(msg, e)

    def process(self, xaf):
        """
        This function:
        - Convert a GRIB file into a NetCDF file.
        - Read some data of the NetCDF file

        :param xaf: the input GRIB data file as an XattrFile object
        :return: True, if the process is successful, False, if the process failed
        """

        # xaf.filepath is the internal file name created by the switch plugin into a temporary directory
        self.info("process for file %s" % xaf.filepath)

        try:
            # In order to get the original GRIB file name, call AcquisitionStep.get_original_basename
            original_grib_filename = str(AcquisitionStep.get_original_basename(self, xaf))

            # Build the output NetCDF file name from the input file name,
            netcdf_filename = re.sub(r'(\.grb|\.grib2|\.grib)$', '', str(original_grib_filename)) + ".nc"
            netcdf_filepath = os.path.normpath(os.path.join(self.args.netcdf_dest_dir, netcdf_filename))

            # Convert Grib to Netcdf
            self.grib_to_netcdf_command(xaf.filepath, netcdf_filepath)

            # We tags/attributes in a specific file
            if self.args.keep_tags:
                tags_filepath = netcdf_filepath + self.args.keep_tags_suffix
                xaf.write_tags_in_a_file(tags_filepath)

            XattrFile(netcdf_filepath).clear_tags()

            # Read the output NetCDF
            # Log the dimensions name and variable names
            netcdf_dataset = Dataset(netcdf_filepath, "r")

            self.info("Dimensions of the Netcdf dataset {}:".format(netcdf_filepath))
            for dim_name in netcdf_dataset.dimensions:
                self.info(dim_name)

            self.info("Variables of the Netcdf dataset {}:".format(netcdf_filepath))
            for var_name in netcdf_dataset.variables:
                self.info(var_name)


        except Exception as e:
            self.exception(str(e))
            return False

        return True

    def after(self, status):
        """
        Method called after the process execution
        :param status: status of the process execution
        """
        self.info("GRIB to NetCDF conversion ended with status {}".format(status))


if __name__ == "__main__":
    x = Convert_grib2MainStep()
    x.run()
