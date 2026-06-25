class PodcastError(Exception):
    pass

class PDFExtractionError(PodcastError):
    pass

class ScriptGenerationError(PodcastError):
    pass

class TTSSubmissionError(PodcastError):
    pass

class TTSTimeoutError(PodcastError):
    pass
