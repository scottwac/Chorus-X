from openai import OpenAI
from anthropic import Anthropic
from groq import Groq
import os
import base64

class LLMService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def classify_user_intent(self, user_message: str) -> str:
        """
        Use GPT-5 to classify user intent
        Returns: 'text', 'find_image', or 'generate_image'
        """
        try:
            classification_prompt = f"""You are an intent classifier. Analyze the user's message and determine their intent.

User message: "{user_message}"

Classify the intent as ONE of these:
1. "text" - User wants a text-based answer or conversation
2. "find_image" - User wants to find/retrieve an existing image from a dataset (e.g., "show me the chart", "find the diagram", "what images do we have")
3. "generate_image" - User wants to create/generate a new image (e.g., "create an image of", "generate a picture", "draw me")

Respond with ONLY the classification word: text, find_image, or generate_image"""

            response = self.openai_client.chat.completions.create(
                model="gpt-5-2025-08-07",
                messages=[
                    {"role": "system", "content": "You are a precise intent classifier. Respond with only one word: text, find_image, or generate_image."},
                    {"role": "user", "content": classification_prompt}
                ]
            )
            
            intent = response.choices[0].message.content.strip().lower()
            
            # Validate response
            if intent in ['text', 'find_image', 'generate_image']:
                return intent
            else:
                # Default to text if unclear
                return 'text'
                
        except Exception as e:
            print(f"Error classifying intent: {e}")
            # Default to text on error
            return 'text'
    
    def call_llm(self, provider: str, model: str, messages: list, temperature: float = 0.7) -> str:
        """
        Universal LLM caller
        provider: 'openai', 'anthropic', or 'groq'
        model: model name
        messages: list of message dicts
        """
        try:
            if provider == 'openai':
                return self._call_openai(model, messages, temperature)
            elif provider == 'anthropic':
                return self._call_anthropic(model, messages, temperature)
            elif provider == 'groq':
                return self._call_groq(model, messages, temperature)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            print(f"Error calling {provider}: {e}")
            return f"Error: {str(e)}"
    
    def _call_openai(self, model: str, messages: list, temperature: float) -> str:
        # GPT-5 models don't support custom temperature values
        params = {
            "model": model,
            "messages": messages
        }
        
        # Only add temperature for models that support it
        if not model.startswith('gpt-5'):
            params["temperature"] = temperature
        
        response = self.openai_client.chat.completions.create(**params)
        return response.choices[0].message.content
    
    def _call_anthropic(self, model: str, messages: list, temperature: float) -> str:
        # Convert messages format for Anthropic
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                claude_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=claude_messages
        )
        return response.content[0].text
    
    def _call_groq(self, model: str, messages: list, temperature: float) -> str:
        response = self.groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def generate_image_description(self, image_path: str) -> str:
        """Use GPT-4o (with vision) to generate image descriptions"""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail. Include all visible elements, text, colors, composition, and context."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating image description: {e}")
            return f"Image description unavailable: {str(e)}"

