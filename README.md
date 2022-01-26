# Optimized-Drug-Screening-Libraries
New repo to store complete screening libraries and project files

Here, I take in silico drug screening libraries and run conformer driving in MMFF, then feed the conformers into geometry optimization runs in MOPAC using the PM7 Hamiltonian and the COSMO water solvent model. I intend to include the optimized geometries, the annotated code I used to automate these processes, and documentation. This is intended as a computationally inexpensive method to roughly represent the conformations the molecules in the library adopt in an aqueous environment. 

Folder/file convention:
Within each folder of this repo, you'll find a chemical library. The files for each library include...

optimized_conformer_geos = *final, optimized* molecular structures for the conformers, extracted from the MOPAC outfiles, in .xyz format and after conversion to .sdf using Open Babel. *Note* Open Babel has known issues interpreting polyheterocyclic structures. If you encounter a structure with a valence error, the original/correct structure is in the MOPAC outfiles.

MOPAC_outfiles = .out, .arc and .cos files from MOPAC geometry optimization runs on conformers;

initial_conformer_geos = molecular structure files for conformers generated for each molecule in MMFF using OpenBabel's GetConformers functionality;

MOPAC_infiles = input files MOPAC refers to for geometry optimization calculations;

starting_compound_geos = one starting structure for each molecule, the structures fed into the conformer driviing step my workflow;

xxx.sdf = a single file containing the information curated (i.e. from Drug Bank) about each molecule in the library, including the SMILES strings used to build a starting structure in Mathematica. 

*Note* The Drug Bank - Approved library is the large one (2370 molecules), so that folder contains additional writen materials (a Word document and a Mathematica notebook) explaining what I did.
