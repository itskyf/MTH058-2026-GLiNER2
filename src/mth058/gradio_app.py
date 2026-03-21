"""Entry point for the MTH058 Incident Triage Copilot."""

import logging

import gradio as gr

from mth058.data.fixtures import load_sample_incidents
from mth058.services.classifier import ClassifierService
from mth058.services.extractor import ExtractorService, get_gliner_model
from mth058.services.orchestrator import Orchestrator
from mth058.services.redactor import RedactorService
from mth058.services.similarity import SimilarityService
from mth058.ui.interface import create_ui
from mth058.ui.theme import load_custom_css

# Configure logging
logger = logging.getLogger(__name__)

# Heavy resources that must not be reloaded on every file-save during development.
# gr.NO_RELOAD is True during `gradio` hot-reload and True in normal `python` execution,
# so this guard is safe to leave in production.
if gr.NO_RELOAD:
    logger.info("Loading heavy resources...")
    _model = get_gliner_model()
    _fixtures = load_sample_incidents()

_extractor = ExtractorService(model=_model)
_classifier = ClassifierService(model=_model)
_redactor = RedactorService()
_similarity = SimilarityService()

_orchestrator = Orchestrator(
    extractor=_extractor,
    classifier=_classifier,
    redactor=_redactor,
    similarity=_similarity,
    fixtures=_fixtures,
)

# Build the UI on every reload so layout/theme changes are picked up immediately.
demo = create_ui(_orchestrator, _fixtures)

# Enable queue for concurrency handling in Gradio 6.0
demo.queue()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    custom_css = load_custom_css()
    logger.info("Starting Gradio server...")
    # App-level parameters (theme, css, js) are passed to launch() in Gradio 6.0
    demo.launch(share=False, css=custom_css)
