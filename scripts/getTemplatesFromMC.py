#!/usr/bin/env python
import ROOT
from optparse import OptionParser

def findBins(array, var):
    size = len(array)
    bin = "dump";
    for i in xrange(size-1):
        low = array[i]
        hi  = array[i+1]
        if (low <= var and hi > var):
            bin = str(low)+"To"+str(hi)
  
    return bin;

def main(options):
    
    var1s  = []
    for v in options.var1Bins.split(","):
        var1s.append(float(v))
    var2s = []
    for v in options.var2Bins.split(","):
        var2s.append(float(v))

    inFile = ROOT.TFile(options.input)
    inFile.cd(options.directory)
    fDir = inFile.Get(options.directory)
    fChain = fDir.Get("fitter_tree")

    histos = dict()

    def fixForPDFusage(hist) :
        # Remove any negative-weighted bins, and
        # apply a small value uniformly to gurantee no zero bins
        for b in range(hist.GetNbinsX()+1) :
            if ( hist.GetBinContent(b) <= 0. ) :
                hist.SetBinContent(b, 0.0001)

    for binVar1 in xrange(len(var1s)-1):
        for binVar2 in xrange(len(var2s)-1):
            histNameSt = "hMass_%s_bin%d__%s_bin%d" % (options.var1Name, binVar1, options.var2Name, binVar2)
            hp = histNameSt+"_Pass"
            hf = histNameSt+"_Fail"
            histos[hp] = ROOT.TH1D(hp, hp, 120, 60, 120)
            histos[hf] = ROOT.TH1D(hf, hf, 120, 60, 120)
            
            binning = "mcTrue == 1 && pair_mass60to120 && "+options.var1Name +">"+str(var1s[binVar1])+" && "+options.var1Name +"<"+str(var1s[binVar1+1])+" && "+options.var2Name +">"+str(var2s[binVar2])+" && "+options.var2Name +"<"+str(var2s[binVar2+1])
            if options.conditions :
                for condition in options.conditions.split(',') :
                    binning += " && %s==1" % condition
            cuts = "(" + binning + " && "+options.idprobe+"==1"+")*"+options.weightVarName
            fChain.Draw("mass>>"+histos[hp].GetName(), cuts, "goff")
            cuts = "(" + binning + " && "+options.idprobe+"==0"+")*"+options.weightVarName
            fChain.Draw("mass>>"+histos[hf].GetName(), cuts, "goff")

            fixForPDFusage(histos[hp])
            fixForPDFusage(histos[hf])
            #hpassInt = histos[hp].Integral()
            #hfailInt = histos[hf].Integral()
            #print hpassInt, hfailInt, hpassInt/(hpassInt+hfailInt)
    
    outFile = ROOT.TFile(options.output, "RECREATE")
    for k in histos:
        histos[k].Write()
    outFile.Close()


if __name__ == "__main__":  
    parser = OptionParser()
    parser.add_option("-i", "--input", default="../TnPTree_mc.root", help="Input filename")
    parser.add_option("-o", "--output", default="mc_templates.root", help="Output filename")
    parser.add_option("-d", "--directory", default="GsfElectronToRECO", help="Directory with fitter_tree")
    parser.add_option("", "--idprobe", default="passingMedium", help="String identifying ID WP to measure")
    parser.add_option("", "--conditions", default="", help="String identifying conditions on Tag and Probe")
    parser.add_option("", "--var1Bins", default="20,30,40,50,200", help="Binning to use in var1")
    parser.add_option("", "--var2Bins", default="0.0,1.0,1.4442,1.566,2.0,2.5", help="Binning to use in var2")
    parser.add_option("", "--var1Name", default="probe_sc_eta", help="Variable1 branch name")
    parser.add_option("", "--var2Name", default="probe_sc_et", help="Variable2 branch name")
    parser.add_option("", "--weightVarName", default="totWeight", help="Weight variable branch name")

    (options, arg) = parser.parse_args()
     
    main(options)
