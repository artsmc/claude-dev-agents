"""Tests for SOLID analyzer.

Validates detection of violations for all five SOLID principles:
SRP, OCP, LSP, ISP, and DIP.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.analyzers.solid_analyzer import SOLIDAnalyzer
from lib.analyzers.base import AnalysisContext
from lib.models.config import AssessmentConfig, SOLIDThresholds


@pytest.fixture
def config():
    """Create test configuration."""
    return AssessmentConfig()


@pytest.fixture
def analyzer():
    """Create SOLID analyzer instance."""
    return SOLIDAnalyzer()


def test_analyzer_metadata(analyzer):
    """Test analyzer metadata."""
    assert analyzer.get_name() == "solid"
    assert "SOLID" in analyzer.get_description()


def test_srp_too_many_methods(analyzer, config):
    """Test SRP violation for class with too many methods."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create class with 15 methods (exceeds default threshold of 10)
        methods = "\n".join(f"    def method_{i}(self): pass" for i in range(15))
        test_file.write_text(f"""
class GodClass:
{methods}
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect SRP violation
        srp_violations = [v for v in violations if v.type == "SRPViolation"]
        assert len(srp_violations) > 0
        assert "too many methods" in srp_violations[0].message.lower()


def test_srp_god_class_loc(analyzer, config):
    """Test SRP violation for God class with too many lines."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create large class (>500 LOC)
        methods = "\n".join(
            f"    def method_{i}(self):\n" + "        pass\n" * 20
            for i in range(30)
        )
        test_file.write_text(f"""
class VeryLargeClass:
{methods}
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect God class
        god_classes = [
            v for v in violations
            if "God Class" in v.message
        ]
        assert len(god_classes) > 0
        assert god_classes[0].severity == "HIGH"


def test_srp_low_cohesion(analyzer, config):
    """Test SRP violation for low cohesion (LCOM)."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create class with low cohesion (methods don't share instance vars)
        test_file.write_text("""
class LowCohesionClass:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3
        self.d = 4

    def method1(self):
        return self.a

    def method2(self):
        return self.b

    def method3(self):
        return self.c

    def method4(self):
        return self.d
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect low cohesion
        cohesion_violations = [
            v for v in violations
            if "cohesion" in v.message.lower()
        ]
        assert len(cohesion_violations) > 0


def test_ocp_type_checking_chain(analyzer, config):
    """Test OCP violation for type-based if-elif chain."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create if-elif chain with type checking
        test_file.write_text("""
def process_payment(payment):
    if isinstance(payment, CreditCard):
        return process_credit_card(payment)
    elif isinstance(payment, DebitCard):
        return process_debit_card(payment)
    elif isinstance(payment, PayPal):
        return process_paypal(payment)
    elif isinstance(payment, Bitcoin):
        return process_bitcoin(payment)
    elif isinstance(payment, Cash):
        return process_cash(payment)
    else:
        raise ValueError("Unknown payment type")
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect OCP violation
        ocp_violations = [v for v in violations if v.type == "OCPViolation"]
        assert len(ocp_violations) > 0
        assert "if-elif" in ocp_violations[0].message.lower()


def test_lsp_not_implemented_error(analyzer, config):
    """Test LSP violation for NotImplementedError in subclass."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create subclass that raises NotImplementedError
        test_file.write_text("""
class Animal:
    def make_sound(self):
        pass

class Cat(Animal):
    def make_sound(self):
        raise NotImplementedError("Cats don't make sounds")
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect LSP violation
        lsp_violations = [v for v in violations if v.type == "LSPViolation"]
        assert len(lsp_violations) > 0
        assert "NotImplementedError" in lsp_violations[0].message


def test_isp_fat_interface(analyzer, config):
    """Test ISP violation for fat interface."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create interface with too many methods
        methods = "\n".join(f"    def method_{i}(self): pass" for i in range(15))
        test_file.write_text(f"""
class IFatInterface(BaseInterface):
{methods}
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect fat interface
        isp_violations = [v for v in violations if v.type == "ISPViolation"]
        assert len(isp_violations) > 0
        assert "Fat interface" in isp_violations[0].message


def test_isp_stub_methods(analyzer, config):
    """Test ISP violation for stub methods."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create class with stub methods
        test_file.write_text("""
class PartialImplementation(FullInterface):
    def method1(self):
        return "implemented"

    def method2(self):
        pass

    def method3(self):
        pass

    def method4(self):
        pass

    def method5(self):
        pass
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect stub methods
        stub_violations = [
            v for v in violations
            if "stub" in v.message.lower()
        ]
        assert len(stub_violations) > 0


def test_dip_concrete_dependencies(analyzer, config):
    """Test DIP violation for concrete dependencies in constructor."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create class that instantiates many concrete dependencies
        test_file.write_text("""
class UserService:
    def __init__(self):
        self.db = DatabaseClient()
        self.cache = RedisCache()
        self.logger = FileLogger()
        self.mailer = SmtpMailer()
        self.notifier = PushNotifier()
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect DIP violation
        dip_violations = [v for v in violations if v.type == "DIPViolation"]
        assert len(dip_violations) > 0
        assert "concrete dependencies" in dip_violations[0].message.lower()


def test_custom_thresholds(analyzer):
    """Test SOLID analyzer with custom thresholds."""
    config = AssessmentConfig()
    config.project.solid_thresholds = SOLIDThresholds(
        srp_max_methods=5,
        srp_max_loc=200,
    )

    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create class with 7 methods (exceeds custom threshold)
        methods = "\n".join(f"    def method_{i}(self): pass" for i in range(7))
        test_file.write_text(f"""
class CustomClass:
{methods}
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect with custom threshold
        assert len(violations) > 0


def test_no_violations_clean_code(analyzer, config):
    """Test analyzer with clean SOLID-compliant code."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create well-designed class
        test_file.write_text("""
class WellDesignedService:
    def __init__(self, repository):
        self.repository = repository

    def get_user(self, user_id):
        return self.repository.find_by_id(user_id)

    def save_user(self, user):
        return self.repository.save(user)
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should have no violations
        assert len(violations) == 0


def test_violation_metadata(analyzer, config):
    """Test that violations include proper metadata."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        methods = "\n".join(f"    def method_{i}(self): pass" for i in range(15))
        test_file.write_text(f"""
class TestClass:
{methods}
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        assert len(violations) > 0
        violation = violations[0]

        # Check violation structure
        assert violation.dimension == "solid"
        assert violation.id.startswith("SRP-") or violation.id.startswith("OCP-")
        assert violation.line_number is not None
        assert violation.recommendation != ""
        assert violation.explanation != ""


def test_only_python_files_analyzed(analyzer, config):
    """Test that only Python files are analyzed."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Python file
        py_file = project_root / "test.py"
        methods = "\n".join(f"    def method_{i}(self): pass" for i in range(15))
        py_file.write_text(f"class BadClass:\n{methods}")

        # Create JavaScript file
        js_file = project_root / "test.js"
        js_file.write_text("class BadClass { /* many methods */ }")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[py_file, js_file],
        )

        violations = analyzer.analyze(context)

        # Should only analyze Python file
        assert len(violations) > 0
        assert all("test.py" in v.file_path for v in violations)
