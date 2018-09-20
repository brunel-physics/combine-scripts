#!/bin/sh

rm -f higgsCombine* impacts.json impacts.pdf datacard*.root datacard_syst_only.txt

# Create workspaces
text2workspace.py datacard_ee.txt
text2workspace.py datacard_mumu.txt

# Combine datacards
combineCards.py MVA_ee=datacard_ee.txt MVA_mumu=datacard_mumu.txt > datacard.txt
awk '!/autoMCStats/' datacard.txt > datacard_syst_only.txt
text2workspace.py datacard.txt
text2workspace.py datacard_syst_only.txt

printf "\n"
printf "\e[1m!===IMPACTS===!\e[0m\n"
combineTool.py -M Impacts -d datacard_syst_only.root -m 125 --rMin -5 --expectSignal=1.0 --doInitialFit --robustFit=1 --setRobustFitAlgo=Minuit2 --setRobustFitStrategy=1 
rename '123456.' '' higgsCombine_initialFit_Test*
combineTool.py -M Impacts -d datacard_syst_only.root -m 125 --rMin -5 --expectSignal=1.0 --doFits --parallel $(nproc) --robustFit=1 --setRobustFitAlgo=Minuit2 --setRobustFitStrategy=1 
rename '123456.' '' higgsCombine_paramFit_Test*
combineTool.py -M Impacts -d datacard_syst_only.root -m 125 --rMin -5 --expectSignal=1.0 --robustFit=1 --setRobustFitAlgo=Minuit2 --setRobustFitStrategy=1 -o impacts.json
plotImpacts.py -i impacts.json -o impacts

printf "\n"
printf "\e[1m!===EXPECTED SIGNIFICANCES===!\e[0m\n"
printf "\e[1m!=== ee EXPECTED SIGNIFICANCE===!\e[0m\n"
combine -M Significance --cminDefaultMinimizerType=Minuit2 --expectSignal=1.0 -s -1 datacard_ee.root

printf "\n\n\e[1m!=== μμ EXPECTED SIGNIFICANCE===!\e[0m\n"
combine -M Significance --cminDefaultMinimizerType=Minuit2 --expectSignal=1.0 -s -1 datacard_mumu.root

printf "\n\n\e[1m!=== COMBINED EXPECTED SIGNIFICANCE===!\e[0m\n"
combine -M Significance --cminDefaultMinimizerType=Minuit2 --expectSignal=1.0 -s -1 datacard.root

printf "\n"
printf "\e[1m!===SIGNAL STRENGTHS===!\e[0m\n"
printf "\e[1m!=== ee EXPECTED SIGNAL STRENGTH===!\e[0m\n"
combine -M FitDiagnostics --robustFit=1 --setRobustFitAlgo=Minuit2 --setRobustFitStrategy=1 --expectSignal=1.0 -s -1 --rMin -5 datacard_ee.root

printf "\n\n\e[1m!=== μμ EXPECTED SIGNAL STRENGTH===!\e[0m\n"
combine -M FitDiagnostics --robustFit=1 --setRobustFitAlgo=Minuit2 --setRobustFitStrategy=1 --expectSignal=1.0 -s -1 --rMin -5 datacard_mumu.root

printf "\n\n\e[1m!=== COMBINED EXPECTED SIGNAL STRENGTH===!\e[0m\n"
combine -M FitDiagnostics --robustFit=1 --setRobustFitAlgo=Minut2 --setRobustFitStrategy=1 --expectSignal=1.0 -s -1 --rMin -5 --saveShapes --saveWithUncertainties datacard.root
