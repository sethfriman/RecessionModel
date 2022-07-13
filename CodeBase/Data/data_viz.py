# This file will hold methods for visualizing data
import datetime
import plotly.express as px
import CodeBase.Data.get_data as get_data
from plotly.subplots import make_subplots

recession_starts = ['1960-04-01', '1969-12-01', '1973-11-01', '1980-01-01', '1981-07-01',
                    '1990-07-01', '2001-03-01', '2007-12-01', '2020-02-01']
recession_ends = ['1961-02-01', '1970-11-01', '1975-03-01', '1980-07-01', '1982-11-01',
                  '1991-03-01', '2001-11-01', '2009-06-01', '2020-04-01']


class Visualizer:

    def __init__(self, df=None):
        self.total_data = df

    def makePlot(self, y, x='date', start_date='1968-01-01', end_date=datetime.datetime.today().strftime('%Y-%m-%d'),
                 df=None, horiz_line_height=0):
        if df is None:
            df = self.total_data
        subdata = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        labels = {x: x.replace('_', ' ').title()}
        for it in y:
            labels[it] = it.replace('_', ' ').title()
        fig = px.line(subdata, x=x, y=y, labels=labels)
        fig.update_layout(title={"text": "Variable Visualization Chart", "y": 0.9})

        # Shade the regions during a recession
        if x == 'date':
            for i in range(len(recession_starts)):
                if (recession_ends[i] >= subdata.date.values[0]) & (recession_starts[i] <= subdata.date.values[-1]):
                    fig.add_vrect(x0=recession_starts[i], x1=recession_ends[i], line_width=0, fillcolor="gray",
                                  opacity=0.5)
                    year_before_start = recession_starts[i].split('-')
                    year_before_start = str(int(year_before_start[0]) - 1) + '-' + year_before_start[1] + '-' + \
                                        year_before_start[2]
                    fig.add_vrect(x0=year_before_start, x1=recession_starts[i], line_width=0, fillcolor="yellow",
                                  opacity=0.5)
            fig.update_layout(xaxis_title="Date - Gray: Recession, Yellow: Year Before")

        fig.add_hline(y=horiz_line_height, line_color='black', line_dash='dash')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        fig.update_layout(hovermode="x")
        return fig

    # Creates a histogram to show the distribution of data for a given feature among different labels
    def histPlot(self, feature, binary, start_date='1968-01-01',
                 end_date=datetime.datetime.today().strftime('%Y-%m-%d'), in_rec=0):
        if (in_rec is None) | (in_rec == []):
            cropped_data = self.total_data[self.total_data['in_recession'] == 0]
            cropped_data = cropped_data[(cropped_data['date'] >= start_date) & (cropped_data['date'] <= end_date)]
        else:
            cropped_data = self.total_data[(self.total_data['date'] >= start_date) &
                                           (self.total_data['date'] <= end_date)]
        if len(feature) > 1:
            cropped_data = (cropped_data-cropped_data.mean())/cropped_data.std()
            cropped_data['combined_feature'] = cropped_data[feature[0]] * cropped_data[feature[1]]
            for i in range(2, len(feature)):
                cropped_data['combined_feature'] = cropped_data['combined_feature'] * cropped_data[feature[i]]
            to_plot = 'combined_feature'
        else:
            to_plot = feature[0]
        fig = px.histogram(cropped_data, x=to_plot, color=binary,
                           labels={
                               to_plot: to_plot.replace('_', ' ').title(),
                               binary: binary.replace('_', ' ').title()
                           },
                           title='Distribution of ' + to_plot.replace('_', ' ').title() + ' by ' +
                                 binary.replace('_', ' ').title(), opacity=0.5, barmode="overlay")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        return fig

    def soloHist(self, feature, start_date='1968-01-01',
                 end_date=datetime.datetime.today().strftime('%Y-%m-%d'), in_rec=0):
        if (in_rec is None) | (in_rec == []):
            cropped_data = self.total_data[self.total_data['in_recession'] == 0]
            cropped_data = cropped_data[(cropped_data['date'] >= start_date) & (cropped_data['date'] <= end_date)]
        else:
            cropped_data = self.total_data[(self.total_data['date'] >= start_date) &
                                           (self.total_data['date'] <= end_date)]
        fig = px.histogram(cropped_data, x=feature,
                           labels={
                               feature: feature.replace('_', ' ').title()
                           },
                           title='Distribution of ' + feature.replace('_', ' ').title())
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        return fig

    # Creates a scatter plot to show the distribution of data for a given feature among a dependent variable
    def scatPlot(self, y, x, start_date='1968-01-01', end_date=datetime.datetime.today().strftime('%Y-%m-%d'),
                 in_rec=0):
        if (in_rec is None) | (in_rec == []):
            cropped_data = self.total_data[self.total_data['in_recession'] == 0]
            cropped_data = cropped_data[(cropped_data['date'] >= start_date) & (cropped_data['date'] <= end_date)]
        else:
            cropped_data = self.total_data[(self.total_data['date'] >= start_date) &
                                           (self.total_data['date'] <= end_date)]

        labels = {x: x.replace('_', ' ').title()}

        fig = px.scatter(cropped_data, x=x, y=y,
                         labels=labels)
        fig.update_layout(title={"text": "Variable Visualization Chart", "y": 0.9})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        fig.add_hline(y=0, line_color='black', line_dash='dash')
        return fig
