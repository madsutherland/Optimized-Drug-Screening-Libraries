#This will be a script for extracting SMILES

fileName = "/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/DB_APcomplex_JaninaDesalted.sdf"
f = open("/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/Approved_JaninaDesalted/allsmiles_DB_APcomplex_JaninaDesalted.txt", "w")

inputfile = open(fileName, 'r').readlines()

files = {}
storeContent = False
content = ""
for line in inputfile:
    if "Formula" in line.strip() and storeContent:
        content=content.rstrip()
        files [storeContent] = content
        storeContent = False
        print(content)
        f.write(content + "\n")
        content = ""
    elif "Smiles" in line:
        storeContent = line.replace(" ", "").strip()
    elif storeContent:
        if not content:
            content += line
        else:
            content += line
    else:
        pass # ignore other content

f.close

# print(files)
# for name, content in files.items():
#    print(name)
#    f = open("/Users/madmarchhare/ms-testing_DBlib/DrugBankNew/sdfs/investigational/" + name + ".sdf", "w")
#    f.write(name + "\n" + content + "M  END")
#    f.close



# g = open("allsmiles.txt", "w")
# g.write(content)
# g.close