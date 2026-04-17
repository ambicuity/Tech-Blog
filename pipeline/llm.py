from __future__ import annotations

import json
from pathlib import Path


class LLMClient:
    def __init__(self, api_key: str) -> None:
        try:
            from google import genai  # type: ignore
        except ImportError as exc:
            raise RuntimeError("google-genai package is not installed") from exc
        self.genai = genai
        self.client = genai.Client(api_key=api_key)

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> str:
        from google.genai import types  # type: ignore

        cfg = types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
            ]
        )

        if temperature is not None:
            cfg.temperature = float(temperature)
        if top_p is not None:
            cfg.top_p = float(top_p)

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=cfg,
        )
        if not response or not response.text:
            raise RuntimeError("Empty LLM response")
        return response.text.strip()


def load_prompt(name: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / name
    return path.read_text(encoding="utf-8")


def try_parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return {}
