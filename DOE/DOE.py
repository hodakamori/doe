import pandas as pd
import numpy as np
import pyDOE2 as doe2
from sklearn.preprocessing import MinMaxScaler
import pyper

class DOE:
    
    def __init__(self, setting_file):
        try:
            self.numerical = pd.read_excel(setting_file, sheet_name='numerical')
        except:
            print("NOTE: Numerical variable is not set.")
        try:
            self.categorical = pd.read_excel(setting_file, sheet_name='categorical')
        except:
            print("NOTE: Categorical variable is not set.")
        if self.numerical is None and self.categorical is None:
            raise ValueError("ERROR: Neither numerical and categorical is not set.") 
        self.table = None

    def linear_to_log(self):

        target_indices = self.numerical[self.numerical['StepType']=='log']['Name'].index
        self.numerical.loc[target_indices,['Min', 'Max']] = self.numerical.loc[target_indices,['Min', 'Max']].apply(np.log10)

    def categorical_to_numeric(self):
        
        for vname in self.categorical['Name'].unique():
            num_counts = len(self.categorical[self.categorical['Name']==vname])
            values = self.categorical[self.categorical['Name']==vname]['Option'].values
            self.numerical = self.numerical.concat({
                'Name':vname,
                'Min':0,
                'Max':num_counts-1,
                'StepType':'categorical',
                'Step':num_counts,
                'Options':values,
            }, ignore_index=True)
    
    def assign_categorical_variables(self):

        target_columns = self.numerical[self.numerical['StepType'] == 'categorical']['Name']
        self.table[target_columns] = self.table[target_columns].astype('int64')

        for col in target_columns:
            options = self.numerical[self.numerical['Name'] == col]['Options'].values[0]
            replace_dict = {index:value for index, value in enumerate(options)}
            self.table[col] = self.table[col].replace(replace_dict)
    
    def assign_numerical_variables(self):

        target_columns = self.numerical[self.numerical['StepType'] != 'categorical']

        for index, row in target_columns.iterrows():
            labels, interval = np.linspace(row['Min'], row['Max'], int(row['Step']), retstep=True)
            edges = np.linspace(row['Min']-interval, row['Max']+interval, int(row['Step'])+1)
            self.table[row['Name']] = pd.cut(self.table[row['Name']], edges, labels=labels)
            
            if row['StepType'] == 'log':
                self.table[row['Name']]
                self.table[row['Name']] = np.power(10, self.table[row['Name']].astype('float'))

    def latin_hypercube(self, num_samples):

        self.linear_to_log()
        try:
            self.categorical_to_numeric()
        except:
            print('Skipped')

        doe_setting = self.numerical[['Min', 'Max']].T

        lhs = doe2.lhs(doe_setting.shape[1], samples=num_samples, criterion='center', random_state=1)

        scaler = MinMaxScaler()
        min_max = scaler.fit(doe_setting)

        self.table = pd.DataFrame(min_max.inverse_transform(lhs), columns=self.numerical['Name'])
        self.assign_categorical_variables()
        self.assign_numerical_variables()  

    def full_fact(self, randomize):

        self.linear_to_log()
        try:
            self.categorical_to_numeric()
        except:
            print('Skipped')


        ff = doe2.fullfact(self.numerical['Step'].values)
        self.table = pd.DataFrame(ff, columns=self.numerical['Name'])

        for index, row in self.numerical.iterrows():
            replace_dict = {key:value for key, value in zip(
                [i for i in range(int(row['Step']))],
                np.linspace(row['Min'], row['Max'], int(row['Step'])),
                )
            }
            self.table[row['Name']] = self.table[row['Name']].replace(replace_dict)
        self.assign_categorical_variables()
        self.assign_numerical_variables()  

        if randomize:
            self.table = self.table.sample(frac=1)

    def placket_burman(self, randomize):

        try:
            self.categorical_to_numeric()
        except:
            print('Skipped')

        for index, row in self.numerical.iterrows():
            if row['Step'] != 2:
                step = row['Step']
                name = row['Name']
                raise ValueError(f'ERROR: {step} of steps for Name:"{name}" is invalid. Placket-Burman design is only available for 2-level factorial.')
        
        pb = doe2.pbdesign(self.numerical.shape[0])
        self.table = pd.DataFrame(pb, columns=self.numerical['Name'])
        for index, row in self.numerical.iterrows():
            self.table[row['Name']] = self.table[row['Name']].replace({-1:row['Min'], 1:row['Max']})

        self.assign_categorical_variables()
        if randomize:
            self.table = self.table.sample(frac=1)

    def central_composite(self, randomize):

        for index, row in self.numerical.iterrows():
            if row['Step'] != 3 or row['StepType'] == "categorical":
                step = row['Step']
                name = row['Name']
                raise ValueError(f'ERROR: {step} of steps for Name:"{name}" is invalid. Central-composite design is only available for 2-level factorial.')

        cc = doe2.ccdesign(self.numerical.shape[0], face='ccf')
        self.table = pd.DataFrame(cc, columns=self.numerical['Name'])
        for index, row in self.numerical.iterrows():
            if row['StepType'] == 'linear':
                self.table[row['Name']] = self.table[row['Name']].replace({-1:row['Min'], 0:(row['Min']+row['Max'])/2, 1:row['Max']})
            elif row['StepType'] == 'log': 
                self.table[row['Name']] = self.table[row['Name']].replace({-1:row['Min'], 0:np.power(10,(np.log10(row['Min'])+np.log10(row['Max'])/2)), 1:row['Max']})

        if randomize:
            self.table = self.table.sample(frac=1)

    def box_behnken(self, randomize):

        for index, row in self.numerical.iterrows():
            if row['Step'] != 3 or row['StepType'] == "categorical":
                step = row['Step']
                name = row['Name']
                raise ValueError(f'ERROR: {step} of steps for Name:"{name}" is invalid. Boc-Behnken design is only available for 2-level factorial.')

        bb = doe2.bbdesign(self.numerical.shape[0])
        self.table = pd.DataFrame(bb, columns=self.numerical['Name'])
        for index, row in self.numerical.iterrows():
            if row['StepType'] == 'linear':
                self.table[row['Name']] = self.table[row['Name']].replace({-1:row['Min'], 0:(row['Min']+row['Max'])/2, 1:row['Max']})
            elif row['StepType'] == 'log': 
                self.table[row['Name']] = self.table[row['Name']].replace({-1:row['Min'], 0:np.power(10,(np.log10(row['Min'])+np.log10(row['Max'])/2)), 1:row['Max']})

        if randomize:
            self.table = self.table.sample(frac=1)

    def d_optimal(self, num_sample):

        self.linear_to_log()
        try:
            self.categorical_to_numeric()
        except:
            print('Skipped')

        r = pyper.R()
        r("library(AlgDesign)")
        names = []

        for index, row in self.numerical.iterrows():

            name = row['Name']
            names.append(name)

            if row['StepType'] == 'linear' or row['StepType'] == 'categorical':
                values = np.linspace(row['Min'], row['Max'], int(row['Step']))
            elif row['StepType'] == 'log':
                values = np.logspace(row['Min'], row['Max'], int(row['Step']), base=10)

            values_string = ",".join(values.astype('str'))
            r(f"{name} <- c({values_string})")

        names_string = ",".join(names)
        r(f"data <- expand.grid({names_string})")
        r(f'desD <- optFederov(~., data, nTrials={num_sample}, criterion = "D")')
        self.table = pd.DataFrame(r.get("desD")["design"])
        self.table.columns = self.numerical['Name'].values
        self.assign_categorical_variables()

    def one_hot_encoding(self):
        get = pd.DataFrame()
        for name in self.categorical['Name'].unique():
            for option in self.categorical[self.categorical['Name']==name]['Option']:
                self.numerical = self.numerical.concat({
                    'Name':f"{name}_{option}",
                    'StepType':'linear',
                    'Min':0,
                    'Max':1,
                    'StepType':'categorical',
                    'Step':2,
                    'Options':['on', 'off']
                }, ignore_index=True)

    def create_table(self, args):

        if args['method'] == 'lth':

            self.latin_hypercube(args['num_samples'])

        elif args['method'] == 'full_fact':

            self.full_fact(args['randomize'])

        elif args['method'] == 'placket_burman':

            self.placket_burman(args['randomize'])

        elif args['method'] == 'central_composite':
            self.central_composite(args['randomize'])

        elif args['method'] == 'box_behnken':
            self.box_behnken(args['randomize'])

        elif args['method'] == 'd_optimal':
            self.d_optimal(args['num_sample'])
   