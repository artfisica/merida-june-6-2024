import os
import sys
import ROOT
from ROOT import TMath
import time

# Ensure a ROOT file URL argument is provided
if len(sys.argv) < 2:
    raise ValueError("No ROOT file provided. Please pass the file URL as an argument.")

root_file_url = sys.argv[1]
start = time.time()

# Open the ROOT file from the provided URL
f = ROOT.TFile.Open(root_file_url)
canvas = ROOT.TCanvas("Canvas", "cz", 800, 600)

tree = f.Get("mini")
tree.GetEntries()

# Invariant mass histogram definition
hist = ROOT.TH1F("h_M_Hyy", "Diphoton invariant-mass ; Invariant Mass m_{yy} [GeV] ; events", 30, 105, 160)

Photon_1 = ROOT.TLorentzVector()
Photon_2 = ROOT.TLorentzVector()
n = 0

for event in tree:
    n += 1
    # Print progress for every 10,000 events
    if n % 10000 == 0:
        print(n)
    
    # Trigger condition
    if tree.trigP:
        goodphoton_index = [0] * 5
        goodphoton_n = 0
        photon_index = 0
        
        # Loop over photons in the event
        for j in range(tree.photon_n):
            if tree.photon_isTightID[j] and tree.photon_pt[j] > 22000 and \
               (TMath.Abs(tree.photon_eta[j]) < 2.37) and \
               (TMath.Abs(tree.photon_eta[j]) < 1.37 or TMath.Abs(tree.photon_eta[j]) > 1.52):
                
                goodphoton_n += 1
                goodphoton_index[photon_index] = j
                photon_index += 1

        # Process only if there are exactly two good photons
        if goodphoton_n == 2:
            goodphoton1_index = goodphoton_index[0]
            goodphoton2_index = goodphoton_index[1]

            # Isolation conditions
            if (tree.photon_ptcone30[goodphoton1_index] / tree.photon_pt[goodphoton1_index] < 0.065) and \
               (tree.photon_etcone20[goodphoton1_index] / tree.photon_pt[goodphoton1_index] < 0.065) and \
               (tree.photon_ptcone30[goodphoton2_index] / tree.photon_pt[goodphoton2_index] < 0.065) and \
               (tree.photon_etcone20[goodphoton2_index] / tree.photon_pt[goodphoton2_index] < 0.065):

                Photon_1.SetPtEtaPhiE(tree.photon_pt[goodphoton1_index] / 1000., tree.photon_eta[goodphoton1_index],
                                      tree.photon_phi[goodphoton1_index], tree.photon_E[goodphoton1_index] / 1000.)
                Photon_2.SetPtEtaPhiE(tree.photon_pt[goodphoton2_index] / 1000., tree.photon_eta[goodphoton2_index],
                                      tree.photon_phi[goodphoton2_index], tree.photon_E[goodphoton2_index] / 1000.)

                Photon_12 = Photon_1 + Photon_2
                hist.Fill(Photon_12.M())

# Draw and save the histogram
os.makedirs('plots', exist_ok=True)
output_filename = f"plots/histogram_{os.path.basename(root_file_url).replace('.root', '.png')}"
hist.Draw("E")
canvas.SetLogy()
canvas.SaveAs(output_filename)

end = time.time()
duration = end - start
print("Finished in {} min {} s".format(int(duration // 60), int(duration % 60)))
