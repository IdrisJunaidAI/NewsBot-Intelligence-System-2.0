"""Data suitable for Plotly or Chart.js visualization."""
def category_chart_data(df):
    return [{'category':str(k),'count':int(v)} for k,v in df.category.value_counts().items()]
