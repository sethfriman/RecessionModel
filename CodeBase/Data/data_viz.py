# This file will hold methods for visualizing data
import datetime
import plotly.express as px
import CodeBase.Data.get_data as get_data

recession_starts = ['1960-04-01', '1969-12-01', '1973-11-01', '1980-01-01', '1981-07-01',
                    '1990-07-01', '2001-03-01', '2007-12-01', '2020-02-01']
recession_ends = ['1961-02-01', '1970-11-01', '1975-03-01', '1980-07-01', '1982-11-01',
                  '1991-03-01', '2001-11-01', '2009-06-01', '2020-04-01']


class Visualizer:

    def __init__(self, df=None):
        if df is None:
            self.total_data = get_data.get_total_table()
        else:
            self.total_data = df

    def makePlot(self, y, x='date', start_date='1968-01-01', end_date=datetime.datetime.today().strftime('%Y-%m-%d'),
                 df=None, horiz_line_height=0):
        if df is None:
            df = self.total_data
        subdata = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        labels = {x: x.replace('_', ' ').title()}
        for it in y:
            labels[it] = it.replace('_', ' ').title()
        fig = px.line(subdata, x=x, y=y, labels=labels, title='Variable Visualization Chart', )
        # for i in range(1, len(y)):
        #     fig.add_trace(px.line(subdata, x=x, y=y[i]))

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

        fig.add_hline(y=horiz_line_height, line_color='black', line_dash='dash')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        return fig

    # Creates a histogram to show the distribution of data for a given feature among different labels
    def histPlot(self, feature, binary):
        cropped_data = self.total_data[self.total_data['in_recession'] == 0]
        fig = px.histogram(cropped_data, x=feature, color=binary,
                           labels={
                               feature: feature.replace('_', ' ').title(),
                               binary: binary.replace('_', ' ').title()
                           },
                           title='Distribution of ' + feature.replace('_', ' ').title() + ' by ' +
                                 binary.replace('_', ' ').title(), opacity=0.5, barmode="overlay")
        return fig

    # Creates a scatter plot to show the distribution of data for a given feature among a dependent variable
    def scatPlot(self, feature, dependent):
        cropped_data = self.total_data[self.total_data['in_recession'] == 0]
        fig = px.scatter(cropped_data, x=feature, y=dependent,
                         labels={
                             feature: feature.replace('_', ' ').title(),
                             dependent: dependent.replace('_', ' ').title()
                         },
                         title='Distribution of ' + feature.replace('_', ' ').title() + ' by ' +
                               dependent.replace('_', ' ').title())
        return fig
