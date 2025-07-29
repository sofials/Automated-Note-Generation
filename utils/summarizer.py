from transformers import pipeline

def load_summarizer(model_name="t5-base"):
    """
    Carica il modello AI per la sintesi del testo.
    """
    return pipeline("summarization", model=model_name)

def summarize_chunks(chunks, summarizer, max_length=100, min_length=30):
    """
    Riassume ciascun blocco di testo con il modello.
    """
    summaries = []
    for i, chunk in enumerate(chunks):
        output = summarizer(
            chunk,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        summaries.append(output[0]['summary_text'])
    return summaries
