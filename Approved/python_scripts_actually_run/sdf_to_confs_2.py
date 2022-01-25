import openbabel
import sys, os, shutil, glob 
from molSimplify.Classes.mol3D import *
from molSimplify.Scripts.geometry import *
from string import Template

## keep eveything neat with a prefix

folder_prefix = '/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use'

## create folders if they don't exist
dirs  = ['records/seed_geo','records/conformer_records',
         'records/raw_smiles','initial_geos/','optimized_geos/','starting_geos/',
         'MOPAC_infiles','MOPAC_outfiles','scr']

dirs = [ "/".join([folder_prefix,i]) for i in dirs ]         
for d in dirs:
    if not os.path.isdir(d):
        os.makedirs(d)

infiles = glob.glob('/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/*.sdf')

for i in infiles:
    ##name  
    this_name = os.path.basename(i)
    name = os.path.splitext(this_name)[0] 
    print('now running')
    print(name)
    # this is where we have debugged to 
    #create objects
    obConversion = openbabel.OBConversion()
    obConversion.SetInFormat("sdf")
    mol = openbabel.OBMol()
    obConversion.ReadFile(mol, "/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/" + this_name)
    mol.AddHydrogens()
    this_charge = mol.GetTotalCharge()
    print('charge for  ' + name + ' is ' +  str(this_charge))

            ## create output converter
    outConversion = openbabel.OBConversion()
    outConversion.SetInFormat('MOL')
    
    # save file before opt
    s = outConversion.WriteFile(mol, folder_prefix + '/records/seed_geo/'+this_name+'-before-opt.mol')
    
    ## create ff
    ff = openbabel.OBForceField.FindForceField("mmff94")
    ff.Setup(mol)
    
    ## run ff
    ff.ConjugateGradients(500)
    ff.GetCoordinates(mol)
    
    ## save file after opt
    s = outConversion.WriteFile(mol,folder_prefix + '/records/seed_geo/'+this_name+'-after-opt.mol')
    
    ## perform openbabel conformer search
    cs = openbabel.OBConformerSearch()
    cs.Setup(mol,100,5,5,25) 
    cs.GetConformers(mol)
    
    ## remove old record to prevent confusion:
    if os.path.isfile(folder_prefix +'/records/conformer_records/'+this_name+'.txt'):
        print('removing ' +folder_prefix +'/records/conformer_records/'+this_name+'.txt')
        os.remove(folder_prefix +'/records/conformer_records/'+this_name+'.txt')
                  

    ## save a record of all conformers 
    conf_energies = []
    conf_list = []
    min_energy = 1e6
    min_ind = 0
    outConversion = openbabel.OBConversion()
    outConversion.SetOutFormat('mol')
    outConversion.SetInFormat('MOL')
    
    ## loop over 100 conformers
    for i in range(0,100):
        mol.SetConformer(i+1)
        ff.Setup(mol)
        ff.ConjugateGradients(500)
        ff.GetCoordinates(mol)
        this_energy = ff.Energy()   
        with open(folder_prefix +'/records/conformer_records/'+this_name+'.txt','a+') as f:
            f.write('conformer ' + str(i) + ' energy = ' + str(this_energy)+'\n')
        if this_energy < min_energy:
            min_energy = this_energy
            min_ind = i

        if this_energy not in conf_energies:
            conf_energies.append(this_energy)
            conf_list.append(i+1)
   
    ## change to min energy conf
    mol.SetConformer(min_ind)
    
    ## start a list of geos to simulate
    geos_to_simulate  =[]
    
    ## create a formatter to create MOPAC files
    mopacConversion = openbabel.OBConversion()
    mopacConversion.SetOutFormat('mopcrt') # mopac cartessian format
    mopacConversion.SetInFormat('mol') # will read in mol - > mopcrt
    
    ## save a geo for the minimum energy conformer
    conf_name =  name + '-min-energy-conf'
    s = outConversion.WriteFile(mol,folder_prefix +'/records/conformer_records/'+conf_name +'.mol')
    
    ## transfer the minimum energy conformer to molsimplify class for rmsd conversion
    min_en_mol = mol3D()
    min_en_mol.OBMol = mol
    min_en_mol.convert2mol3D()
    min_en_mol.charge = this_charge
    
    ## here add the minimum to simulate, always
    with open(folder_prefix + '/records/conformer_records/'+this_name+'.txt','a+') as f:
        f.write('saving the minimum energy geo: ' +  conf_name + '  \n')
    geos_to_simulate.append(conf_name)   
    mopacMol = openbabel.OBMol()
    mopacConversion.ReadFile(mopacMol,folder_prefix + '/records/conformer_records/'+conf_name +'.mol')
    mopacConversion.WriteFile(mopacMol,folder_prefix + '/initial_geos/'+conf_name +'.mopcrt')

    ## save all confomers within tolerance 
    e_tolerance = 40 # here is where tolerance is set
    rmsd_tolerance = 2
    print('found a total of ' + str(len(conf_list)) + ' conformers ') 

    for i,c in enumerate(conf_list):
        
        if conf_energies[i] - min_energy < e_tolerance:
            with open(folder_prefix + '/records/conformer_records/'+name+'.txt','a+') as f:
                f.write('low energy conformer found at confromer ' +str(c)+' with energy gap ' + str(conf_energies[i] - min_energy)+' \n')
            mol.SetConformer(c)  
            conf_name =  name + '-conf-'+ str(i+1)
            s = outConversion.WriteFile(mol,folder_prefix + '/records/conformer_records/'+conf_name +'.mol')
    
    
            ## create a mol3D version to calculate RMSD to minimum 
            this_conf_mol = mol3D()            
            this_conf_mol.OBMol = mol
            this_conf_mol.convert2mol3D()
            this_conf_mol.charge = this_charge
            
            ## measure the RMSD
            align_mol,U,d0,d1= kabsch(min_en_mol,this_conf_mol)
            rmsd = align_mol.rmsd(this_conf_mol)

            if rmsd > rmsd_tolerance:
                print('high RMSD, low energy conformer found at confromer ' +str(c)+ ' with rmsd ' + str(round(rmsd,2)) + ' and energy gap ' + str(round(conf_energies[i] - min_energy,2)))
                with open(folder_prefix + '/records/conformer_records/'+this_name+'.txt','a+') as f:
                    f.write('high RMSD conformer found at confromer ' +str(c)+ ' with rmsd ' + str(rmsd)+ '\n')
                    
                
                geos_to_simulate.append(conf_name)   
                mopacMol = openbabel.OBMol()
                mopacConversion.ReadFile(mopacMol,folder_prefix + '/records/conformer_records/'+conf_name +'.mol')
                mopacConversion.WriteFile(mopacMol,folder_prefix + '/initial_geos/'+conf_name +'.mopcrt')
    os.rename('/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/'+name+'.sdf', '/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/starting_geos/'+name+'.sdf')
                
    print('found a total of ' + str(len(geos_to_simulate)) + ' conformers to simulate for ' + name )

    ## now, write MOPAC input files for these cases       
    for conf_name in geos_to_simulate:
        print('writing and input for ' + conf_name)
        
        ## write MOPAC input file, maybe remove the .in later:
        input_file_name = folder_prefix +'/MOPAC_infiles/'+ conf_name
        geo_file_name = '/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/BLOOPERS/input_geos_to_use/initial_geos/'+ conf_name + '.mopcrt'

        ## build sub dict
        d  = {'charge':str(this_charge),
                'name':conf_name,
                'geo':geo_file_name}

        # open the template
        f = open('MOPAC_template')
        f.seek(0)
        s = Template(f.read())
        ## open the new file:
        with open(input_file_name,'w') as fnew:
            fnew.write(s.safe_substitute(d))
        # close old file
        f.close()    
        
