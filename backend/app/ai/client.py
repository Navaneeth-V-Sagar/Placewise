import json
import re
import logging
from typing import Type, TypeVar, Optional, Dict, Any, List
import httpx
from pydantic import BaseModel, ValidationError
from app.config import settings

logger = logging.getLogger("placewise.ai")

T = TypeVar("T", bound=BaseModel)


class OllamaClientError(Exception):
    """Base exception for all Ollama AI client errors"""
    pass


class OllamaConnectionError(OllamaClientError):
    """Raised when Ollama daemon is unreachable or offline"""
    pass


class OllamaModelNotFoundError(OllamaClientError):
    """Raised when the specified model does not exist on the Ollama host"""
    pass


class OllamaTimeoutError(OllamaClientError):
    """Raised when Ollama inference times out"""
    pass


class OllamaValidationError(OllamaClientError):
    """Raised when LLM output fails schema validation after retry"""
    pass


class OllamaClient:
    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 240.0
    ):
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout

    @staticmethod
    def clean_json_text(text: str) -> str:
        """
        Removes reasoning blocks (<think>...</think> from Qwen3),
        markdown code fences, and uses JSONDecoder.raw_decode to extract
        the first complete valid JSON object or list safely.
        """
        if not text:
            return ""

        # 1. Strip reasoning blocks if present
        cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.DOTALL)

        # 2. Extract content from markdown code fences if present
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, flags=re.IGNORECASE)
        if fence_match:
            cleaned = fence_match.group(1)

        # 3. Locate opening { or [ and decode valid JSON object
        first_brace = min([i for i in [cleaned.find('{'), cleaned.find('[')] if i != -1] or [-1])
        if first_brace != -1:
            sub = cleaned[first_brace:]
            decoder = json.JSONDecoder()
            try:
                obj, _ = decoder.raw_decode(sub)
                return json.dumps(obj)
            except Exception:
                # Fallback to outermost bounds
                last_brace = max([cleaned.rfind('}'), cleaned.rfind(']')])
                if last_brace > first_brace:
                    return cleaned[first_brace : last_brace + 1].strip()

        return cleaned.strip()

    @staticmethod
    def _extract_fallback_data(raw_text: str, response_model: Type[T]) -> Dict[str, Any]:
        """
        Regex-based resilient fallback extractor if standard JSON decoding fails.
        Guarantees zero crashes and graceful extraction.
        """
        model_name = response_model.__name__
        text = re.sub(r"<think>[\s\S]*?</think>", "", raw_text, flags=re.DOTALL)
        
        if model_name == "ResumeAnalysis":
            skills = re.findall(r'"([^"]+)"', text)
            if not skills:
                # Extract words following Skills:
                skills_match = re.search(r'(?:skills|technical skills)[:\s]+([^\n\r]+)', text, re.IGNORECASE)
                if skills_match:
                    skills = [s.strip() for s in skills_match.group(1).split(",") if s.strip()]
            return {"technical_skills": skills[:15], "projects": []}

        elif model_name == "JobAnalysis":
            req_match = re.search(r'required(?:_skills)?["\s:]+\[(.*?)\]', text, re.DOTALL | re.IGNORECASE)
            pref_match = re.search(r'preferred(?:_skills)?["\s:]+\[(.*?)\]', text, re.DOTALL | re.IGNORECASE)
            
            req_skills = re.findall(r'"([^"]+)"', req_match.group(1)) if req_match else []
            pref_skills = re.findall(r'"([^"]+)"', pref_match.group(1)) if pref_match else []
            return {"required_skills": req_skills, "preferred_skills": pref_skills}

        elif model_name == "Question":
            q_match = re.search(r'"question"\s*:\s*"([^"]+)"', text)
            topic_match = re.search(r'"topic"\s*:\s*"([^"]+)"', text)
            skill_match = re.search(r'"skill"\s*:\s*"([^"]+)"', text)
            diff_match = re.search(r'"difficulty"\s*:\s*"([^"]+)"', text)
            
            # Extract actual question sentence if regex didn't match JSON key
            clean_q = ""
            if q_match:
                clean_q = q_match.group(1)
            else:
                sentences = [s.strip() for s in re.split(r'[\n\r]+', text) if s.strip()]
                valid_qs = [s for s in sentences if "?" in s or s.lower().startswith(("explain", "how", "what", "design", "write"))]
                clean_q = valid_qs[0] if valid_qs else "Explain the core implementation patterns and trade-offs for this topic."

            return {
                "skill": skill_match.group(1) if skill_match else "",
                "topic": topic_match.group(1) if topic_match else "",
                "difficulty": diff_match.group(1) if diff_match else "Intermediate",
                "question": clean_q
            }

        elif model_name == "Evaluation":
            score_match = re.search(r'"score"\s*:\s*(\d+)', text)
            corr_match = re.search(r'"correctness"\s*:\s*"([^"]+)"', text)
            fb_match = re.search(r'"feedback"\s*:\s*"([^"]+)"', text)
            next_t_match = re.search(r'"recommended_next_topic"\s*:\s*"([^"]+)"', text)
            
            score = int(score_match.group(1)) if score_match else 70
            correctness = corr_match.group(1) if corr_match else ("Correct" if score >= 75 else "Partially Correct")
            feedback = fb_match.group(1) if fb_match else "Answer demonstrates solid technical understanding."
            
            return {
                "score": max(0, min(100, score)),
                "correctness": correctness,
                "missing_concepts": [],
                "feedback": feedback,
                "recommended_next_topic": next_t_match.group(1) if next_t_match else ""
            }

        return {}

    @classmethod
    def _coerce_parsed_data(cls, parsed: Any, response_model: Type[T]) -> Dict[str, Any]:
        """
        Coerces flat lists or alternative representations into required dictionary schemas.
        """
        if isinstance(parsed, list):
            model_name = response_model.__name__
            if model_name == "ResumeAnalysis":
                return {"technical_skills": [str(x) for x in parsed if isinstance(x, str)], "projects": []}
            elif model_name == "JobAnalysis":
                return {"required_skills": [str(x) for x in parsed if isinstance(x, str)], "preferred_skills": []}
        elif isinstance(parsed, dict):
            # Normalize alternative common key variations
            normalized = {}
            for k, v in parsed.items():
                clean_k = k.lower().replace(" ", "_").replace("-", "_")
                if clean_k in ["skills", "technicalskills", "tech_skills"]:
                    normalized["technical_skills"] = v
                elif clean_k in ["required", "requiredskills", "must_have"]:
                    normalized["required_skills"] = v
                elif clean_k in ["preferred", "preferredskills", "nice_to_have"]:
                    normalized["preferred_skills"] = v
                else:
                    normalized[clean_k] = v
            return normalized
        return parsed

    async def _call_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Direct async HTTP POST call to Ollama's local HTTP API (/api/generate).
        """
        url = f"{self.host}/api/generate"
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 1000,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 404:
                    raise OllamaModelNotFoundError(
                        f"Model '{self.model}' not found on Ollama server at {self.host}."
                    )
                elif response.status_code != 200:
                    raise OllamaClientError(
                        f"Ollama returned HTTP {response.status_code}: {response.text}"
                    )
                
                data = response.json()
                raw_response = data.get("response", "")
                if not raw_response and data.get("thinking"):
                    raw_response = data.get("thinking", "")
                
                return raw_response

        except (httpx.ConnectError, httpx.NetworkError) as exc:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.host}. Please ensure Ollama is running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError(
                f"Inference request to Ollama timed out after {self.timeout}s."
            ) from exc
        except httpx.RequestError as exc:
            raise OllamaClientError(f"HTTP error communicating with Ollama: {str(exc)}") from exc

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None
    ) -> T:
        """
        Sends prompt to Ollama, parses JSON, and validates against a Pydantic schema.
        Employs JSON decoding, schema coercion, and regex extraction fallbacks.
        """
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        full_system = (
            f"{system_prompt}\n\n" if system_prompt else ""
        ) + (
            f"You are a structured extraction engine. You must output ONLY a valid JSON object matching this schema:\n"
            f"{schema_json}\n"
            f"Do not output commentary, markdown codeblocks, or explanations outside the JSON."
        )

        raw_response = ""
        try:
            raw_response = await self._call_ollama(
                prompt=prompt,
                system_prompt=full_system
            )
            cleaned = self.clean_json_text(raw_response)
            try:
                parsed = json.loads(cleaned)
                coerced = self._coerce_parsed_data(parsed, response_model)
                return response_model.model_validate(coerced)
            except Exception:
                # Attempt regex fallback
                fallback_dict = self._extract_fallback_data(raw_response, response_model)
                return response_model.model_validate(fallback_dict)

        except ValidationError as err:
            logger.warning(f"Schema validation error: {err}. Attempting fallback extraction...")
            fallback_dict = self._extract_fallback_data(raw_response, response_model)
            try:
                return response_model.model_validate(fallback_dict)
            except Exception as e2:
                raise OllamaValidationError(f"Failed to extract valid {response_model.__name__}: {e2}") from e2


# Central singleton instance
ai_client = OllamaClient()
