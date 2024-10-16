from app.fetchers.pdf_handling import PdfReader
from app.composers.thinkers import TechnicalComposer, PhilosopherComposer, FirstPrinciplesComposer, HistoryOfScienceComposer, MailComposer, ComposerContext


def main():
    # Create a PdfReader instance
    pdf_reader = PdfReader()

    # Read the PDF file
    print("Reading the PDF file")
    pdf_content = pdf_reader.read("https://www.biorxiv.org/content/10.1101/2023.12.12.571272v3.full.pdf")
    print(f"PDF file read: {pdf_content[:100]} (...)")
    user_interests = "I'm interested in neuroscience, dynamic systems, and topology."

    technical_composer = TechnicalComposer()
    philosopher_composer = PhilosopherComposer()
    first_principles_composer = FirstPrinciplesComposer()
    history_of_science_composer = HistoryOfScienceComposer()
    mail_composer = MailComposer()

    technical_analysis = technical_composer.compose(pdf_content, user_interests,temperature=0.0)
    print(f'technical_analysis: {technical_analysis}')   
    philosopher_analysis = philosopher_composer.compose(pdf_content, user_interests,temperature=1.0)
    print(f'philosopher_analysis: {philosopher_analysis}')
    first_principles_analysis = first_principles_composer.compose(pdf_content, user_interests,temperature=2.0)
    print(f'first_principles_analysis: {first_principles_analysis}')
    history_of_science_analysis = history_of_science_composer.compose(pdf_content, user_interests,temperature=1.0)
    print(f'history_of_science_analysis: {history_of_science_analysis}')
    mail = mail_composer.compose(pdf_content, technical_analysis, philosopher_analysis, first_principles_analysis, history_of_science_analysis, user_interests,temperature=2.0)

    print(f'\n\n##MAIL:\n\n {mail}')

if __name__ == "__main__":
    main()



