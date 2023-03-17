import subprocess
import os
import argparse
import logging

logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)

class DebPgk:
	def __init__(self, binary_info : tuple, 
	      			debian_pkg_dir : str = './deb_pkg', 
				    installPath : str = 'usr/local/bin',
				    architecture = 'x86-64',
				    pkgVersion : str = '0.1',
				    pgkRev : str = '1',
					manteinerName : str = 'HomeMicrotech', 
					packageDescription : str = 'My wonderful deb package\n') -> None:
		
		if len(binary_info) != 2:
			raise ValueError(f'The binary info is a 2-size tuple')
		logging.debug(f'Binary info tuple: {binary_info}')
		self._binary_info = binary_info
		self._binary_name = self._binary_info[0]
		self._final_deb_pgk_dir = debian_pkg_dir
		self._install_deb_path = installPath
		self._arch = architecture
		self._pgk_version = pkgVersion
		self._pgk_rev = pgkRev
		self._manteiner_name = manteinerName
		self._pkg_desc = packageDescription
		self._full_bin_path = self._binary_info[1]
		if not os.path.exists(self._full_bin_path):
			raise FileNotFoundError(f'File {self._full_bin_path} not found')

	def _build_deb_dict(self) -> dict:
		deb_pkg_info = dict()
		deb_pkg_info['pkg_name'] = self._binary_name
		deb_pkg_info['full_bin_path'] = self._full_bin_path
		deb_pkg_info['pkg_version'] = self._pgk_version
		deb_pkg_info['pkg_rev'] = self._pgk_rev
		deb_pkg_info['pkg_arch'] = self._arch
		deb_pkg_info['pkg_install_path'] = self._install_deb_path
		deb_pkg_info['pkg_mantainer'] =  self._manteiner_name
		deb_pkg_info['pkg_description'] = self._pkg_desc
		return deb_pkg_info

	def _build_ctrl_file(self, deb_dict : dict) -> str:
		control_file = str()
		if type(deb_dict) == dict:
			control_file = 'Package: ' + str(deb_dict['pkg_name']).replace('_', '') + '\n' + \
											'Version: ' + deb_dict['pkg_version'] + '\n' +  \
											'Architecture: ' + deb_dict['pkg_arch'] + '\n' +  \
											'Maintainer: ' + deb_dict['pkg_mantainer'] + '\n' + \
											'Description: ' + deb_dict['pkg_description'] + '\n'
		return control_file

	def build_pkg(self):
		if not os.path.isdir(self._final_deb_pgk_dir):
			subprocess.run(['mkdir', '-p', self._final_deb_pgk_dir])
		self._final_deb_pgk_dir = os.path.abspath(self._final_deb_pgk_dir)
		deb_dict = self._build_deb_dict()
		for key in deb_dict:
			logging.debug(f'Deb dict: key: {key} -> value: {deb_dict[key]}')
		package_dir = deb_dict['pkg_name'] + \
							'_' + deb_dict['pkg_version'] + \
							'-' + deb_dict['pkg_rev'] + '_' + deb_dict['pkg_arch']
		package_install_dir = package_dir + '/' + deb_dict['pkg_install_path']
		package_DEBIAN_dir = package_dir + '/DEBIAN'
		control_file = self._build_ctrl_file(deb_dict)
		logging.debug(f'Package install dir: {package_install_dir}')
		logging.debug(f'Package DEBIAN dir: {package_DEBIAN_dir}')
		subprocess.run(['mkdir', '-p', package_install_dir])
		subprocess.run(['mkdir', '-p', package_DEBIAN_dir])
		with open(package_DEBIAN_dir + '/control', 'w') as control_fd:
			control_fd.write(control_file)
		subprocess.run(['cp', deb_dict['full_bin_path'], package_install_dir])
		subprocess.run(['mv', package_dir, self._final_deb_pgk_dir])
		subprocess.run(['dpkg-deb', '--build', '--root-owner-group', self._final_deb_pgk_dir + '/' + package_dir])
		subprocess.run(['rm', '-rf', self._final_deb_pgk_dir + '/' + package_dir])
		logging.info(f'Removing directory: {self._final_deb_pgk_dir + "/" + package_dir}')

		
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--bin-dir', type=str, help='Directory with the binaries', required=True)
	parser.add_argument('-o', '--deb-dir', default= './deb_pkg', type=str, help='Directory for the output deb package', required=False)
	parser.add_argument('-i', '--install-dir', default= 'usr/local/bin', type=str, help='Directory for the application installation', required=False)
	parser.add_argument('-v', '--version-major', default= '0.1', type=str, help='Package version', required=False)
	parser.add_argument('-r', '--revision', default= '1', type=str, help='Package revision', required=False)
	parser.add_argument('-a', '--arch', default= 'x86-64', type=str, help='Sytem target architecture', required=False)
	parser.add_argument('-m', '--mantainer', default= 'Home Microtech', type=str, help='Package mantainer', required=False)
	parser.add_argument('-ds', '--description', default= 'Deb package very useful', type=str, help='Package description', required=False)


	args = parser.parse_args()

	bin_dir = args.bin_dir
	bin_dir = os.path.abspath(bin_dir)
	deb_out_dir = args.deb_dir
	install_path = args.install_dir
	version = args.version_major
	rev = args.revision
	arch = args.arch
	mantainer = args.mantainer
	desc = args.description

	logging.debug(f'Bin dir: {bin_dir}')
	if os.path.isdir(bin_dir):
		for bin_file in os.listdir(bin_dir):
			logging.debug(f'Bin file: {bin_file}')
			bin_info = (bin_file, bin_dir + '/' + bin_file)
			deb_pkg_builder = DebPgk(binary_info=bin_info, 
			    					debian_pkg_dir=deb_out_dir, 
									installPath=install_path, 
									pkgVersion=version,
									pgkRev=rev,
									architecture=arch,
									manteinerName=mantainer,
									packageDescription=desc)
			deb_pkg_builder.build_pkg()

if __name__ == '__main__':
        main()