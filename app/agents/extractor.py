from __future__ import annotations

from typing import Any, Dict, Mapping, Type

from pydantic import BaseModel

from app.core.contracts import StructuredQuotation


class ExtractorAgent:
    """
    Simple heuristic extractor that always returns a StructuredQuotation.

    This initial version does not call an LLM yet. It inspects the
    StructuredQuotation schema and builds a payload with safe default
    values, using the incoming raw_text where it makes sense.
    """

    def extract(self, raw_text: str) -> StructuredQuotation:
        """
        Extract a StructuredQuotation from a raw text.

        For now this is a heuristic, schema-driven implementation that:
        - inspects the StructuredQuotation Pydantic model;
        - fills reasonable defaults for each field;
        - uses the raw_text in fields that look like the main text field.

        Later we can replace the internal logic with an LLM-powered
        implementation without changing the public interface.
        """
        model_cls = self._get_model_class()
        payload = self._build_payload_for_model(model_cls=model_cls, raw_text=raw_text)
        return model_cls(**payload)

    @staticmethod
    def _get_model_class() -> Type[StructuredQuotation]:
        """
        Resolve the StructuredQuotation model class and validate assumptions.
        """
        if not isinstance(StructuredQuotation, type):
            raise TypeError("StructuredQuotation must be a class.")

        if not issubclass(StructuredQuotation, BaseModel):
            raise TypeError(
                "StructuredQuotation must inherit from pydantic.BaseModel."
            )

        return StructuredQuotation

    @classmethod
    def _build_payload_for_model(
        cls,
        model_cls: Type[BaseModel],
        raw_text: str,
    ) -> Dict[str, Any]:
        """
        Build a payload for a Pydantic model using the given raw_text.

        Supports both Pydantic v1 (__fields__) and v2 (model_fields).
        """
        field_defs: Mapping[str, Any]

        if hasattr(model_cls, "model_fields"):
            # Pydantic v2
            field_defs = model_cls.model_fields  # type: ignore[attr-defined]
        elif hasattr(model_cls, "__fields__"):
            # Pydantic v1
            field_defs = model_cls.__fields__  # type: ignore[attr-defined]
        else:
            raise TypeError(
                "StructuredQuotation model does not expose known Pydantic fields API."
            )

        payload: Dict[str, Any] = {}

        for name, field in field_defs.items():
            # Pydantic v2: field.annotation
            # Pydantic v1: field.outer_type_
            annotation = getattr(field, "annotation", None) or getattr(
                field, "outer_type_", None
            )

            value: Any

            # Prefer to use raw_text in obviously text-related fields
            if name in {"raw_text", "text", "content", "body"}:
                value = raw_text
            elif annotation is str:
                value = ""
            elif annotation is int:
                value = 0
            elif annotation is float:
                value = 0.0
            elif annotation is bool:
                value = False
            elif annotation in (list, tuple, set):
                value = []
            else:
                # Fallback: we do not know the best value, keep it None
                value = None

            payload[name] = value

        return payload
