from __future__ import annotations

from typing import Any, Dict, Mapping, Type

from pydantic import BaseModel

from app.core.schemas import QuotationUploadRequest, StructuredQuotation


class ExtractorAgent:
    """
    Heuristic extractor that always returns a StructuredQuotation.

    This initial version does not call an LLM. It inspects the
    StructuredQuotation schema and builds a payload with safe default
    values, using fields from the incoming upload request whenever
    possible (raw_text, supplier, filename, metadata, etc.).

    Later we can replace the internal logic with an LLM-powered
    implementation without changing the public interface.
    """

    def extract(self, upload_request: QuotationUploadRequest) -> StructuredQuotation:
        """
        Extract a StructuredQuotation from a QuotationUploadRequest.

        The returned object is deterministic and schema-driven, so it
        is suitable for tests and local development.
        """
        model_cls = self._get_model_class()
        payload = self._build_payload_for_model(
            model_cls=model_cls,
            upload=upload_request,
        )
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
        upload: QuotationUploadRequest,
    ) -> Dict[str, Any]:
        """
        Build a payload for a Pydantic model using the given upload request.

        Supports both Pydantic v1 (__fields__) and v2 (model_fields).
        The mapping is heuristic:
        - raw_text-like fields get upload.raw_text
        - supplier-like fields get upload.supplier
        - filename gets upload.filename
        - metadata gets upload.metadata
        - other fields receive type-based defaults
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
                field,
                "outer_type_",
                None,
            )

            value: Any

            # Prefer to use upload fields when names are obviously related
            if name in {"raw_text", "text", "content", "body"}:
                value = upload.raw_text
            elif name in {"supplier", "supplier_name", "vendor", "vendor_name"}:
                value = upload.supplier
            elif name == "filename":
                value = upload.filename
            elif name == "metadata":
                value = upload.metadata
            # Type-based fallbacks
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
                # Unknown or complex type: keep None so Pydantic can handle
                value = None

            payload[name] = value

        return payload
