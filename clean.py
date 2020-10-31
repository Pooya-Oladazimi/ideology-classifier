class Cleaner:
    def __init__(self, congress_Ids):
        from helper import Helper
        import os
        import pandas as pd
        self.congress_Ids = congress_Ids
        self.helper = Helper
        self.os = os
        self.pandas = pd

    def speakers_to_csv(self, Id):
        csv_file = "processedData/" + Id + "_SpeakerMap.csv"
        if self.os.path.isfile(csv_file): # already exist so do not process it again
            return True
        file_name = "rawData/" + Id + "_SpeakerMap.txt"
        content = open(file_name, "r")
        header = True
        Index = 0
        for line in content:
            if header:  # set dataframe columns name
                cols = line.strip('\n').split('|')
                frame = self.pandas.DataFrame(columns=cols)
                header = False
                continue
            line_elements = line.strip('\n').split('|')
            frame.loc[Index] = line_elements
            Index += 1
        frame.to_csv(csv_file, sep='\t', encoding='utf-8')
        return True

    def speeches_to_csv(self, Id, chunk_count):
        csv_file = "rawData/" + Id + "_speeches.csv"
        if self.os.path.isfile(csv_file): # already exist so do not process it again
            return True
        header = True
        Index = 0
        for ch in range(1, chunk_count + 1):
            file_name = "temp/" + Id + "_" + str(ch) + "_chunk.txt"
            content = open(file_name, "r", errors='ignore')
            for line in content:
                if header:
                    cols = line.strip('\n').split('|')
                    frame = self.pandas.DataFrame(columns=cols)
                    header = False
                    continue

                line_elements = line.strip('\n').split('|')
                if len(line_elements) != 2:  # we supposed to have only two columns
                    temp = [0, 0]
                    temp[1] = ''.join(line_elements[1:])
                    temp[0] = line_elements[0]
                    line_elements = temp

                frame.loc[Index] = line_elements
                Index += 1

            content.close()

        frame.to_csv(csv_file, sep='\t', encoding='utf-8')
        return True

    def convert_to_csv(self):
        for Id in self.congress_Ids:
            self.speakers_to_csv(Id)
            path = "rawData/" + "speeches_" + Id + ".txt"
            chunk_count = self.helper.file_splitor(path, Id)   # split the large text data to chunks
            self.speeches_to_csv(Id, chunk_count)

        return True

    def map_speech_to_speaker(self):
        for Id in self.congress_Ids:
            speeches = self.helper.readCSV("rawData/" + Id + "_speeches.csv")
            speakers = self.helper.readCSV("processedData/" + Id + "_SpeakerMap.csv")
            col = ["speech", "id", "speaker", "chamber", "party"]
            data = self.pandas.DataFrame(columns=col)
            for Index, row in speeches.iterrows():
                Input = {}
                speech_id = row['speech_id']
                speaker_row = speakers.loc[speakers['speech_id'] == speech_id]
                chamber = speaker_row['chamber'].tolist()
                if chamber == []:
                    chamber = ""
                else:
                    chamber = chamber[0]
                if chamber in ['S', 'H']:  # S for Senate and H for House
                    Input['speech'] = row['speech']
                    Input['id'] = row['speech_id']
                    Input['speaker'] = speaker_row['speakerid'].tolist()[0]
                    Input['chamber'] = speaker_row['chamber'].tolist()[0]
                    Input['party'] = speaker_row['party'].tolist()[0]
                    data = data.append(Input, ignore_index=True)

            data.to_csv("rawData/" + Id + "_mapped_data.csv", sep='\t', encoding='utf-8')
            return True

    def separate_house_senate(self):  # separate  House and Senate Data
        for Id in self.congress_Ids:
            data = self.helper.readCSV("rawData/" + Id + "_mapped_data.csv")
            col = ["speech", "id", "speaker", "party"]
            data_house = self.pandas.DataFrame(columns=col)
            data_senate = self.pandas.DataFrame(columns=col)
            for Index, row in data.iterrows():
                if row['chamber'] == "S":  # Senate
                    Input = {}
                    Input['speech'] = row['speech']
                    Input['id'] = row['id']
                    Input['speaker'] = row['speaker']
                    Input['party'] = row['party']
                    data_senate = data_senate.append(Input, ignore_index=True)
                else:
                    Input = {}
                    Input['speech'] = row['speech']
                    Input['id'] = row['id']
                    Input['speaker'] = row['speaker']
                    Input['party'] = row['party']
                    data_house = data_house.append(Input, ignore_index=True)

            data_house.to_csv("rawData/" + Id + "_House.csv", sep='\t', encoding='utf-8')
            data_senate.to_csv("rawData/" + Id + "_Senate.csv", sep='\t', encoding='utf-8')
            return True

    def create_speech_per_person(self, data):   # gather all speeches for each congress member
        person_ids = set(list(data['speaker']))
        cols = ["person", "party", "speeches"]
        frame = self.pandas.DataFrame(columns=cols)
        for Id in person_ids:
            if list(data.loc[data['speaker'] == int(Id)]['party'])[0] in ["D", "R"]:  # get only Republicans and Democrats
                person_speeches = " ".join(list(data.loc[data['speaker'] == int(Id)]['speech']))
                Row = {}
                Row['person'] = Id
                Row['party'] = list(data.loc[data['speaker'] == int(Id)]['party'])[0]
                Row['speeches'] = person_speeches
                frame = frame.append(Row, ignore_index=True)
        return frame

    def clean_pipeline(self):
        answer = self.convert_to_csv()
        if not answer:
            raise Exception("Cannot convert text to csv")
        answer = self.map_speech_to_speaker()
        if not answer:
            raise Exception("Cannot map speakers to speeches")
        answer = self.separate_house_senate()
        if not answer:
            raise Exception("Cannot separate House and Senate data")

        for Id in self.congress_Ids:
            House = self.helper.readCSV("rawData/" + Id + "_House.csv")
            Senate = self.helper.readCSV("rawData/" + Id + "_Senate.csv")
            house_speeches = self.create_speech_per_person(House)
            senate_speeches = self.create_speech_per_person(Senate)
            house_speeches = self.helper.tokenize(house_speeches)
            senate_speeches = self.helper.tokenize(senate_speeches)
            house_speeches.to_csv("processedData/" + Id + "_House_tokenized.csv", sep='\t', encoding='utf-8')
            senate_speeches.to_csv("processedData/" + Id + "_Senate_tokenized.csv", sep='\t', encoding='utf-8')

        return True


