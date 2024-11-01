#  Copyright  2021 Alexis Lopez Zubieta
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
import logging
import subprocess
import re

from appimagebuilder.utils import shell

CLI_REQUIRE = ["dpkg-query"]


class FilePackageResolver:
    """Resolve which deb packages provide a given file using `dpkg-query -S`"""

    def __init__(self):
        self.logger = logging.getLogger(str(self.__class__.__name__))
        self._cli_tools = shell.require_executables(CLI_REQUIRE)

    def resolve(self, files) -> {}:
        stdout_data = self._run_dpkg_query_s(files)
        results = self._parse_dpkg_query_s_output(stdout_data)

        return results

    def _run_dpkg_query_s(self, files):
        command = "{dpkg-query} -S {files}"
        command = command.format(**self._cli_tools, files=" ".join(files))
        self.logger.info(command)
        _proc = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        stdout_data = _proc.stdout.decode()
        return stdout_data

    def _extract_package_names(self, pkg_names):
        """
        Checks if pkg_names is in the form 'diversion by <package_names> to <destination>'
        and extracts the package names if it is.
        """
        # Define the regex to match the diversion format
        match = re.match(r"diversion by (.+?) (to|from)", pkg_names)
        if match:
            extracted_names = match.group(1).strip()
            logging.debug(f"Extracted package names from diversion: {extracted_names}")
            return extracted_names
        else:
            logging.debug(f"No diversion format found in: {pkg_names}")
            return pkg_names.strip()

    def _parse_dpkg_query_s_output(self, stdout_data):
        logging.debug("Starting to parse dpkg-query output.")
        
        # Initialize an empty dictionary to store results
        results = {}
        logging.debug("Initialized empty results dictionary.")
        
        # Process each line in the output
        for line in stdout_data.splitlines():
            logging.debug(f"Processing line: {line}")
            
            # Split the line into package names and file path
            line_parts = line.split(sep=": ", maxsplit=1)
            
            if len(line_parts) != 2:
                logging.warning(f"Line format unexpected, skipping: {line}")
                continue
            
            pkg_names = self._extract_package_names(line_parts[0])
            file_path = line_parts[1]

            logging.debug(f"Package names: {pkg_names}, File path: {file_path}")
            
            # Process each package name in case of multiple names
            for pkg_name in pkg_names.split(","):
                pkg_name = pkg_name.strip()
                logging.debug(f"Parsed package name: {pkg_name}")
                
                # Assign the package name to the file path in results
                results[file_path] = pkg_name
                logging.debug(f"Mapping file path '{file_path}' to package name '{pkg_name}'")
        
        logging.debug(f"Completed parsing. Final results: {results}")
        return results
