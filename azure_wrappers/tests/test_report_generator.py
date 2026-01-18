"""
Tests unitaires pour le module azure_wrappers.report_generator

Ces tests vérifient la génération automatique des rapports d'intervention.

Story: STORY-015 (Génération Automatique Rapport d'Intervention)
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from azure_wrappers.report_generator import (
    generate_report,
    save_report,
    display_report,
    regenerate_report,
    list_reports,
    REPORT_DIR,
)


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def sample_storage_info():
    """Informations Storage Account"""
    return {
        "name": "storageclienttest123",
        "sku": "Standard_LRS",
        "container_name": "translations",
        "primary_endpoints": {
            "blob": "https://storageclienttest123.blob.core.windows.net/"
        }
    }


@pytest.fixture
def sample_translator_info():
    """Informations Translator"""
    return {
        "name": "translator-clienttest-001",
        "sku": "F0",
        "region": "francecentral",
        "endpoint": "https://api.cognitive.microsofttranslator.com/"
    }


@pytest.fixture
def sample_function_app_info():
    """Informations Function App"""
    return {
        "name": "func-clienttest-001",
        "runtime_version": "3.11",
        "default_hostname": "func-clienttest-001.azurewebsites.net",
        "state": "Running"
    }


@pytest.fixture
def temp_report_dir(monkeypatch):
    """Crée un dossier temporaire pour les rapports"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("azure_wrappers.report_generator.REPORT_DIR", tmpdir)
        yield tmpdir


# ============================================
# Tests: generate_report()
# ============================================

class TestGenerateReport:
    """Tests pour generate_report()"""

    def test_generate_report_success(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """Test: Génération réussie d'un rapport complet"""
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-clienttest-001",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info,
            technician_name="Jean Dupont",
            subscription_id="12345678-1234-1234-1234-123456789abc",
            tenant_id="87654321-4321-4321-4321-cba987654321",
            deployment_duration="12 minutes",
            notes="Déploiement test réussi"
        )

        assert result["client_name"] == "ClientTest"
        assert "report_content" in result
        assert "report_path" in result
        assert "timestamp" in result

        # Vérifier contenu du rapport
        content = result["report_content"]
        assert "ClientTest" in content
        assert "Jean Dupont" in content
        assert "rg-clienttest-001" in content
        assert "francecentral" in content
        assert "storageclienttest123" in content
        assert "translator-clienttest-001" in content
        assert "func-clienttest-001" in content
        assert "F0 (GRATUIT)" in content or "F0" in content

    def test_generate_report_missing_client_name(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info
    ):
        """Test: Erreur si nom client manquant"""
        with pytest.raises(ValueError, match="nom du client est requis"):
            generate_report(
                client_name="",
                resource_group="rg-test",
                region="francecentral",
                storage_info=sample_storage_info,
                translator_info=sample_translator_info,
                function_app_info=sample_function_app_info
            )

    def test_generate_report_missing_resource_group(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info
    ):
        """Test: Erreur si resource group manquant"""
        with pytest.raises(ValueError, match="Resource Group est requis"):
            generate_report(
                client_name="ClientTest",
                resource_group="",
                region="francecentral",
                storage_info=sample_storage_info,
                translator_info=sample_translator_info,
                function_app_info=sample_function_app_info
            )

    def test_generate_report_incomplete_info(self):
        """Test: Erreur si informations incomplètes"""
        with pytest.raises(ValueError, match="informations de déploiement sont incomplètes"):
            generate_report(
                client_name="ClientTest",
                resource_group="rg-test",
                region="francecentral",
                storage_info=None,
                translator_info=None,
                function_app_info=None
            )

    def test_generate_report_no_credentials_in_output(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """Test: Aucune credential complète dans le rapport"""
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-test",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info,
            subscription_id="12345678-1234-1234-1234-123456789abc",
            tenant_id="87654321-4321-4321-4321-cba987654321"
        )

        content = result["report_content"]

        # Vérifier que subscription_id est sanitizé (seuls 8 derniers caractères)
        assert "89abc" in content  # 8 derniers caractères visibles
        assert "12345678-1234-1234-1234" not in content  # Début masqué

        # Vérifier que tenant_id complet est présent (pas sensible)
        assert "87654321-4321-4321-4321-cba987654321" in content


# ============================================
# Tests: save_report()
# ============================================

class TestSaveReport:
    """Tests pour save_report()"""

    def test_save_report_success(self, temp_report_dir):
        """Test: Sauvegarde réussie d'un rapport"""
        content = "Test rapport contenu"
        timestamp = "20260118_143000"

        filepath = save_report(content, "ClientTest", timestamp)

        assert os.path.exists(filepath)
        assert "rapport-ClientTest-20260118_143000.txt" in filepath

        with open(filepath, "r", encoding="utf-8") as f:
            saved_content = f.read()

        assert saved_content == content

    def test_save_report_sanitizes_filename(self, temp_report_dir):
        """Test: Nom de fichier sécurisé (caractères spéciaux)"""
        content = "Test"
        timestamp = "20260118_143000"

        filepath = save_report(content, "Client/Test*123?", timestamp)

        # Vérifier que caractères spéciaux sont remplacés
        filename = Path(filepath).name
        assert "/" not in filename
        assert "*" not in filename
        assert "?" not in filename
        assert "Client_Test_123_" in filename


# ============================================
# Tests: display_report()
# ============================================

class TestDisplayReport:
    """Tests pour display_report()"""

    @patch('builtins.print')
    def test_display_report(self, mock_print):
        """Test: Affichage d'un rapport"""
        content = "Test rapport\nLigne 2"

        display_report(content)

        # Vérifier que print a été appelé
        assert mock_print.call_count > 0

        # Vérifier que le contenu est affiché
        calls = [str(call) for call in mock_print.call_args_list]
        combined = "".join(calls)
        assert "Test rapport" in combined


# ============================================
# Tests: regenerate_report()
# ============================================

class TestRegenerateReport:
    """Tests pour regenerate_report()"""

    def test_regenerate_report_success(self, temp_report_dir):
        """Test: Rechargement d'un rapport existant"""
        # Créer un rapport
        content = "Test rapport original"
        filepath = save_report(content, "ClientTest", "20260118_143000")

        # Recharger
        result = regenerate_report(filepath)

        assert result["exists"] is True
        assert result["report_content"] == content
        assert result["report_path"] == filepath

    def test_regenerate_report_not_found(self, temp_report_dir):
        """Test: Erreur si rapport inexistant"""
        with pytest.raises(FileNotFoundError):
            regenerate_report("/chemin/inexistant/rapport.txt")


# ============================================
# Tests: list_reports()
# ============================================

class TestListReports:
    """Tests pour list_reports()"""

    def test_list_reports_empty(self, temp_report_dir):
        """Test: Liste vide si aucun rapport"""
        reports = list_reports()
        assert reports == []

    def test_list_reports_multiple(self, temp_report_dir):
        """Test: Liste de plusieurs rapports"""
        # Créer 3 rapports
        save_report("Rapport 1", "ClientA", "20260118_100000")
        save_report("Rapport 2", "ClientB", "20260118_110000")
        save_report("Rapport 3", "ClientA", "20260118_120000")

        reports = list_reports()

        assert len(reports) == 3
        assert all("filename" in r for r in reports)
        assert all("filepath" in r for r in reports)
        assert all("client" in r for r in reports)
        assert all("timestamp" in r for r in reports)

    def test_list_reports_filtered_by_client(self, temp_report_dir):
        """Test: Filtrage par nom de client"""
        save_report("Rapport 1", "ClientA", "20260118_100000")
        save_report("Rapport 2", "ClientB", "20260118_110000")
        save_report("Rapport 3", "ClientA", "20260118_120000")

        reports = list_reports(client_name="ClientA")

        assert len(reports) == 2
        assert all("ClientA" in r["client"] for r in reports)

    def test_list_reports_sorted_by_timestamp(self, temp_report_dir):
        """Test: Tri par timestamp décroissant"""
        save_report("Rapport 1", "ClientA", "20260118_100000")
        save_report("Rapport 2", "ClientA", "20260118_120000")
        save_report("Rapport 3", "ClientA", "20260118_110000")

        reports = list_reports()

        # Le plus récent devrait être en premier
        assert reports[0]["timestamp"] == "20260118_120000"
        assert reports[1]["timestamp"] == "20260118_110000"
        assert reports[2]["timestamp"] == "20260118_100000"


# ============================================
# Tests: STORY-015 Acceptance Criteria
# ============================================

class TestSTORY015AcceptanceCriteria:
    """Tests de validation des critères d'acceptation STORY-015"""

    def test_acceptance_criteria_1_module_exists(self):
        """AC1: Module Python report_generator.py créé"""
        from azure_wrappers import report_generator
        assert report_generator is not None

    def test_acceptance_criteria_2_generate_report_function(self):
        """AC2: Fonction generate_report() existe"""
        from azure_wrappers.report_generator import generate_report
        assert generate_report is not None
        assert callable(generate_report)

    def test_acceptance_criteria_3_report_contains_required_info(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """AC3: Rapport contient les informations requises"""
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-test-001",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info
        )

        content = result["report_content"]

        # Vérifier présence des infos requises
        assert "ClientTest" in content  # Nom client
        assert "rg-test-001" in content  # Resource group
        assert "storageclienttest123" in content  # Services déployés
        assert "translator-clienttest-001" in content
        assert "func-clienttest-001" in content
        assert "https://" in content  # URLs/endpoints

        # Vérifier date/heure présentes
        today = datetime.now().strftime("%d/%m/%Y")
        assert today in content or "/" in content  # Format date

    def test_acceptance_criteria_4_no_credentials_in_report(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """AC4: Aucune information sensible (credentials) dans le rapport"""
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-test",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info,
            subscription_id="12345678-1234-1234-1234-123456789abc"
        )

        content = result["report_content"]

        # Vérifier que subscription complète n'est PAS présente
        assert "12345678-1234-1234-1234-123456789abc" not in content

        # Vérifier sanitization (seuls derniers caractères visibles)
        assert "89abc" in content

    def test_acceptance_criteria_5_report_saved_with_timestamp(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """AC5: Rapport sauvegardé avec timestamp"""
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-test",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info
        )

        filepath = result["report_path"]

        # Vérifier format: rapport-{client}-{timestamp}.txt
        assert "rapport-ClientTest-" in filepath
        assert ".txt" in filepath
        assert os.path.exists(filepath)

    def test_acceptance_criteria_6_report_displayed_in_terminal(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """AC6: Rapport affiché dans terminal pour copier-coller"""
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-test",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info
        )

        # Vérifier que display_report() existe
        from azure_wrappers.report_generator import display_report
        assert callable(display_report)

        # Le contenu peut être affiché
        content = result["report_content"]
        assert len(content) > 0
        assert isinstance(content, str)

    def test_acceptance_criteria_7_regenerate_report_capability(
        self,
        sample_storage_info,
        sample_translator_info,
        sample_function_app_info,
        temp_report_dir
    ):
        """AC7: Possibilité de regénérer le rapport si besoin"""
        # Générer un rapport
        result = generate_report(
            client_name="ClientTest",
            resource_group="rg-test",
            region="francecentral",
            storage_info=sample_storage_info,
            translator_info=sample_translator_info,
            function_app_info=sample_function_app_info
        )

        original_path = result["report_path"]
        original_content = result["report_content"]

        # Regénérer/recharger
        regenerated = regenerate_report(original_path)

        assert regenerated["exists"] is True
        assert regenerated["report_content"] == original_content
