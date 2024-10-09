class User:
    def __init__(self, name, email, interests, sites_of_interest):
        self.name = name
        self.email = email
        self.interests = interests
        self.sites_of_interest = sites_of_interest

    def send_report(self, report):
        # This method would handle sending the report to the user
        # For now, we'll just print it
        print(f"Sending report to {self.email}:\n{report}")