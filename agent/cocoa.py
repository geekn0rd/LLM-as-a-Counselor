import json
import logging

from openai import OpenAI

from prompts.prompts import CBTPrompt
from prompts.structured_outputs import CognitiveDistortion, DialogueResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)


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
        self.technique_usage = list()
        self.chat_history = list()
        self.basic_memory = list()
        self.cd_memory = list()

        CBTPrompt.load_cbt_doc()
        # logger.info("CoCoAgent initialized with model: %s", self.model_name)

    def response_from_opanai(self, prompt: str) -> str:
        """
        Generate a response from OpenAI for the given prompt.

        Args:
            prompt (str): The prompt to send to OpenAI.

        Returns:
            str: The response from OpenAI.
        """
        # logger.info("Generating response from OpenAI for prompt: %s", prompt)
        completion = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        response = completion.choices[0].message.content
        # logger.info("Received response: %s", response)
        return response

    def structured_response_from_openai(self, prompt):
        """
        Generate a structured response from OpenAI for the given prompt.

        Args:
            prompt (str): The prompt to send to OpenAI.

        Returns:
            CognitiveDistortion: The structured response from OpenAI.
        """
        # logger.info("Generating structured response from OpenAI for prompt: %s", prompt)
        completion = self.llm_client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_format=CognitiveDistortion,
        )
        response = completion.choices[0].message.parsed
        # logger.info("Received structured response: %s", response)
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
                {"role": "system", "content": CBTPrompt.static},
                *self.chat_history
            ],
            temperature=0,
        )
        chat_response = response.choices[0].message.content
        # logger.info("Received chat response: %s", chat_response)
        return chat_response

    def log_technique(self, technique):
        """
        Log the usage of a specific technique.

        Args:
            technique (str): The technique to log.
        """
        # logger.info("Logging technique usage: %s", technique)
        self.technique_usage.append(technique)

    def detect_cognitive_distortion(self, latest_dialogue):
        """
        Detect cognitive distortions in the latest dialogue.

        Args:
            latest_dialogue (str): The latest dialogue from the user.

        Returns:
            CognitiveDistortion: The detected cognitive distortion.
        """
        return self.structured_response_from_openai(CBTPrompt.cognitive_distortion_detection(latest_dialogue))

    def select_cbt_stage(self, technique: str, progress: str, latest_dialogue: str):
        """
        Select the CBT stage based on the detected cognitive distortion.

        Returns:
            str: The selected CBT stage.
        """
        return self.response_from_opanai(CBTPrompt.stage_selection(technique=technique, progress=progress, technique_usage_log=self.technique_usage, latest_dialogue=latest_dialogue))

    def extract_insight(self, latest_dialogue):
        """
        Extract insights from the latest dialogue.

        Args:
            latest_dialogue (str): The latest dialogue from the user.

        Returns:
            str: The extracted insights.
        """
        return self.response_from_opanai(CBTPrompt.extract_insight(latest_dialogue))

    def select_cbt_technique(self, distortion_type):
        """
        Select the CBT technique to employ based on the detected cognitive distortion.

        Returns:
            str: The selected CBT technique.
        """
        return self.response_from_opanai(CBTPrompt.technique_selection(distortion_type=distortion_type, memory=self.chat_history))

    def run(self):
        """
        Start the CoCoAgent run loop, interacting with the user and detecting cognitive distortions.
        """
        logger.info("Starting CoCoAgent run loop")
        while True:
            logger.info("chat_history: %s", self.chat_history)
            logger.info("technique_usage %s: ", self.technique_usage)
            latest_dialogue = input("User: ")
            self.chat_history.append(
                {"role": "user", "content": latest_dialogue})

            distortion_type = self.detect_cognitive_distortion(latest_dialogue)
            logger.info("Detected cognitive distortion: %s", distortion_type)

            cbt_technique = self.select_cbt_technique(distortion_type)
            logger.info("Selected CBT technique: %s", cbt_technique)

            cbt_stage = self.select_cbt_stage(
                technique=cbt_technique, progress="", latest_dialogue=self.chat_history)
            logger.info("Selected CBT stage: %s", cbt_stage)

            response = self.response_from_opanai(prompt=CBTPrompt.final(
                latest_dialogue=self.chat_history,
                technique=cbt_technique,
                cbt_documentation="",
                stage_example="",
                stage=cbt_stage)
            )
            self.chat_history.append(
                {"role": "assistant", "content": response})
            self.log_technique(cbt_technique)
            print("Assistant: ", response)

    async def process_dialogue(self, client_utterance: str) -> str:
        """
        Process a single dialogue message and return structured response.

        Args:
         client_utterance (str): The latest dialogue from the user.

        Returns:
            DialogueResponse: Structured response containing the assistant's reply and metadata
        """
        self.chat_history.append(
            {"role": "user", "content": client_utterance}
        )

        latest_dialogue = ''.join([json.dumps(item)
                                  for item in self.chat_history[-2:]])

        cognitive_distortion = self.detect_cognitive_distortion(
            latest_dialogue)
        logger.info("Detected cognitive distortion: %s", cognitive_distortion)
        if cognitive_distortion.distortion_type != "None":
            self.cd_memory.append(cognitive_distortion)

        utterence_insight = self.extract_insight(latest_dialogue)
        logger.info("Extracted insight: %s", utterence_insight)
        if utterence_insight != "None":
            self.basic_memory.append(utterence_insight)

        cbt_technique = self.select_cbt_technique(cognitive_distortion)
        logger.info("Selected CBT technique: %s", cbt_technique)

        cbt_stage = self.select_cbt_stage(
            technique=cbt_technique,
            progress="",
            latest_dialogue=self.chat_history
        )
        logger.info("Selected CBT stage: %s", cbt_stage)

        response = self.response_from_opanai(
            prompt=CBTPrompt.final(
                latest_dialogue=self.chat_history,
                technique=cbt_technique,
                cbt_documentation="",
                stage_example="",
                stage=cbt_stage
            )
        )

        self.chat_history.append(
            {"role": "assistant", "content": response}
        )
        self.log_technique(cbt_technique)

        return response
