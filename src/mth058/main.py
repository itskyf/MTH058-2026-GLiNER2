"""Entry point for the MTH058 Incident Triage Copilot."""

import logging

import gradio as gr

from mth058.data.fixtures import load_sample_incident
from mth058.services.classifier import ClassifierService
from mth058.services.extractor import ExtractorService, get_gliner_model
from mth058.services.orchestrator import Orchestrator
from mth058.services.redactor import RedactorService
from mth058.services.similarity import SimilarityService
from mth058.ui.app import create_ui
from mth058.ui.theme import load_custom_css

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_demo() -> gr.Blocks:
    """Initialize application components and return the Gradio demo object.

    Returns:
        gr.Blocks: The initialized Gradio Blocks instance.
    """
    # 1. Initialize Model and Services
    logger.info("Loading GLiNER2 model...")
    try:
        model = get_gliner_model()
    except (RuntimeError, ImportError, ValueError):
        logger.exception("Critical failure loading GLiNER2 model")
        raise

    # 2. Load Fixtures
    logger.info("Loading incident fixtures...")
    try:
        sample_incident = load_sample_incident()
        fixtures = [sample_incident]
    except (FileNotFoundError, ValueError) as e:
        logger.warning("Failed to load fixtures: %s. Starting with empty list.", e)
        fixtures = []

    extractor = ExtractorService(model=model)
    classifier = ClassifierService(model=model)
    redactor = RedactorService()
    similarity = SimilarityService()

    orchestrator = Orchestrator(
        extractor=extractor,
        classifier=classifier,
        redactor=redactor,
        similarity=similarity,
        fixtures=fixtures,
    )

    # 3. Create UI
    demo_obj = create_ui(orchestrator, fixtures)

    # Enable queue for concurrency handling in Gradio 6.0
    demo_obj.queue(default_concurrency_limit=2)

    return demo_obj


# Global demo object for Gradio reloader compatibility (getattr(module, 'demo'))
demo: gr.Blocks = create_demo()


def main() -> None:
    """Launch the Gradio application."""
    # Load custom CSS for launch
    custom_css = load_custom_css()

    logger.info("Starting Gradio server...")
    demo.launch(share=False, debug=True, css=custom_css)


if __name__ == "__main__":
    main()
