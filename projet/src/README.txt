# Commande pour construire les ensembles de train/test à partir du KNBC
python knbc_to_xml.py knbc-train.xml knbc-test.xml knbc-reference.xml

# Commande pour segmenter le fichier de test avec mon implémentation de hmm
python hmm_segmenter.py knbc-train.xml knbc-test.xml knbc-hmm.xml

# Commande pour évaluer la performance d'un système
python evaluation.py knbc-hmm.xml knbc-reference.xml

# Scores obtenus avec le système HMM
Avg Precision 0.904005681695
Avg Recall 0.881382517888
Avg f-measure 0.892550767507