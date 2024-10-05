#import openai  # or any other LLM provider you prefer

class Analyzer:
    def __init__(self, api_key):
        self.llm_provider = openai  # or another LLM provider
        self.llm_provider.api_key = api_key

    def analyze(self, research_data, interests):
        relevant_research = []
        for data in research_data:
            relevance_score = self._check_relevance(data, interests)
            if relevance_score > 0.7:  # Adjust threshold as needed
                relevant_research.append({
                    'data': data,
                    'relevance_score': relevance_score
                })
        return sorted(relevant_research, key=lambda x: x['relevance_score'], reverse=True)

    def _check_relevance(self, data, interests):
        prompt = f"""
        Given the following research data and user interests, rate the relevance on a scale of 0 to 1:

        Research data: {data}

        User interests: {', '.join(interests)}

        Provide only a number between 0 and 1 as the response, where 1 is highly relevant and 0 is not relevant at all.
        """

        response = self.llm_provider.Completion.create(
            engine="text-davinci-002",  # or another appropriate engine
            prompt=prompt,
            max_tokens=1,
            n=1,
            stop=None,
            temperature=0.5,
        )

        try:
            relevance_score = float(response.choices[0].text.strip())
            return max(0, min(relevance_score, 1))  # Ensure the score is between 0 and 1
        except ValueError:
            return 0  # Default to 0 if we can't parse the response
