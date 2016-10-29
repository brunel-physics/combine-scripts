#!/bin/sh

printf "\e[1m!=== OBSERVED SIGNIFICANCE ===!\e[0m\n"
combine -M ProfileLikelihood --signif --cminDefaultMinimizerType=Minuit2 -s -1 datacard.txt 2> /dev/null

printf "\n\n\e[1m!=== A PRIORI EXPECTED SIGNIFCANCE===!\e[0m\n"
combine -M ProfileLikelihood --signif --cminDefaultMinimizerType=Minuit2 -t -1 --expectSignal=1.0 -s -1 datacard.txt 2> /dev/null

printf "\n\n\e[1m!=== A POSTERIORI EXPECTED SIGNIFICANCE===!\e[0m\n"
combine -M ProfileLikelihood --signif --cminDefaultMinimizerType=Minuit2 -t -1 --expectSignal=1.0 -s -1 --toysFreq datacard.txt 2> /dev/null
