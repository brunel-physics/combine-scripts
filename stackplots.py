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

    # Sort by normalisation
    bkg_histos = sorted(bkg_histos, key=lambda h: h.GetSumOfWeights())
    # ...put signals first
    histos = sig_histos + bkg_histos

    stack = ROOT.THStack("hs", "")
    for hists in histos:
        hists.SetFillColor(background_colours[hists.GetName()])
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
    "tZq": 2,
    "DYToLL_M10to50": 4,
    "DYToLL_M10to50_aMC@NLO": 4,
    "DYToLL_M50": 7,
    "DYToLL_M50_aMC@NLO": 7,
    "TbartChan": 30,
    "TbartW": 31,
    "THQ": 49,
    "TsChan": 32,
    "TtChan": 33,
    "ttH": 28,
    "TT": 3,
    "TtW": 40,
    "TTW": 41,
    "TTZ": 42,
    "TWZ": 43,
    "Wjets": 44,
    "WW": 18,
    "WWW": 17,
    "WWZ": 16,
    "WZ": 15,
    "WZZ": 14,
    "ZZ": 13,
    "ZZZ": 12,
    "FakeEG": 1,
    "FakeMu": 1}

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

        make_plot(match, sig_histos, bkg_histos)
