import logging

from openai import OpenAI

from prompts.prompts import Prompt
from prompts.structured_outputs import CognitiveDistortion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoCoAgent():
    """CoCoAgent is a conversational agent that interacts with users and detects cognitive distortions
    in their dialogue using OpenAI's language model.
    """
    def __init__(self, api_key):
        """
        Initialize the CoCoAgent with the given API key.

        Args:
            api_key (str): The API key for accessing the OpenAI service.
        """
        self.model_name = "gpt-4o-mini"
        self.llm_client = OpenAI(api_key=api_key)
        self.technique_usage_log = list()
        self.chat_history = list()
        logger.info("CoCoAgent initialized with model: %s", self.model_name)

    def response_from_opanai(self, prompt):
        """
        Generate a response from OpenAI for the given prompt.

        Args:
            prompt (str): The prompt to send to OpenAI.

        Returns:
            str: The response from OpenAI.
        """
        logger.info("Generating response from OpenAI for prompt: %s", prompt)
        completion = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        response = completion.choices[0].message.content
        logger.info("Received response: %s", response)
        return response

    def structured_response_from_openai(self, prompt):
        """
        Generate a structured response from OpenAI for the given prompt.

        Args:
            prompt (str): The prompt to send to OpenAI.

        Returns:
            CognitiveDistortion: The structured response from OpenAI.
        """
        logger.info("Generating structured response from OpenAI for prompt: %s", prompt)
        completion = self.llm_client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_format=CognitiveDistortion,
        )
        response = completion.choices[0].message.parsed
        logger.info("Received structured response: %s", response)
        return response

    def chat(self):
        """
        Generate a chat response based on the chat history.

        Returns:
            str: The chat response from OpenAI.
        """
        logger.info("Generating chat response")
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": Prompt.static},
                *self.chat_history
            ],
            temperature=0,
        )
        chat_response = response.choices[0].message.content
        logger.info("Received chat response: %s", chat_response)
        return chat_response

    def log_technique_usage(self, technique):
        """
        Log the usage of a specific technique.

        Args:
            technique (str): The technique to log.
        """
        logger.info("Logging technique usage: %s", technique)
        self.technique_usage_log.append(technique)

    def detect_cognitive_distortion(self, latest_dialogue):
        """
        Detect cognitive distortions in the latest dialogue.

        Args:
            latest_dialogue (str): The latest dialogue from the user.

        Returns:
            CognitiveDistortion: The detected cognitive distortion.
        """
        logger.info("Detecting cognitive distortion for dialogue: %s", latest_dialogue)
        return self.structured_response_from_openai(Prompt.cognitive_distortion_detection(latest_dialogue))
    
    def run(self):
        """
        Start the CoCoAgent run loop, interacting with the user and detecting cognitive distortions.
        """
        logger.info("Starting CoCoAgent run loop")
        while True:
            latest_dialogue = input("User: ")
            self.chat_history.append({"role": "user", "content": latest_dialogue})
            distortion_type = self.detect_cognitive_distortion(latest_dialogue)
            logger.info("Detected cognitive distortion: %s", distortion_type)
            response = self.chat()
            self.chat_history.append({"role": "assistant", "content": response})
            print("Assistant: ", response)
