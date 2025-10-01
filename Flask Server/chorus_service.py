from llm_service import LLMService
from typing import List, Dict
import json

class ChorusService:
    def __init__(self):
        self.llm_service = LLMService()
    
    def run_chorus(self, user_query: str, context: str, responder_llms: List[Dict], evaluator_llms: List[Dict], status_callback=None) -> Dict:
        """
        Run the Chorus model:
        1. Get responses from all responder LLMs
        2. Have evaluator LLMs vote on the best response
        3. Return the most voted response
        
        responder_llms: [{"provider": "openai", "model": "gpt-4"}]
        evaluator_llms: [{"provider": "anthropic", "model": "claude-3-sonnet"}]
        """
        
        # Step 1: Get responses from all responder LLMs
        print(f"Getting responses from {len(responder_llms)} responder LLMs...")
        responses = []
        
        for i, llm_config in enumerate(responder_llms):
            if status_callback:
                status_callback(f'Getting response from responder {i + 1}/{len(responder_llms)}...')
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the user's question."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"}
            ]
            
            response = self.llm_service.call_llm(
                provider=llm_config['provider'],
                model=llm_config['model'],
                messages=messages
            )
            
            responses.append({
                'index': i,
                'provider': llm_config['provider'],
                'model': llm_config['model'],
                'response': response
            })
            
            if status_callback:
                status_callback(f'Received response from {llm_config["provider"]} {llm_config["model"]}')
        
        # If only one responder, return it directly
        if len(responses) == 1:
            return {
                'final_response': responses[0]['response'],
                'responses': responses,
                'votes': None,
                'winner_index': 0
            }
        
        # Step 2: Have evaluators vote on the best response
        print(f"Getting votes from {len(evaluator_llms)} evaluator LLMs...")
        if status_callback:
            status_callback(f'Evaluating responses with {len(evaluator_llms)} evaluator(s)...')
        votes = []
        
        # Format responses for evaluation
        responses_text = "\n\n".join([
            f"Response {r['index']} (from {r['provider']} {r['model']}):\n{r['response']}"
            for r in responses
        ])
        
        for idx, evaluator in enumerate(evaluator_llms):
            if status_callback:
                status_callback(f'Getting vote from evaluator {idx + 1}/{len(evaluator_llms)}...')
            
            evaluation_prompt = f"""You are an expert evaluator. Below are {len(responses)} different responses to the same question.

Question: {user_query}

{responses_text}

Evaluate all responses and select the BEST one based on:
- Accuracy and relevance to the question
- Use of provided context
- Clarity and completeness
- Helpfulness

Respond with ONLY the number (index) of the best response. Just the number, nothing else."""

            messages = [
                {"role": "system", "content": "You are an expert response evaluator."},
                {"role": "user", "content": evaluation_prompt}
            ]
            
            vote = self.llm_service.call_llm(
                provider=evaluator['provider'],
                model=evaluator['model'],
                messages=messages,
                temperature=0.3
            )
            
            # Extract vote number
            try:
                vote_index = int(vote.strip())
                if 0 <= vote_index < len(responses):
                    votes.append({
                        'evaluator': f"{evaluator['provider']} {evaluator['model']}",
                        'vote': vote_index
                    })
                    if status_callback:
                        status_callback(f'{evaluator["provider"]} {evaluator["model"]} voted for Response {vote_index + 1}')
            except:
                print(f"Invalid vote received: {vote}")
        
        # Step 3: Count votes and determine winner
        vote_counts = {}
        for vote in votes:
            vote_index = vote['vote']
            vote_counts[vote_index] = vote_counts.get(vote_index, 0) + 1
        
        # Get winner (response with most votes)
        if vote_counts:
            winner_index = max(vote_counts, key=vote_counts.get)
        else:
            # Fallback: return first response if no valid votes
            winner_index = 0
        
        return {
            'final_response': responses[winner_index]['response'],
            'responses': responses,
            'votes': votes,
            'vote_counts': vote_counts,
            'winner_index': winner_index
        }

