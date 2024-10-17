from app.composers.analizer import PaperAnalyzerFactory
from app.fetchers.pdf_handling import PdfReader
from app.composers.thinkers import (
    TechnicalComposer, PhilosopherComposer, FirstPrinciplesComposer,
    HistoryOfScienceComposer, MailComposer
)

import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Configuration
    config = {
        'data_dir': 'data',
        'vector_dimension': 768,
        'gemini_api_key': os.getenv('API_KEY'),
        'bert_model_name': 'BAAI/bge-base-en-v1.5',
        'index_file': 'bge_vector_database_faiss_index_20241015.bin',
        'metadata_file': 'bge_vector_database_metadata_20241015.pkl',
        'top_k': 20 
    }

    # Create factory
    factory = PaperAnalyzerFactory(config)

    # Get analyzer and vectorizer
    analyzer = factory.analyzer()
    vectorizer = factory.create_vectorizer()

    # Example usage
    user_interests = """
Our group aims to further our understanding of the human genome by computational integration of large-scale functional and comparative genomics datasets. (1) We use comparative genomics of multiple related species to recognize evolutionary signatures of protein-coding genes, RNA structures, microRNAs, regulatory motifs, and individual regulatory elements. (2) We use combinations of epigenetic modifications to define chromatin states associated with distinct functions, including promoter, enhancer, transcribed, and repressed regions, each with distinct functional properties. (3) We use dynamics of functional elements across many cell types to link regulatory regions to their target genes, predict activators and repressors, and cell type specific regulatory action. (4) We combine these evolutionary, chromatin, and activity signatures to dramatically expand the annotation of the non-coding genome, elucidate the regulatory circuitry of the human and fly genomes, and to revisit previously uncharacterized disease-associated variants, providing mechanistic insights into their likely molecular roles
"""


    vectorized_user_interests = vectorizer.vectorize_text(user_interests)

    # Analyze papers
    chosen_papers = analyzer.analyze_papers(vectorized_user_interests, user_interests)

    # Select the first paper for detailed analysis
    if chosen_papers:
        selected_paper = chosen_papers[0]
        pdf_url = selected_paper['pdf_url']
        
        # Create a PdfReader instance and read the PDF
        pdf_reader = PdfReader()
        print(f"Reading the PDF file: {pdf_url}")
        pdf_content = pdf_reader.read(pdf_url)
        print(f"PDF file read: {pdf_content[:100]} (...)")

        # Initialize composers with specific LLM providers and settings
        technical_composer = TechnicalComposer("gemini", temperature=0.0)
        philosopher_composer = PhilosopherComposer("gemini", temperature=1.0)
        first_principles_composer = FirstPrinciplesComposer("gemini", temperature=1.0)
        history_of_science_composer = HistoryOfScienceComposer("gemini", temperature=1.0)
        mail_composer = MailComposer("gemini", temperature=0.5)

        # Perform analyses
        technical_analysis = technical_composer.compose(pdf_content, user_interests)
        philosopher_analysis = philosopher_composer.compose(pdf_content, user_interests)
        first_principles_analysis = first_principles_composer.compose(pdf_content, user_interests)
        history_of_science_analysis = history_of_science_composer.compose(pdf_content, user_interests)

        # Generate final mail
        mail = mail_composer.compose(
            pdf_content, technical_analysis, philosopher_analysis,
            first_principles_analysis, history_of_science_analysis,
            user_interests
        )

        # Print results
        print("\n--- Analysis Results ---")
        print(f"Technical Analysis: {technical_analysis[:100]}...")
        print(f"Philosopher Analysis: {philosopher_analysis[:100]}...")
        print(f"First Principles Analysis: {first_principles_analysis[:100]}...")
        print(f"History of Science Analysis: {history_of_science_analysis[:100]}...")
        print(f"\n--- Final Mail ---\n{mail}")
    else:
        print("No papers were found matching the user's interests.")

if __name__ == "__main__":
    main()
