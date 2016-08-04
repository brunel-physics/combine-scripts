rm roostats-* input.root higgsCombineTest.HybridNew.mH120.* significances.txt

repeat 1;
do;
  repeat 10;
  do;
    combine -M HybridNew --frequentist datacard.txt --significance --saveToys --fullBToys --saveHybridResult -T 500 -i 5 -s -1 --fork 0 2>&1 | ag Significance >> significances.txt &;
    # combine -M HybridNew -t -1 datacard.txt --significance --saveToys --fullBToys --saveHybridResult -T 500 -i 5 -s -1 --fork 0 2>&1 | ag Significance >> significances.txt &;
  done
  wait;
done

hadd -f input.root higgsCombineTest.HybridNew.mH120.*

combine -M HybridNew --frequentist datacard.txt  --significance --readHybridResult --toysFile=input.root
