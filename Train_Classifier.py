import pandas as pd
from Model_DQN import *
import warnings

warnings.filterwarnings("ignore")

class Classifier():

    def __init__(self):

        import numpy as np
        self.Coin = np.loadtxt("./Log/Coin_Select.txt", dtype=np.str)

    def GetData_Classifier(self):

        from sklearn import preprocessing
        import numpy as np
        scaler = preprocessing.StandardScaler()

        Data = np.loadtxt(open("./Data/Data.csv", "rb"), delimiter=",", skiprows=0)
        Data = scaler.fit_transform(Data)
        PriceArray = np.loadtxt(open("./Data/PriceArray.csv", "rb"), delimiter=",", skiprows=0)

        DQN_Data = pd.DataFrame()
        agent = DQN()

        Price_Begun = PriceArray[-1,-1]
        Action_last = len(self.Coin)

        Reward = 0
        Q_Value = 0
        D_price = 0

        for number in range(2, len(Data)):

            state = Data[number, :]
            action = agent.action(state)
            Price_Now = PriceArray[:, action]
            gamma = 0.95
            fex = 1 / (0.998 * 0.998) - 1
            f_reward = 0
            for x in range(0, 2):
                f_reward += gamma * (
                            ((Price_Now[number - x] - Price_Now[number - x - 1]) / Price_Now[number - x]) - fex)
                gamma = gamma ** 2

            action_reward = float(f_reward)
            d_price = max(Price_Now[:number + 1]) - Price_Now[number]

            Price = PriceArray[number,action]
            SellPrice = PriceArray[number,Action_last]

            if action != Action_last:

                Inc = float(SellPrice / Price_Begun - 1)
                Target = 1 if Inc > 0 else 0
                Price_Begun = Price

                insert = np.array([Reward, Q_Value,Action_last,D_price])
                insert = scaler.fit_transform(insert.reshape((-1, 1))).reshape(insert.shape[0], )

                D_price = d_price
                Reward = action_reward
                Q_Value = agent.Q_Value
                Action_last = action

                ClassifierDa = (state.tolist() + insert.tolist()+[Target])
                ClassifierDa = np.array([ClassifierDa])

                if number == 2:
                    DQN_Data = ClassifierDa
                else:
                    DQN_Data = np.row_stack((DQN_Data, ClassifierDa))

            self.DQN_Data = DQN_Data

    def Get_Model_Single(self):

        try:
            model = load_model('./Keras_Model/my_model.h5')
            print('Successfully loaded : my_model')
        except:

            from keras.models import Sequential
            from keras.layers import Dense, Dropout

            model = Sequential()
            model.add(Dense((self.DQN_Data.shape[1] - 1) * 2, input_dim=self.DQN_Data.shape[1] - 1, init='uniform', activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(self.DQN_Data.shape[1] - 1, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(self.DQN_Data.shape[1] - 1, activation='relu'))
            model.add(Dense(1, init='uniform', activation='sigmoid'))
            model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model


    def main(self):

        self.GetData_Classifier()
        model = self.Get_Model_Single()
        Feature_Train, Feature_Test, Target_Train \
            , Target_Test = train_test_split(self.DQN_Data[:, :-1], self.DQN_Data[:, -1]
                                             , test_size=0.2, random_state=0)
        model.fit(Feature_Train, Target_Train, batch_size=10, nb_epoch=10000, verbose=0,
                  validation_data=(Feature_Test, Target_Test))
        model.save('./Keras_Model/my_model.h5')

        from keras.models import load_model
        model = load_model('./Keras_Model/my_model.h5')
        score = model.evaluate(Feature_Test, Target_Test, )
        # print(model.predict_classes(Feature_Test))
        print('Test score:', score[0])
        print('Test accuracy:', score[1])


if __name__ == '__main__':

    import time

    from sklearn.model_selection import train_test_split
    import warnings
    from keras.models import load_model

    warnings.filterwarnings("ignore")

    Classifier = Classifier()
    while True:

        StartTime = time.time()
        Classifier.main()
        EndTime = time.time()
        print('Training Using_Time: %d min' % int((EndTime - StartTime) / 60))

        tf.reset_default_graph()
        import gc
        gc.collect()
