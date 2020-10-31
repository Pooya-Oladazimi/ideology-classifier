class Helper:
    def __init__(self):
        pass

    @staticmethod
    def readCSV(path):
        import pandas
        dump = pandas.read_csv(path, sep="\t")
        dump = dump.fillna(-1)
        return dump

    @staticmethod
    def file_splitor(path, congress_Id): # split txt files to chunks since the text files are large to precess
        import os
        content = open(path, "r", errors='ignore')
        limit = 15000
        Index = 1
        counter = 1
        target = open("temp/" + congress_Id + "_" + str(counter) + "_chunk.txt", "w")
        for line in content:
            if limit == Index:
                Index = 1
                target.close()
                counter += 1
                target = open("temp/" + congress_Id + "_" + str(counter) + "_chunk.txt", "w")

            target.write(line)
            Index += 1
        return counter

    @staticmethod
    def tokenize(data):  # tokenize speeches, remove stop words, lemmatize
        from nltk.tokenize import word_tokenize
        from nltk import pos_tag
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        from collections import defaultdict
        from nltk.corpus import wordnet as wn
        import nltk
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        data['speeches'].dropna(inplace=True)
        data['speeches'] = [entry.lower() for entry in data['speeches']]
        data['speeches'] = [word_tokenize(entry) for entry in data['speeches']]
        tag_map = defaultdict(lambda: wn.NOUN)
        tag_map['J'] = wn.ADJ
        tag_map['V'] = wn.VERB
        tag_map['R'] = wn.ADV

        for index, entry in enumerate(data['speeches']):
            Final_words = []
            word_Lemmatized = WordNetLemmatizer()
            for word, tag in pos_tag(entry):
                if word not in stopwords.words('english') and word.isalpha():
                    word_Final = word_Lemmatized.lemmatize(word, tag_map[tag[0]])
                    Final_words.append(word_Final)
            data.loc[index, 'text_final'] = str(Final_words)
        return data

    @staticmethod
    def tf(data_list):  # term frequency for a list of corpus. each list element is a corpus (like [House, Senate])
        import ast
        result = {}
        for data in data_list:
            for speech in data['text_final']:
                for token in ast.literal_eval(speech):
                    if token in result.keys():
                        result[token] += 1
                    else:
                        result[token] = 1
        return result

    @staticmethod
    def filter_words(data, corpus_tf, max_limit, states, names):
        # remove words with low ( > 4) and high ( < max_limit) term frequency
        # remove state and people names
        import ast
        for Index, row in data.iterrows():
            final_text = ast.literal_eval(row['text_final'])
            new_final_text = []
            for word in final_text:
                if 4 < corpus_tf[word] < max_limit and word not in states and word not in names:
                    new_final_text.append(word)
            data.at[Index, 'text_final'] = str(new_final_text)
        data = data[data['text_final'] != '[]']
        return data

    @staticmethod
    def get_people_names(Id):  # return a list of congress member names
        names = []
        speakers = Helper.readCSV("processedData/" + Id + "_SpeakerMap.csv")
        f_name = list(speakers['firstname'])
        l_name = list(speakers['lastname'])
        names = f_name + l_name
        names = [entry.lower() for entry in names]
        names = set(names)
        return list(names)

    @staticmethod
    def get_states_name():  # returns states name
        states = []
        file = open("states.txt", "r")
        for line in file:
            states.append(line.strip().lower())
        return states

    @staticmethod
    def run_svm(train_x, train_y, test_x, test_y, all_text): # Support Vector Machine algorithm
        from sklearn.preprocessing import LabelEncoder
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn import svm
        from sklearn.metrics import accuracy_score
        encoder = LabelEncoder()
        train_y = encoder.fit_transform(train_y)
        test_y = encoder.fit_transform(test_y)
        tfidf_vect = TfidfVectorizer()
        tfidf_vect.fit(all_text)
        train_x_tfidf = tfidf_vect.transform(train_x)
        test_x_tfidf = tfidf_vect.transform(test_x)
        svm_model = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
        svm_model.fit(train_x_tfidf, train_y)
        predictions_svm = svm_model.predict(test_x_tfidf)
        return accuracy_score(predictions_svm, test_y) * 100

