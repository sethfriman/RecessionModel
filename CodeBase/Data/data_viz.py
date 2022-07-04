# This file will hold methods for visualizing data
import datetime

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import plotly.express as px
import CodeBase.Data.get_data as get_data


class Visualizer:

    def __init__(self):
        self.total_data = get_data.get_total_table()

    def makePlot(self, y, x='date', start_date='1968-01-01', end_date=datetime.datetime.today().strftime('%Y-%m-%d'),
                 df=None, horiz_line_height=0):
        if df is None:
            df = self.total_data
        subdata = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        fig, ax = plt.subplots(1, 1, figsize=(25, 25))
        for variable in y:
            sns.lineplot(data=subdata, x=x, y=variable, ax=ax)

        # Shade the regions during a recession
        if x == 'date':
            line = ax.get_lines()[-1]
            x_mask, y_mask = line.get_data()
            IRVect = np.vectorize(get_data.inRecession)
            mask = IRVect(x_mask)
            switch_list = []
            for i in range(len(mask)):
                if (((i == 0) & (mask[i] == 1)) |
                        ((i != 0) & (mask[i] != mask[i - 1])) |
                        ((i == len(mask) - 1) & (mask[i] == 1))):
                    switch_list.append(i)

            it = 0
            while it < len(switch_list):
                plt.axvspan(switch_list[it], switch_list[it + 1], color='gray', alpha=0.5, lw=0)
                plt.axvspan(switch_list[it], switch_list[it] - 12, color='yellow', alpha=0.3, lw=0)
                it += 2

        plt.axhline(y=horiz_line_height, color='black', linestyle='--')
        ax.legend(labels=y + ['', 'recession', 'year before recession'])
        return fig

    # Creates a histogram to show the distribution of data for a given feature among different labels
    def histPlot(self, feature, binary):
        cropped_data = self.total_data[self.total_data['in_recession'] == 0]
        fig, ax = plt.subplots(1, 1)
        ax.hist(cropped_data[cropped_data[binary] == 1][feature], alpha=0.5, label='Recession')
        ax.hist(cropped_data[cropped_data[binary] == 0][feature], alpha=0.5, label='No Recession')
        ax.legend()
        ax.set_xlabel('Value')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of ' + feature.replace('_', ' ').title() + ' by ' + binary.replace('_', ' ').title())
        return fig

    # Creates a scatter plot to show the distribution of data for a given feature among a dependent variable
    def scatPlot(self, feature, dependent):
        cropped_data = self.total_data[self.total_data['in_recession'] == 0]
        fig, ax = plt.subplots(1, 1)
        ax.scatter(x=cropped_data[feature], y=cropped_data[dependent])
        ax.set_xlabel(feature.replace('_', ' ').title())
        ax.set_ylabel(dependent.replace('_', ' ').title())
        ax.set_title(
            'Distribution of ' + feature.replace('_', ' ').title() + ' by ' + dependent.replace('_', ' ').title())
        return fig

    def scatPlot2(self, feature, dependent):
        cropped_data = self.total_data[self.total_data['in_recession'] == 0]
        fig = px.scatter(cropped_data, x=feature, y=dependent)
        return fig
