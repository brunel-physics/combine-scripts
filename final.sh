#!/usr/bin/env bash

set -Eeuo pipefail

minlib="Minuit2"
algo="Combined"
strategy=1
toys=-1
seed=777

combine () {
    combineTool.py --cminDefaultMinimizerStrategy="${strategy}" --cminDefaultMinimizerType="${minlib}" --cminDefaultMinimizerAlgo="${algo}" --expectSignal=1.0 --toys "${toys}" --mass 120 --seed "${seed}" "${@}"
}

mkdir -p 2016+2017/datacards 2016+2017/shapes

cp 2016/datacards/datacard_combined.txt 2016+2017/datacards/datacard_combined_2016.txt
cp 2017/datacards/datacard_combined.txt 2016+2017/datacards/datacard_combined_2017.txt

pushd 2016+2017/datacards
combineCards.py era_2016=datacard_combined_2016.txt era_2017=datacard_combined_2017.txt > datacard_all.txt
popd

text2workspace.py --poisson=2147483647 --no-optimize-pdfs 2016+2017/datacards/datacard_all.txt

combine -M Significance -d 2016+2017/datacards/datacard_all.root --bruteForce --setBruteForceTypeAndAlgo $minlib,$algo --uncapped 1

combine -M FitDiagnostics -d 2016+2017/datacards/datacard_all.root --robustFit=1 --setRobustFitAlgo=$minlib,$algo --setRobustFitStrategy=$strategy --rMin -5
