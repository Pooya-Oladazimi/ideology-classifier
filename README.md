I implemented this python project for a seminar paper and [a talk](https://west.uni-koblenz.de/talks/30-07-2020-challenges-interpreting-political-text-classification) at the 
[University of Koblenz](https://west.uni-koblenz.de/). This code classifies US congress members to parties based 
on their speeches content. The goal was to understand the challenges in 
interpreting the outcome of ideology classification in political science.  

### Key findings 
- US House is not more partsian than the senate. However, it is better for training since it has more members than the Senate. 
- Partisanship is increasing in between US major parties in Congress
- Ideology is Not the only factor which shapes speeches, Political party position (incumbent/challenger) also affects it. 


### Methodology
- Classification: Support Vector Machine (SVM)
- Vectorization: TF-IDF 
- Text representation: Bag-of-Words 


### Compatibility 
Python 3.6

### install packages
`pip install requirements.txt `  or  `python -m pip install requirements.txt`

### data source
[Stanford, SSDS Social Science Data Collection](https://data.stanford.edu/congress_text) (hein-daily)

### Usage

`python run.py Congress_ID [--skip]`


- **Congress_ID**: the target congress Id. Ex: 114 is the ID for 114th US Congress.

- **--skip**: (optional) if you want to skip data cleaning, In case you already cleaned it. 

### Directory and Files

- **processedData**: contains the processed data after cleaning.

- **rawData**: contains the raw text data which you can get from data source (Stanford). There are two text data which you need:
  - **n_SpeakerMap.txt**: n is the congress ID.
  - **speeches_n.txt**: n is the congress ID.

- **temp**: needed for data cleaning

- **results**: contains the final outcome.

- **states.txt**: contains US states name, used for cleaning

- **congress_metadata**: contains each congress chamber majority baseline. Format has to be like  "chamber,congress_ID,percentage,party", For example, "house,109,53,R". This means in 109th congress, Republicans had the majority in house chamber with 53 percents:
  - **chamber**: house or senate
  - **congress_ID**: congress term number
  - **percentage**: majority baseline
  - **party**: R (Republicans) , D (Democrats)
  
  
### Results structure 
The results will be in *results/base_pipeline.csv*. It contains four runs for the target congress:
- **House to Senate**: Train on house, Test on senate
- **Senate to House**: Train on senate, Test on house
- **House to House**: Train on house, Test on house
- **Senate to Senate**: Train on senate, Test on senate

### Data cleaning
- remove stop words
- remove non-alpha words
- lemmatization
- remove terms with low (< 4) and high (> 50) term frequency.
- remove people (congress members) names
- remove states name





  
