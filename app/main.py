from app.composers.analizer import PaperAnalyzerFactory

def main():
    # Configuration
    config = {
        'data_dir': 'data',
        'vector_dimension': 768,
        'gemini_api_key': 'your api key here',
        'bert_model_name': 'bert-base-uncased'
    }

    # Create factory
    factory = PaperAnalyzerFactory(config)

    # Get analyzer and vectorizer
    analyzer = factory.analyzer()
    vectorizer = factory.create_vectorizer()

    # Example usage

    user_interests = """ The complexity of aging and age-related diseases remains one of the most profound challenges in biomedical research. Recent advances in high-throughput sequencing technologies have revealed that non-coding regions of the genome, comprising regulatory elements, enhancers, and long non-coding RNAs (lncRNAs), play a significant role in modulating gene expression and cellular pathways related to disease progression and the aging process. However, deciphering these vast, uncharted territories requires sophisticated computational techniques. In this paper, we present a deep learning framework to integrate multi-omics data and uncover the functional relevance of non-coding regions in disease and aging mechanisms.

Our approach employs deep neural networks (DNNs) to fuse data from multiple omics layers, including genomics, transcriptomics, epigenomics, and proteomics, with a focus on interpreting the regulatory impact of non-coding variants. By training the model on large-scale datasets, such as The Cancer Genome Atlas (TCGA) and the Genotype-Tissue Expression (GTEx) project, we identify non-coding elements that correlate with age-related phenotypes and disease susceptibility. The model incorporates feature selection techniques to prioritize regions of interest, such as promoters, enhancers, and non-coding RNAs, that exhibit significant regulatory influence on key aging-related pathways, including inflammation, senescence, and cellular stress responses.

Experimental validation in in vitro and in vivo aging models confirms that several non-coding regulatory elements, particularly lncRNAs and enhancer RNAs (eRNAs), modulate gene networks involved in metabolic regulation, immune response, and tissue regeneration. Additionally, the application of attention mechanisms in the deep learning model enables the identification of specific non-coding mutations associated with age-related diseases such as cancer, neurodegeneration, and cardiovascular disease.

Our results underscore the potential of deep learning to disentangle the complex regulatory roles of non-coding regions in the genome, providing insights into novel therapeutic targets for combating aging and its associated diseases. This study highlights the importance of integrating multi-omics data to gain a comprehensive understanding of genome regulation beyond coding regions, offering a path forward in personalized medicine and anti-aging interventions.

Keywords: Deep Learning, Multi-Omics, Non-Coding Regions, Aging, Disease, lncRNA, Enhancers, Epigenomics, Regulatory Networks, Genome-Wide Association Studies (GWAS), Cancer, Neurodegeneration.
"""
    

    vectorized_user_interests = vectorizer.vectorize_text(user_interests)

    # Analyze papers
    chosen_papers = analyzer.analyze_papers(vectorized_user_interests, user_interests)

    # Print results
    print("Chosen papers:")
    for paper in chosen_papers:
        print(f"- {paper['id']}: {paper['abstract'][:1000]}...")  # Print first 100 characters of abstract

if __name__ == "__main__":
    main()
