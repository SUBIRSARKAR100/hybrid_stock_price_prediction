from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment_score(text_list):
    """
    Calculates average sentiment score for a list of headlines.
    Normalized to [0, 1] range to align with FinBERT behavior in the notebook.
    """
    if not text_list:
        return 0.5, "Neutral"
    
    scores = []
    for text in text_list:
        vs = analyzer.polarity_scores(text)
        scores.append(vs['compound'])
    
    avg_compound = sum(scores) / len(scores)
    # Normalize from [-1, 1] to [0, 1]
    normalized_score = (avg_compound + 1.0) / 2.0
    
    if normalized_score > 0.51:
        label = "Positive"
    elif normalized_score < 0.49:
        label = "Negative"
    else:
        label = "Neutral"
        
    return normalized_score, label
