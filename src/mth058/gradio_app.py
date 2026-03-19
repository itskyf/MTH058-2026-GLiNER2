"""Entry point for the MTH058 Incident Triage Copilot."""

import logging

import gradio as gr

from mth058.data.fixtures import load_sample_incident
from mth058.services.classifier import ClassifierService
from mth058.services.extractor import ExtractorService, get_gliner_model
from mth058.services.orchestrator import Orchestrator
from mth058.services.redactor import RedactorService
from mth058.services.similarity import SimilarityService
from mth058.ui.interface import create_ui
from mth058.ui.theme import load_custom_css

# Configure logging
logger = logging.getLogger(__name__)


def create_demo() -> gr.Blocks:
    """Initialize application components and return the Gradio demo object.

    This function coordinates the initialization of GLiNER2 services and
    constructs the user interface.

    Returns:
        gr.Blocks: The initialized Gradio Blocks instance.
    """
    logger.info("Initializing Incident Triage Copilot services...")

    # 1. Initialize Model (Module-level lru_cache handles reuse)
    try:
        model = get_gliner_model()
    except (RuntimeError, ImportError, ValueError):
        logger.exception("Critical failure loading GLiNER2 model")
        raise

    # 2. Load Fixtures
    sample_incident = load_sample_incident()
    fixtures = [sample_incident]

    # 3. Initialize Domain Services
    extractor = ExtractorService(model=model)
    classifier = ClassifierService(model=model)
    redactor = RedactorService()
    similarity = SimilarityService()

    # 4. Initialize Orchestrator
    orchestrator = Orchestrator(
        extractor=extractor,
        classifier=classifier,
        redactor=redactor,
        similarity=similarity,
        fixtures=fixtures,
    )

    # 5. Create UI
    demo_obj = create_ui(orchestrator, fixtures)

    # Enable queue for concurrency handling in Gradio 6.0
    demo_obj.queue(default_concurrency_limit=2)

    return demo_obj


# Global `demo` object for Gradio reloader compatibility
demo: gr.Blocks = create_demo()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    custom_css = load_custom_css()
    logger.info("Starting Gradio server...")
    # App-level parameters (theme, css, js) are passed to launch() in Gradio 6.0
    demo.launch(share=False, debug=True, css=custom_css)
