"""Check the website independently from the original discovery release."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_public_website():
    spec=importlib.util.spec_from_file_location('atlas_web_validator',ROOT/'scripts/validate_web.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result=module.validate(ROOT)
    assert result['passed'],result['errors']
