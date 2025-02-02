#!/bin/sh

pwd
while true; do
    echo "===== Running script at $(date) ====="

    echo "YouTube Video ID,Match ID,Date,Stage,Player 1 Ringname,Player 1 Rank,Player 1 Character,Player 2 Ringname,Player 2 Rank,Player 2 Character,round_number,Winning Player Number,How Round Ended,Time Remaining When Round Ended,Shun.Drinks.1P,Shun.Drinks.2P,Strike First Player,P1 Health,P2 Health,P1 Rounds Won So Far,P2 Rounds Won So Far,Match Winner,Youtube Link" > ../virtuanalytics_dashboard/vf_match_data.csv
    
    #excluding NA, I wonder if we need or not
    cat match_data*csv | grep -E ',EX,|,RO,|,TO,|,KO,' | sed 's/Lei Fei/LeiFei/g' | sort >> ../virtuanalytics_dashboard/vf_match_data.csv

    cd ../virtuanalytics_dashboard/data/ && rm *.Rda
    cd ../ && Rscript deploy_app.R
    cd ../vf_analytics

    echo "     done loop at $(date) ====="
    pwd

    sleep 900
done