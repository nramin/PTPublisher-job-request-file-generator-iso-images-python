from JRQMaker import JRQMaker
import os

def main():
	iso_images_folder = 'C:/Users/user/Desktop/iso_images'
	job_requests_folder = 'C:/PTBurnJobs'

	create_job_requests = JRQMaker(iso_images_folder, job_requests_folder, True)
	create_job_requests.close_disc(True)
	create_job_requests.reject_if_not_blank(True)
	create_job_requests.create_disc_labels(True)
	#create_job_requests.set_copies(2)
	#create_job_requests.set_importance(4)
	#create_job_requests.set_burn_speed(8)

if __name__=="__main__":
	main()