# horse_racing_to_the_moon


This project aims to train a machine learning model to predict the result of a horse race, by providing related information of the horse and the race.

Data collection:
1) scraping race data from fixture published by hkjc (start from 10/09/2023)
2) access the race through 'date', 'venue', loop through race numbers for each race 
3) scrap the href for each participating horse 
4) from the href, scrape race data (able to access retired horses)

scraped dataframe contain 25 columns, which further engineering were done

Current problem: horse id contain strange data


Modeling:
- using learning-to-rank models to output the ranking:
    XGBoost support learning to rank task (objective = 'rank:ndcg, or objective = 'rank:pairwise')