import os
from typing import Any, Iterator, Optional
import requests
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import GenerationChunk
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib3.exceptions import InsecureRequestWarning
import ssl

from utils.env import get_chat_brd_cert_pem

class ChatBRD(LLM):
    def __init__(self, username: str, secret_key: str, base_url: str, chatbot_pk: str, chatbot_sk: str):
        super(ChatBRD, self).__init__()
        self._username = username
        self._secret_key = secret_key

        self._chatbot_pk = chatbot_pk
        self._chatbot_sk = chatbot_sk
        self._access_cookie = None
        self._base_url = base_url
        self._timeout = 60

        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Create a custom SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Create a session
        self._session = requests.Session()

        # Configure retries
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

        # Configure the adapter with the retry strategy and SSL context
        adapter = HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100)
        adapter.ssl_context = ssl_context

        # Mount the adapter to the session
        self._session.mount('https://', adapter)
        
        cert_path = os.path.join(os.getcwd(), get_chat_brd_cert_pem())
        if os.path.isfile(cert_path):
            self._verify = cert_path
        else:
            self._verify = False

    def _get_access_cookie(self, force_new_access_token: bool = False):
        if force_new_access_token or self._access_cookie is None:
            response = self._session.post(
                f'{self._base_url}/api/api/tokens',
                json={
                    'username': self._username,
                    'secret_key': self._secret_key
                },
                timeout=self._timeout,
                verify=self._verify,
            )

            response.raise_for_status()

            self._access_cookie = response.json()

        return self._access_cookie
    
    def call_with_retry(self, prompt: str, force_new_access_token: bool = False):
        cookies = self._get_access_cookie(force_new_access_token)

        response = self._session.post(
            f'{self._base_url}/api/chatbot/{self._chatbot_pk}/{self._chatbot_sk}/query',
            json={"query": prompt},
            cookies=cookies,
            timeout=self._timeout,
            verify=self._verify,
        )

        if not force_new_access_token and not response.ok:
            return self.call_with_retry(prompt, True)

        response.raise_for_status()
        
        result = response.json()

        return result
        
    def _call(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
                If stop tokens are not supported consider raising NotImplementedError.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string.
        """
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        

        response = self.call_with_retry(prompt)

        return response
    
    def _stream(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the LLM on the given prompt.

        This method should be overridden by subclasses that support streaming.

        If not implemented, the default behavior of calls to stream will be to
        fallback to the non-streaming version of the model and return
        the output as a single chunk.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of these substrings.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            An iterator of GenerationChunks.
        """
        ValueError("stream is not permitted.")
        
    @property
    def _identifying_params(self) -> dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "ChatBRD",
            
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "ChatBRD"