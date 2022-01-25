import os, glob, subprocess, time, shutil

nits = 0
while nits < 6000:
        nits +=1 
        subbed_jobs =[]
        with open('/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/submitted_jobs_2.txt','r') as f:
                for lines in f.readlines():
                        subbed_jobs.append(lines.strip().strip('\n'))

        infiles = glob.glob('/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/MOPAC_infiles/*')
        p1 = subprocess.Popen('squeue -u msuther | wc -l',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        queue_length,er = p1.communicate()
        try:
#               queue_length=int(queue_length.split("gpus=")[1].split('/64')[0])
                #Deep question for Pushpita here: can I do a version of this queue check on my machine?
               queue_length=int(queue_length.strip()) -1

        except:
                queue_length = 0
	print('we think there are ' + str(queue_length) + ' jobs in queue ')
        
        qtol = 500

        infiles.sort()
        if queue_length < qtol:
                number_of_jobs = qtol-queue_length
                print('submitting '+str(number_of_jobs) + ' jobs')
                jc = 0

                for j in infiles:
                        if not j in subbed_jobs:
                                if jc < number_of_jobs:
                                        unq_jid = str(len(subbed_jobs))
					j_name = os.path.basename(j).strip('.in')
                                        print(j_name)
                                        shutil.move(j, '/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/MOPAC_outfiles/'+j_name)
                                        outputfile ='queue_records/job_'+j_name+'.o'
                                        cmdstr = 'mopac BLOOPERS/input_geos_to_use/MOPAC_outfiles/' + j_name
                               		print(cmdstr)
                                        subbed_jobs.append(j)
                                        jc+=1
                                        print('subbed JN : ' + str(jc))
                                        subprocess.call( cmdstr,shell=True)
                                          
        with open('submitted_jobs_2.txt','w') as f:
                for j in subbed_jobs:
                        f.write(j+'\n')
        print('sleeping...')
        time.sleep(600) 

