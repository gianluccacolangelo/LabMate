class PaperScraper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PaperScraper, cls).__new__(cls)
        return cls._instance

    def fetch_papers(self):
        bioRxiv_papers = BioRxivAPIAdapter().fetch()
        arXiv_papers = arXivAPIAdapter().fetch()
        return bioRxiv_papers + arXiv_papers