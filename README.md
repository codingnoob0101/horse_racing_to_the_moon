# horse_racing_to_the_moon


This project aims to train a machine learning model to predict the result of a horse race, by providing related information of the horse and the race.

Data collection:
1) scraping race data from fixture published by hkjc (start from 10/09/2023)
2) access the race through 'date', 'venue', loop through race numbers for each race 
3) scrap the href for each participating horse 
4) from the href, scrape race data (able to access retired horses)

scraped dataframe contain 25 columns, which further engineering were done

Data cleaning:
- data are cleaned in different aspect
- excluded all the horses that have the 'WV' labels, as they didn't participate the race at last
- included one hot encoding for gears of the horses
- "found that the race class is not in the same format, there are some with G in front of the class"


Modeling:
- using learning-to-rank models to output the ranking, catboost are being chosen for the problem.
    there are two models included: 
    1) include the following variables:
        - categorical: race distance, track condition, race class, gate position, trainer, jockey, import type, sire, dam, dam sire, race course, track, course, origin, age, colour, sex
        - numerical: rating, win odds, act weight, declar. horse weight
    2) include all the above variables, except 'win odds'
    3) tried to also include gears used by horse within the race, but the NDCG score is lowered

Inferencing:
- input race card url and odds url for scraping of latest pre-race data.
- 'Final_inference' will output the name of the horse and predicted score by decending order (higher the score, better the rank being predicted)
- two functions inluded, one included win odds and one without


version_2:

features being used:
categorical_cols = [
    'Dist.', 'track_condition', 'RaceClass', 'Trainer', 'Jockey', 'Dam sire', 'rc', 'track', 'course', 
    'Import type', 'Sire', 'Dam', 'origin', 'age', 'colour', 'sex'
]

numerical_cols = [
    'Rtg.', 'Act.Wt.', 'Declar.Horse Wt.','recent_3_win_rate_horse',
       'recent_3_win_rate_jockey', 'recent_5_avg_finish_pos',
       'recent_3_consistency', 'jockey_trainer_combo_rate',
       'horse_track_distance_rate'
]