import glob
import os
import datetime
import math

def file_len(iso_images_log):
    with open(iso_images_log) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def clean_path(file_path):
	path = file_path.split("\\")
	return path[-1]

def get_size(folder_path):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(folder_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size

class JRQMaker():

	def __init__(self, iso_images_folder, job_requests_folder, burn_folders=False):
		self.iso_images_folder = os.path.normpath(iso_images_folder)
		self.job_requests_folder = os.path.normpath(job_requests_folder)
		self.burn_folders = burn_folders
		self.iso_images_log = os.path.normpath(self.job_requests_folder + '/iso_images_log.txt')

		existing_iso_images = set([])
		self.new_iso_images = set([])

		first_time_checking = True

		try:
			with open(self.iso_images_log): pass
		except IOError:
			f = open(self.iso_images_log, 'w').close()

		while True:
			try:
				if file_len(self.iso_images_log) > 0:
					existing_iso_images = set(line.strip() for line in open(self.iso_images_log))
					first_time_checking = False
				break
			except UnboundLocalError:
				f = open(self.iso_images_log, 'w')
				for files in glob.glob(os.path.normpath(self.iso_images_folder + '/*.iso')):
					f.write(clean_path(files) + '\n')
					self.new_iso_images.add(clean_path(files))
					existing_iso_images.add(clean_path(files))
				if self.burn_folders:
					for folder in os.listdir(os.path.normpath(self.iso_images_folder)):
						if os.path.isdir(os.path.normpath(self.iso_images_folder + '/' + folder)):
							f.write(folder + '\n')
							self.new_iso_images.add(folder)
							existing_iso_images.add(folder)
				f.close()
				break

		if not first_time_checking:
			self.updated_existing_iso_images = set([])
			for files in glob.glob(os.path.normpath(self.iso_images_folder + '/*.iso')):
				self.updated_existing_iso_images.add(clean_path(files))
				if clean_path(files) not in existing_iso_images:
					self.new_iso_images.add(clean_path(files))
					existing_iso_images.add(clean_path(files))
			if self.burn_folders:
				for folder in os.listdir(os.path.normpath(self.iso_images_folder)):
					if os.path.isdir(os.path.normpath(self.iso_images_folder + '/' + folder)):
						self.updated_existing_iso_images.add(folder)
						if folder not in existing_iso_images:
							self.new_iso_images.add(folder)
							existing_iso_images.add(folder)
			self.updated_existing_iso_images = self.updated_existing_iso_images.intersection(existing_iso_images)

			f = open(self.iso_images_log, 'a')
			for files in self.updated_existing_iso_images:
				if files in self.new_iso_images:
					f.write(clean_path(files) + '\n')
			f.close()
		else:
			f = open(self.iso_images_log, 'w')
			for files in existing_iso_images:
				f.write(clean_path(files) + '\n')
			f.close()

		for files in self.new_iso_images:
			if os.path.isdir(os.path.normpath(self.iso_images_folder + '/' + files)):
				f = open(os.path.normpath(self.job_requests_folder + '/' + files + '.jrq'), 'w').close()
			else:
				f = open(os.path.normpath(self.job_requests_folder + '/' + os.path.splitext(files)[0] + '.jrq'), 'w').close()

		self._set_job_id()
		self._set_client_id()
		self._load_data()
		self._set_disc_type()
		self._set_volume_name()
		self._client_commands()

	def _file_folder_detect(self, image):
		if os.path.isdir(os.path.normpath(self.iso_images_folder + '/' + image)):
			return str(image)
		else:
			return os.path.splitext(image)[0]

	# if client wants to give all new iso images being burned the same job id
	def _set_job_id(self):
		for files in self.new_iso_images:
			f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
			f.write('JobID = ' + self._file_folder_detect(files) + '\n')
			f.close()

	# if client wants to give all new iso images being burned the same client id
	def _set_client_id(self):
		for files in self.new_iso_images:
			f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
			f.write('ClientID = ' + self._file_folder_detect(files) + '\n')
			f.close()

	# if client wants to give all new iso images being burned the same importance
	def set_importance(self, importance):
		if importance:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('Importance = ' + str(importance) + '\n')
				f.close()

	def _load_data(self):
		for files in self.new_iso_images:
			f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
			if os.path.isdir(os.path.normpath(self.iso_images_folder + '/' + files)):
				f.write('Data = ' + os.path.normpath(self.iso_images_folder + '/' + files) + '\n')
			else:
				f.write('ImageFile = ' + os.path.normpath(self.iso_images_folder + '/' + files) + '\n')
			f.close()

	def _set_disc_type(self):
		for files in self.new_iso_images:
			image_file_size = 0
			if os.path.isdir(os.path.normpath(self.iso_images_folder + '/' + files)):
				image_file_size = get_size(os.path.normpath(self.iso_images_folder + '/' + files))
			else:
				image_file_size = os.path.getsize(os.path.normpath(self.iso_images_folder + '/' + files))
			if image_file_size > 737280000:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('DiscType = DVDR' + '\n')
				f.close()

	def set_copies(self, copies):
		if copies:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('Copies = ' + str(copies) + '\n')
				f.close()

	def set_burn_speed(self, speed):
		if speed:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('BurnSpeed = ' + str(speed) + '\n')
				f.close()

	def is_verified(self, verify):
		if verify:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('VerifyDisc = YES' + '\n')
				f.close()

	def close_disc(self, closed):
		if closed:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('CloseDisc = YES' + '\n')
				f.close()

	def _set_volume_name(self):
		for files in self.new_iso_images:
			f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
			f.write('VolumeName = ' + self._file_folder_detect(files) + '\n')
			f.write('CDTextDiscTitle = ' + self._file_folder_detect(files) + '\n')
			f.close()

	def reject_if_not_blank(self, reject):
		if reject:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('RejectIfNotBlank = YES' + '\n')
				f.close()

	def create_disc_labels(self, label=True):
		if label:
			for files in self.new_iso_images:
				f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.jrq'), 'a')
				f.write('PrintLabel = '+ os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/disc_cover.std') + '\n')
				f.write('MergeField=' + self._file_folder_detect(files)[:259] + '\n')
				f.close()

	def _client_commands(self):
		for files in self.new_iso_images:
			f = open(os.path.normpath(self.job_requests_folder + '/' + self._file_folder_detect(files) + '.ptm'), 'w')
			f.write('Message= CHANGE_KIOSK_MODE' + '\n')
			f.write('Value=1' + '\n')
			f.write('ClientID=Administrator' + '\n')
			f.write('Message= IGNORE_INKLOW' + '\n')
			f.write('ClientID=Administrator' + '\n')
			f.close()