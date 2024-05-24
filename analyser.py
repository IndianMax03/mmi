import pandas as pd
import numpy as np
import random
from sklearn.linear_model import LinearRegression
from sklearn import metrics


class Analyser:

    def __init__(self, filename):
        self._filename = filename
        self._target_label = 'Дельта_калорий'
        data = pd.read_csv(filename)

        x = data.drop(self._target_label, axis=1)
        y = data[self._target_label]

        indices = list(range(len(x)))
        test_size = 0.2  # 20%
        random.seed(42)
        random.shuffle(indices)
        split_index = int(len(x) * test_size)

        x_train = x.iloc[indices[split_index:]]
        x_test = x.iloc[indices[:split_index]]
        y_train = y.iloc[indices[split_index:]]
        y_test = y.iloc[indices[:split_index]]

        model = LinearRegression()

        model.fit(x_train, y_train)

        y_predicted = model.predict(x_test)

        self._accuracy = np.round(metrics.r2_score(y_test, y_predicted), 2) * 100

        coefficients = model.coef_
        features = model.feature_names_in_

        attribute_impact: dict[str, float] = {}

        coef_sum = sum([abs(coefficient) for coefficient in coefficients])

        for i in range(coefficients.size):
            attribute_impact[features[i]] = round(abs(coefficients[i]) / coef_sum * 100, 2)

        sorted_attribute_impact: dict[str, float] = dict(
            sorted(attribute_impact.items(), key=lambda item: item[1], reverse=True))
        self._attribute_impact = sorted_attribute_impact

        main_impact_value_name = next(iter(sorted_attribute_impact))
        last_two_weeks = data.tail(14).drop(self._target_label, axis=1)
        self._main_impact_value_name = main_impact_value_name

        max_main_impact_value = last_two_weeks[main_impact_value_name].max()
        last_two_weeks[main_impact_value_name] = max_main_impact_value
        impact_predict = model.predict(last_two_weeks)
        weight_changing_in_two_weeks = sum(impact_predict) / 7700
        weight_changing_in_moth = weight_changing_in_two_weeks * 2
        self._weight_changing_in_moth = weight_changing_in_moth

    def get_accuracy(self):
        return self._accuracy

    def get_attribute_impact_str(self):
        result: str = f'Влияние показателей на целевое значение "{self._target_label}":\n\n'
        for attr, percent in self._attribute_impact.items():
            result += f'{percent:.2f}% -> {attr}\n'

        return result

    def get_weight_changing_in_moth(self) -> float:
        return self._weight_changing_in_moth

    def get_main_impact_value_name(self):
        return self._main_impact_value_name
