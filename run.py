import sys
from clean import Cleaner
from classify import Classifier
import os

congress_id = ""
if len(sys.argv) > 3 or len(sys.argv) < 2:
    print("Please Enter valid parameter:")
    print("Parameter: Congress term number")
    print("Option: --skip, avoid data cleaning")
    sys.exit()

if len(sys.argv) == 2:
    congress_id = str(sys.argv[1])
    if os.path.isfile("rawData/" + "speeches_" + congress_id + ".txt") and os.path.isfile("rawData/" + congress_id + "_SpeakerMap.txt"):
        print("cleaning ....")
        data_cleaner = Cleaner([congress_id])
        data_cleaner.clean_pipeline()
        print("classifying ....")
        congress_classifier = Classifier([congress_id])
        congress_classifier.base_pipeline()
        print("done.")
        sys.exit()
    else:
        print("There are no speeches and speakerMap text file to process for congress " + congress_id)
        print("Please put the target congress raw text data into rawData directory")
        sys.exit()

if len(sys.argv) == 3 and (sys.argv[1] == "--skip"):  # skip data cleaning (data is already cleaned)
    congress_id = str(sys.argv[2])
    if os.path.isfile("processedData/" + congress_id + "_House_tokenized.csv") and os.path.isfile("processedData/" + congress_id + "_Senate_tokenized.csv"):
        print("classifying ....")
        congress_classifier = Classifier([congress_id])
        congress_classifier.base_pipeline()
        print("done.")
        sys.exit()
    else:
        print("There are no clean csv files in processedData directory for congress " + congress_id)
        sys.exit()


print("Please Enter valid parameter:")
print("Parameter: Congress term number")
print("Option: --skip, avoid data cleaning")
sys.exit()


