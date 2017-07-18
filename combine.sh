#!/bin/sh

printf "\e[1m!=== ee EXPECTED SIGNIFCANCE===!\e[0m\n"
combine -M ProfileLikelihood --signif --cminDefaultMinimizerType=Minuit2 -t -1 --expectSignal=1.0 -s -1 datacard-ee.txt 2> /dev/null

printf "\n\n\e[1m!=== μμ EXPECTED SIGNIFCANCE===!\e[0m\n"
combine -M ProfileLikelihood --signif --cminDefaultMinimizerType=Minuit2 -t -1 --expectSignal=1.0 -s -1 datacard-mumu.txt 2> /dev/null

printf "\n\n\e[1m!=== COMBINED EXPECTED SIGNIFCANCE===!\e[0m\n"
combine -M ProfileLikelihood --signif --cminDefaultMinimizerType=Minuit2 -t -1 --expectSignal=1.0 -s -1 datacard.txt 2> /dev/null
