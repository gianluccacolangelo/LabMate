import scraper
import analyzer
import report_generator
from user import User

class CorrespondentAI:
    def __init__(self, llm_api_key):
        self.users = []
        self.scraper = scraper.Scraper()
        self.analyzer = analyzer.Analyzer(llm_api_key)
        self.report_generator = report_generator.ReportGenerator()

    def add_user(self, user):
        self.users.append(user)

    def run_weekly_report(self):
        for user in self.users:
            research_data = self.scraper.scrape_sites(user.sites_of_interest)
            relevant_research = self.analyzer.analyze(research_data, user.interests)
            report = self.report_generator.generate_report(relevant_research, user)
            user.send_report(report)
        return "Weekly reports generated and sent to all users."

if __name__ == "__main__":
    ai = CorrespondentAI()
    # Add users and run the weekly report
    # This is just a placeholder for now
    ai.run_weekly_report()