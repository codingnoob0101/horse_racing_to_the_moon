# horse_racing_to_the_moon


This project aims to train a machine learning model to predict the result of a horse race, by providing related information of the horse and the race.

Data collection:
- Hong Kong: https://racing.hkjc.com/racing/information/English/Horse/ListByLocation.aspx?Location=HK 
- Conghua: https://racing.hkjc.com/racing/information/English/Horse/ListByLocation.aspx?Location=CH 
- lots of missing data due to retirement of horses or oversea horses participating into the race
- the approach changed to 1) scraping race data from fixture published by hkjc -> 2)access the race through 'date', 'venue', loop through race numbers for each race -> 3)scrap the href for each participating horse -> 4) from the href, scrape race data (able to access retired horses)


Modeling:
- using learning-to-rank models to output the ranking:
    1) pairwise approach (RankNet): probability that one horse will finish ahead of another
    2) listwise approach (ListNet, ListMLE, XGBoost with ranking objective): directly predict the best overall ordering of all horses in a race

