class Classifier:
    def __init__(self, congress_Ids):
        from helper import Helper
        import pandas as pd
        import operator
        import collections
        from sklearn import model_selection
        self.congress_Ids = congress_Ids
        self.helper = Helper
        self.pandas = pd
        self.operator = operator
        self.top_frequency_bound = 50
        self.collection = collections
        self.model_selection = model_selection
        self.house_base_line = Classifier.get_congress_majority_baselines('house')
        self.senate_base_line = Classifier.get_congress_majority_baselines('senate')

    @staticmethod
    def get_congress_majority_baselines(chamber):
        result = {}
        file = open("congress_metadata", 'r').read()
        file = file.split('\n')
        for line in file:
            line = line.split(',')
            if len(line) == 4 and line[0] == chamber:
                result[str(line[1])] = [str(line[2]), str(line[3])]
        return result

    def create_result_record(self, name, train_name, test_name, accuracy):
        Input = {}
        Input['Name'] = name
        Input["Train"] = train_name
        Input["Test"] = test_name
        Input["accuracy"] = accuracy
        Input["majority_House"] = self.house_base_line[name][0] + " - " + self.house_base_line[name][1]
        Input["majority_Senate"] = self.senate_base_line[name][0] + " - " + self.senate_base_line[name][1]
        return Input

    def base_pipeline(self):
        cols = ["Name", "Train", "Test", "accuracy", "majority_House", "majority_Senate"]
        Result = self.pandas.DataFrame(columns=cols)
        states = self.helper.get_states_name()
        for Id in self.congress_Ids:
            names = self.helper.get_people_names(Id)
            house = self.helper.readCSV("processedData/" + Id + "_House_tokenized.csv")
            senate = self.helper.readCSV("processedData/" + Id + "_Senate_tokenized.csv")
            corpus_tf = self.helper.tf([house, senate])
            corpus_tf = sorted(corpus_tf.items(), key=self.operator.itemgetter(1))
            # to remove the most n frequent words
            top_n_lower_bound = corpus_tf[len(corpus_tf) - self.top_frequency_bound][1]
            corpus_tf = self.collection.OrderedDict(corpus_tf)
            house = self.helper.filter_words(house, corpus_tf, top_n_lower_bound, states, names)
            senate = self.helper.filter_words(senate, corpus_tf, top_n_lower_bound, states, names)
            congress = house.append(senate, ignore_index=True)
            # House to Senate
            accuracy = self.helper.run_svm(house['text_final'], house['party'], senate['text_final'], senate['party'],
                                           congress['text_final'])
            Result = Result.append(self.create_result_record(Id, "House", "Senate", accuracy), ignore_index=True)
            # Senate to House
            accuracy = self.helper.run_svm(senate['text_final'], senate['party'], house['text_final'], house['party'],
                                           congress['text_final'])
            Result = Result.append(self.create_result_record(Id, "Senate", "House", accuracy), ignore_index=True)
            # House to House
            Train_X, Test_X, Train_Y, Test_Y = self.model_selection.train_test_split(house['text_final'], house['party'],
                                                                                test_size=0.3)
            accuracy = self.helper.run_svm(Train_X, Train_Y, Test_X, Test_Y, house['text_final'])
            Result = Result.append(self.create_result_record(Id, "House", "House", accuracy), ignore_index=True)
            # Senate to Senate
            Train_X, Test_X, Train_Y, Test_Y = self.model_selection.train_test_split(senate['text_final'], senate['party'],
                                                                                test_size=0.3)
            accuracy = self.helper.run_svm(Train_X, Train_Y, Test_X, Test_Y, senate['text_final'])
            Result = Result.append(self.create_result_record(Id, "Senate", "Senate", accuracy), ignore_index=True)

        Result.to_csv("results/base_pipeline.csv", sep='\t', encoding='utf-8')
        return True








