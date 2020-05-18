#!/usr/bin/env bash

set -Eeuo pipefail
# set -x

usage () {
    printf -- "Usage:\n\t-l\tMinimiser type\n\t-a\tMinimiser algorithm\n\t-s\tMinimiser strategy\n\t-t\tToys\n\t-S\tSeed\n"
}

t2w () {
    text2workspace.py "${@}"
}

combine () {
    combineTool.py --cminDefaultMinimizerStrategy="${strategy}" --cminDefaultMinimizerType="${minlib}" --cminDefaultMinimizerAlgo="${algo}" --expectSignal=1.0 --toys "${toys}" --mass 120 --seed "${seed}" "${@}"
}

significance () {
    combine -M Significance -d ${era}/datacards/datacard_"${1}".root --bruteForce --setBruteForceTypeAndAlgo $minlib,$algo --uncapped 1 --name "_${1}" --plot out/${era}/loglikelihood_"${1}".png
}

signal () {
    combine -M FitDiagnostics -d ${era}/datacards/datacard_"${1}".root --robustFit=1 --setRobustFitAlgo=$minlib,$algo --setRobustFitStrategy=$strategy --rMin -15 --out out/${era} --name "_${1}" --plots --saveShapes --saveWithUncertainties # --ignoreCovWarning 
}

shapes () {
    PostFitShapesFromWorkspace -w ${era}/datacards/datacard_"${1}".root -o out/${era}/shapes_"${1}".root -m 120 --postfit --print --covariance --sampling -f out/${era}/fitDiagnostics_"${1}".root:fit_s > logs/postfitshapes_"${1}".log
}

impacts () {
    combine -M Impacts -d ${era}/datacards/datacard_"${1}".root --rMin -5 --doInitialFit --robustFit=1 --setRobustFitAlgo=$minlib,$algo --setRobustFitStrategy=$strategy --name "${1}" > logs/impacts_"${1}".log 2>&1
    rename "${seed}." '' higgsCombine_initialFit_"${1}"*
    combine -M Impacts -d ${era}/datacards/datacard_"${1}".root --rMin -5 --doFits --parallel $(nproc) --robustFit=1 --setRobustFitAlgo=$minlib,$algo --setRobustFitStrategy=$strategy --name "${1}" >> logs/impacts_"${1}".log 2>&1
    rename "${seed}." '' higgsCombine_paramFit_"${1}"*
    combine -M Impacts -d ${era}/datacards/datacard_"${1}".root --rMin -5 --robustFit=1 --setRobustFitAlgo=$minlib,$algo --setRobustFitStrategy=$strategy -o out/${era}/impacts_"${1}".json --name "${1}" >> logs/impacts_"${1}".log 2>&1

    # Before making the plot remove all nuisance parameters from statistical
    # uncertainties
    python stat_remover.py out/${era}/impacts_"${1}".json

    plotImpacts.py -i out/${era}/impacts_"${1}".json -o out/${era}/impacts_"${1}" --translate ${era}/json/thesis.json --per-page 50 --label-size 0.03
}

# Defaults
minlib="Minuit2"
algo="Migrad"
strategy=1
toys=-1
seed=777
era=2017

while getopts "l:a:e:s:S:t:h" OPTION; do
    case "${OPTION}" in
        l)
            minlib="${OPTARG}"
            ;;
        a)
            algo="${OPTARG}"
            ;;
        e) 
            era="${OPTARG}"
            ;;
        s)
            strategy="${OPTARG}"
            ;;
        S)
            seed="${OPTARG}"
            ;;
        t)
            toys="${OPTARG}"
            ;;
        h)
            usage
            exit 0
            ;;
        ?)
            usage
            exit 1
            ;;
    esac
done
shift "$((${OPTIND} -2))"

printf "\e[1m!===SETUP===!\e[0m\n"
mkdir -p logs out/${era}
rm -f higgsCombine* out/${era}/* ${era}/datacards/datacard*.root ${era}/datacards/datacard_combined.txt logs/*.log

printf "\e[1m!== Creating workspaces ==!\e[0m\n"
# Create workspaces
t2w ${era}/datacards/datacard_ee.txt > logs/text2workspace_datacard_ee.log
t2w ${era}/datacards/datacard_mumu.txt > logs/text2workspace_datacard_mumu.log

printf "\e[1m!== Combining Datacards ==!\e[0m\n"
# Combine datacards
pushd ${era}/datacards/
combineCards.py MVA_ee=datacard_ee.txt MVA_mumu=datacard_mumu.txt > datacard_combined.txt
popd
t2w ${era}/datacards/datacard_combined.txt > logs/text2workspace_datacard.log

printf "\n"
printf "\e[1m!===CALCULATING SIGNIFICANCES===!\e[0m\n"
printf "\e[1m!== ee SIGNIFICANCE==!\e[0m\n"
significance ee

printf "\n\e[1m!== μμ SIGNIFICANCE==!\e[0m\n"
significance mumu

printf "\n\e[1m!== COMBINED SIGNIFICANCE==!\e[0m\n"
significance combined

printf "\n"
printf "\e[1m!===CALCULATING SIGNAL STRENGTHS===!\e[0m\n"
printf "\e[1m!== ee SIGNAL STRENGTH==!\e[0m\n"
signal ee

printf "\n\e[1m!== μμ SIGNAL STRENGTH==!\e[0m\n"
signal mumu

printf "\n\e[1m!== COMBINED SIGNAL STRENGTH==!\e[0m\n"
signal combined

if [ "${toys}" -gt 1 ]
then
    exit 0;
fi

printf "\n\e[1m!===CREATING POST-FIT SHAPES===!\e[0m\n"
printf "\e[1m!== ee ==!\e[0m\n"
shapes ee

printf "\e[1m!== μμ ==!\e[0m\n"
shapes mumu

printf "\e[1m!== COMBINED ==!\e[0m\n"
shapes combined

printf "\n"
printf "\e[1m!===CREATING POST-FIT IMPACT PLOTS===!\e[0m\n"
printf "\e[1m!== ee ==!\e[0m\n"
impacts ee

printf "\n\e[1m!== μμ ==!\e[0m\n"
impacts mumu

printf "\n\e[1m!== COMBINED ==!\e[0m\n"
impacts combined

# printf "\e[1m!===CREATING STACKPLOTS===!\e[0m\n"
# ./stackplots.py out/${era}/shapes_combined.root out/${era}/
