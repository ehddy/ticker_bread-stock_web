import pandas as pd
import numpy as np
import plotly.express as px

class viz:
    def single_line_chart(self, data, x, y):
        fig = px.line(data, x=x, y=y)

        return fig
    
    def multi_line_chart(self, data, x, y, col):
        fig = px.line(data, x=x, y=y, color=col)

        return fig