#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

import re
import sys

import CombineHarvester.CombineTools.plotting as plot
import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.AddDirectory(False)
ROOT.gStyle.SetPalette(ROOT.kOcean)


def createAxisHists(n, src, xmin=0, xmax=499):
    result = []
    for i in range(0, n):
        res = src.Clone()
        res.Reset()
        res.SetTitle("")
        res.SetName("axis{}".format(i))
        res.SetAxisRange(xmin, xmax)
        res.SetStats(0)
        result.append(res)
    return result


def make_plot(match, sig_histos, bkg_histos, padding=0, log_y=False,
              lumi=35.9, ratio_range=(0.5, 1.5), x_title="MVA discriminant",
              y_title="Events", outdir = "out"):

    # Sort by plot order
    histos = sorted(bkg_histos + sig_histos, key=lambda h: plot_order[h.GetName()])

    stack = ROOT.THStack("hs", "")
    for hists in histos:
        hists.SetFillColor(ROOT.TColor.GetColor(background_colours[hists.GetName()]))
        hists.SetMarkerSize(0)
        hists.SetLineWidth(0)
        stack.Add(hists)

    # Set up pads
    c2 = ROOT.TCanvas()
    c2.cd()
    pads = plot.TwoPadSplit(0.29, 0.01, 0.01)
    pads[0].cd()

    if (log_y):
        pads[0].SetLogy(1)

    axish = createAxisHists(2, tothist,
                            tothist.GetXaxis().GetXmin(),
                            tothist.GetXaxis().GetXmax() - 0.01)
    axish[1].GetXaxis().SetTitle(x_title)
    axish[1].GetYaxis().SetNdivisions(4)
    axish[1].GetYaxis().SetTitle("Obs/Exp")
    axish[1].GetYaxis().SetTitleSize(0.04)
    axish[1].GetYaxis().SetLabelSize(0.04)
    axish[1].GetYaxis().SetTitleOffset(1.3)
    axish[0].GetYaxis().SetTitleSize(0.04)
    axish[0].GetYaxis().SetLabelSize(0.04)
    axish[0].GetYaxis().SetTitleOffset(1.3)

    axish[0].GetXaxis().SetTitleSize(0)
    axish[0].GetXaxis().SetLabelSize(0)
    axish[0].GetYaxis().SetTitle(y_title)
    axish[0].GetXaxis().SetTitle(x_title)
    axish[0].SetMaximum(padding * tothist.GetMaximum())
    axish[0].SetMaximum(tothist.GetMaximum())

    if (log_y):
        axish[0].SetMinimum(0.0009)
    else:
        axish[0].SetMinimum(0)

    axish[0].Draw()

    # Draw uncertainty band
    tothist.SetFillColor(plot.CreateTransparentColor(921, 1))
    tothist.SetMarkerStyle(0)
    tothist.SetLineColor(0)
    tothist.SetMarkerSize(0)
    tothist.SetFillStyle(3144)

    stack.Draw("histsame")
    tothist.Draw("e2same")
    datahist.SetLineColor(ROOT.kBlack)
    datahist.DrawCopy("psame")
    axish[0].Draw("axissame")

    # Setup legend
    legend = plot.PositionedLegend(0.20, 0.42, 3, 0.01)
    legend.SetTextFont(42)
    legend.SetTextSize(0.015)
    legend.SetFillColor(0)

    # Drawn on legend in reverse order looks better
    histos.reverse()
    for h in histos:
        legend.AddEntry(h, h.GetName(), "f")

    legend.AddEntry(tothist, "Syst.", "f")
    legend.AddEntry(datahist, "Observation", "le")
    legend.Draw("same")

    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(ROOT.kBlack)
    latex2.SetTextSize(0.028)
    latex2.DrawLatex(0.145, 0.955, match.group(1))

    # CMS and lumi labels
    plot.FixTopRange(pads[0], plot.GetPadYMax(pads[0]), padding
                     if padding > 0 else 0.30)
    plot.FixTopRange(pads[0], plot.GetPadYMax(pads[0]), 0.30)
    # plot.DrawCMSLogo(pads[0], 'CMS', 'Internal', 11, 0.045, 0.05, 1.0, '', 1.0)
    plot.DrawTitle(pads[0], str(lumi) +
                   r"fb^\{-1} (#font[52]{s} = #sqrt{13} TeV)", 3)

    # Add ratio plot if required
    div_hist = tothist.Clone()
    for i in xrange(0, div_hist.GetNbinsX() + 2):
        div_hist.SetBinError(i, 0)

    ratio_hist = tothist.Clone()
    ratio_hist.Divide(div_hist)
    datahist.Divide(div_hist)

    pads[1].cd()
    pads[1].SetGrid(0, 1)
    axish[1].Draw("axis")
    axish[1].SetMinimum(ratio_range[0])
    axish[1].SetMaximum(ratio_range[1])
    ratio_hist.SetMarkerSize(0)
    ratio_hist.Draw("e2same")
    datahist.DrawCopy("e0same")
    pads[1].RedrawAxis("G")

    pads[0].cd()
    pads[0].RedrawAxis()

    outname = "postfit"
    if (log_y):
        outname += "_logy"

    if outdir[-1] != '/':
        outdir += '/'

    c2.SaveAs("{}{}.root".format(outdir, match.group(0)))
    c2.SaveAs("{}{}.pdf".format(outdir, match.group(0)))
    c2.SaveAs("{}{}.tex".format(outdir, match.group(0)))


# Signals
signals = ["tZq"]

# Colours
background_colours = {
    "TZQ": "#999999",
    "DYToLL_M10to50": "#006699",
    "DYToLL_M10to50_aMC@NLO": "#006699",
    "DYToLL_M50": "#006699",
    "DYToLL_M50_aMC@NLO": "#006699",
    "DYJetsLLPt0To50": "#006699",
    "DYJetsLLPt50To100": "#006699",
    "DYJetsLLPt100To250": "#006699",
    "DYJetsLLPt250To400": "#006699",
    "DYJetsLLPt400To650": "#006699",
    "DYJetsLLPt650ToInf": "#006699",
    "TbartChan": "#ff99cc",
    "TbarW": "#ff99cc",
    "THQ": "#ff99cc",
    "TsChan": "#ff99cc",
    "TtChan": "#ff99cc",
    "TTHbb": "#ff99cc",
    "TTHnonbb": "#ff99cc",
    "TT": "#cc0000",
    "TW": "#ff99cc",
    "TTW2q": "#339933",
    "TTWlnu": "#339933",
    "TTZ2q": "#339933",
    "TTZ2l2nu": "#339933",
    "TWZ": "#ff99cc",
    "Wjets": "#ffff33",
    "WW1l1nu21": "#ff9933",
    "WW2l2nu": "#ff9933",
    "WWW": "#993399",
    "WWZ": "#993399",
    "WZ3l1nu": "#ff9933",
    "WZ2l2q": "#ff9933",
    "WZ1l1nu2q": "#ff9933",
    "WZZ": "#993399",
    "ZZZ": "#ff9933",
    "ZZ4l": "#ff9933",
    "ZZ2l2nu": "#ff9933",
    "ZZ2l2q": "#ff9933",
    "FakeEG": "#003300",
    "FakeMu": "#003300",
}

plot_order = {
    "DYToLL_M10to50": 8,
    "DYToLL_M10to50_aMC@NLO": 8,
    "DYToLL_M50": 8,
    "DYToLL_M50_aMC@NLO": 8,
    "DYJetsLLPt0To50": 8,
    "DYJetsLLPt50To100": 8,
    "DYJetsLLPt100To250": 8,
    "DYJetsLLPt250To400": 8,
    "DYJetsLLPt400To650": 8,
    "DYJetsLLPt650ToInf": 8,
    "TT": 7,
    "WW1l1nu21": 6,
    "WW2l2nu": 6,
    "WZ3l1nu": 6,
    "WZ2l2q": 6,
    "WZ1l1nu2q": 6,
    "ZZ4l": 6,
    "ZZ2l2nu": 6,
    "ZZ2l2q": 6,
    "FakeEG": 5,
    "FakeMu": 5,
    "TbartChan": 4,
    "TbarW": 4,
    "THQ": 4,
    "TsChan": 4,
    "TtChan": 4,
    "TTHbb": 4,
    "TTHnonbb": 4,
    "TW": 4,
    "TWZ": 4,
    "Wjets": 3,
    "TTWlnu": 2,
    "TTW2q": 2,
    "TTZ2q": 2,
    "TTZ2l2nu": 2,
    "WWW": 1,
    "WWZ": 1,
    "WZZ": 1,
    "ZZZ": 1,
    "TZQ": 0,
}


fi = ROOT.TFile(sys.argv[1], "read")
keylist = fi.GetListOfKeys()

for key in keylist:
    obj = key.ReadObj()
    match = re.match("^(.+)_(?:post|pre)fit$", obj.GetName())

    bkg_histos = []
    sig_histos = []

    if match:
        variable = match.group(1)
        print(variable)
        kl = obj.GetListOfKeys()

        for k in kl:
            h = k.ReadObj()
            name = h.GetName()
            if name == "TotalBkg":
                # bkghist = h
                pass
            elif name == "TotalSig":
                # sighist = h
                pass
            elif name == "TotalProcs":
                tothist = h
            elif name == "data_obs":
                datahist = h
            elif name in signals:
                sig_histos.append(h)
            elif name not in signals:
                bkg_histos.append(h)

        make_plot(match, sig_histos, bkg_histos, outdir=sys.argv[2])
