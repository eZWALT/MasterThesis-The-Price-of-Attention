"""
Stage 1 — Intent Classifier.

Reads  : state.query, state.context
Writes : state.intent  (human-readable label string)

Model  : Thrad/thrad-bert-conversation-classifier
         DistilBERT fine-tuned on 13 conversation-intent classes
         (83.8 % accuracy on 2 224 held-out samples).
         Runs on CPU; inference < 50 ms.

Label mapping (index → name):
  0  academic_help
  1  personal_writing_or_communication
  2  writing_and_editing
  3  creative_writing_and_role_play
  4  general_guidance_and_info
  5  programming_and_data_analysis
  6  creative_ideation
  7  purchasable_products          ← main signal for ad injection
  8  greetings_and_chitchat
  9  relationships_and_personal_reflection
  10 media_generation_or_analysis
  11 other
  12 other_obscene_or_illegal

The labels are read directly from the model's id2label config so the
classifier stays in sync even if the checkpoint is updated.

Override with env var  INTENT_MODEL_NAME  to swap checkpoints without
touching this file.
"""

from __future__ import annotations

from core.config import INTENT_MODEL_NAME, INTENT_DEVICE
from core.log import logger
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState


class IntentClassifier(PipelineStage):
    """
    Sequence-classification intent stage using ThradBERT.

    Config keys (core.config)
    -------------------------
    INTENT_MODEL_NAME  — HuggingFace model id (overridable via env var)
    INTENT_DEVICE      — "cpu" default; set to "cuda:N" to move to GPU

    Output
    ------
    state.intent : human-readable label (e.g. "purchasable_products").
                   Falls back to "" on any error so downstream stages
                   always continue.
    """

    # Canonical label list — kept here as authoritative documentation.
    # The classifier reads id2label from the model config at runtime
    # so this list is only used as a fallback if the model fails to load.
    LABEL_MAP: dict[int, str] = {
        0:  "academic_help",
        1:  "personal_writing_or_communication",
        2:  "writing_and_editing",
        3:  "creative_writing_and_role_play",
        4:  "general_guidance_and_info",
        5:  "programming_and_data_analysis",
        6:  "creative_ideation",
        7:  "purchasable_products",
        8:  "greetings_and_chitchat",
        9:  "relationships_and_personal_reflection",
        10: "media_generation_or_analysis",
        11: "other",
        12: "other_obscene_or_illegal",
    }

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._id2label: dict[int, str] = self.LABEL_MAP.copy()
        self._device_str = INTENT_DEVICE
        try:
            self._model, self._tokenizer, self._id2label = self._load(
                INTENT_MODEL_NAME, INTENT_DEVICE
            )
        except Exception as exc:
            logger.warning(
                "IntentClassifier: could not load '{}': {}. "
                "Intent stage will be a no-op (state.intent = '').",
                INTENT_MODEL_NAME,
                exc,
            )

    # ── private ─────────────────────────────────────────────────────────

    @staticmethod
    def _load(model_name: str, device: str):
        """
        Load model + tokenizer and return (model, tokenizer, id2label).

        Places the model on `device`; keeps on CPU if 'cpu'.
        """
        import torch
        from transformers import BertTokenizerFast, AutoModelForSequenceClassification

        # The ThradBERT repo ships model weights + config but no tokenizer files.
        # DistilBERT/BERT share the same WordPiece vocabulary, so we load the
        # tokenizer from bert-base-uncased and the model from the checkpoint.
        tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        target = torch.device(device)
        model = model.to(target)
        model.eval()

        # Read label mapping from model config.
        # If the config still has generic LABEL_N names (missing from upstream
        # repo), fall back to the canonical LABEL_MAP defined on this class.
        raw_id2label: dict[int, str] = {
            int(k): v for k, v in model.config.id2label.items()
        }
        all_generic = all(v.startswith("LABEL_") for v in raw_id2label.values())
        id2label = IntentClassifier.LABEL_MAP.copy() if all_generic else raw_id2label

        return model, tokenizer, id2label

    def _classify(self, text: str) -> str:
        """Tokenise, forward-pass, return the top label string."""
        import torch

        device = next(self._model.parameters()).device
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        # DistilBERT does not accept token_type_ids — drop it if present.
        inputs = {k: v.to(device) for k, v in inputs.items()
                  if k != "token_type_ids"}

        with torch.no_grad():
            logits = self._model(**inputs).logits

        pred_idx = int(logits.argmax(dim=-1).item())
        return self._id2label.get(pred_idx, f"LABEL_{pred_idx}")

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if self._model is None:
            state.intent = ""
            return state
        try:
            state.intent = self._classify(state.query)
        except Exception as exc:
            logger.opt(exception=True).error("IntentClassifier inference error: {}", exc)
            state.intent = ""
        return state
