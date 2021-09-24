def per_lesson_stats(df, metric=None)

    """

    Returns a dataframe containing the desired statistic.

    df =  per_lesson_stats(df, metric=metric_string)


    Args:

    * df (pandas dataframe):
    is a dataframe containing the lesson data from a single day.

     i.e. df = pd.read_csv(path_to_lessons + lesson_file_name, index_col=0)


    Kwargs:
    * metric_string (string):
    a string specififying the analysis.  one of "sentiment", ...

    Returns:

    dataframe containing the desired statistics
   

    """
 

    if metric=="sentiment":


        has_sentiment = df.columns.str.startswith('n_')
        cols = df.columns[has_sentiment]

        sentiment_values = df[cols].sum()
        sentiment_values.name = 'number of responses'
        sentiment_values = sentiment_values.to_frame()
        sentiment_values['avg per student'] = sentiment_values/df.shape[0]


        return sentiment_values
