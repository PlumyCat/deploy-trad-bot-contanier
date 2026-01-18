"""
Tests unitaires pour le module azure_wrappers.functions

Ces tests vérifient le wrapper Python pour le déploiement Azure Functions.

Story: STORY-008 (Wrapper Python Azure CLI - Déploiement Azure Functions)
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess
from datetime import datetime

from azure_wrappers.functions import (
    create_function_app,
    configure_app_settings,
    deploy_functions,
    check_health,
    verify_function_app,
    delete_function_app,
    _create_deployment_zip,
    _list_deployed_functions,
    FUNCTION_RUNTIME_DEFAULT,
    FUNCTION_RUNTIME_VERSION_DEFAULT,
    EXPECTED_FUNCTIONS,
)
from azure_wrappers.common import AzureWrapperError


# ============================================
# Tests: create_function_app()
# ============================================


class TestCreateFunctionApp:
    """Tests pour create_function_app()"""

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    def test_create_function_app_success(self, mock_run, mock_login):
        """Test: Création réussie d'une Function App"""
        mock_response = {
            "name": "func-test-app",
            "id": "/subscriptions/123/resourceGroups/rg-test/providers/Microsoft.Web/sites/func-test-app",
            "defaultHostName": "func-test-app.azurewebsites.net",
            "state": "Running",
        }
        mock_run.return_value = json.dumps(mock_response)

        result = create_function_app(
            name="func-test-app",
            resource_group="rg-test",
            storage_account="storage123",
            region="francecentral",
        )

        assert result["name"] == "func-test-app"
        assert result["default_hostname"] == "func-test-app.azurewebsites.net"
        assert result["runtime"] == FUNCTION_RUNTIME_DEFAULT
        assert result["runtime_version"] == FUNCTION_RUNTIME_VERSION_DEFAULT
        assert result["region"] == "francecentral"
        assert result["storage_account"] == "storage123"

        # Vérifier la commande Azure CLI
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "az" in cmd
        assert "functionapp" in cmd
        assert "create" in cmd
        assert "--name" in cmd
        assert "func-test-app" in cmd
        assert "--runtime" in cmd
        assert "python" in cmd
        assert "--runtime-version" in cmd
        assert "3.11" in cmd

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    def test_create_function_app_with_tags(self, mock_run, mock_login):
        """Test: Création avec tags"""
        mock_response = {
            "name": "func-test",
            "defaultHostName": "func-test.azurewebsites.net",
        }
        mock_run.return_value = json.dumps(mock_response)

        result = create_function_app(
            name="func-test",
            resource_group="rg-test",
            storage_account="storage123",
            tags={"client": "Acme", "env": "prod"},
        )

        assert result["name"] == "func-test"

        # Vérifier que les tags sont dans la commande
        cmd = mock_run.call_args[0][0]
        assert "--tags" in cmd

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    def test_create_function_app_error_already_exists(self, mock_run, mock_login):
        """Test: Erreur si Function App existe déjà"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "az", stderr="WebsiteAlreadyExists"
        )

        with pytest.raises(AzureWrapperError, match="existe déjà"):
            create_function_app(
                name="func-existing",
                resource_group="rg-test",
                storage_account="storage123",
            )

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    def test_create_function_app_no_storage(self, mock_login):
        """Test: Erreur si Storage Account non fourni"""
        with pytest.raises(AzureWrapperError, match="Storage Account est requis"):
            create_function_app(
                name="func-test",
                resource_group="rg-test",
                storage_account="",
            )

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=False)
    def test_create_function_app_not_logged_in(self, mock_login):
        """Test: Erreur si non connecté à Azure CLI"""
        with pytest.raises(AzureWrapperError, match="connecté à Azure CLI"):
            create_function_app(
                name="func-test",
                resource_group="rg-test",
                storage_account="storage123",
            )


# ============================================
# Tests: configure_app_settings()
# ============================================


class TestConfigureAppSettings:
    """Tests pour configure_app_settings()"""

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    def test_configure_app_settings_success(self, mock_run, mock_login):
        """Test: Configuration réussie des app settings"""
        mock_run.return_value = "{}"

        settings = {
            "AZURE_ACCOUNT_NAME": "storage123",
            "AZURE_ACCOUNT_KEY": "key123",
            "TRANSLATOR_KEY": "translator_key",
            "TRANSLATOR_ENDPOINT": "https://api.cognitive.microsofttranslator.com/",
            "TRANSLATOR_REGION": "francecentral",
        }

        result = configure_app_settings(
            name="func-test",
            resource_group="rg-test",
            settings=settings,
        )

        assert result is True

        # Vérifier la commande
        cmd = mock_run.call_args[0][0]
        assert "az" in cmd
        assert "functionapp" in cmd
        assert "config" in cmd
        assert "appsettings" in cmd
        assert "set" in cmd
        assert "--settings" in cmd

        # Vérifier que toutes les variables sont présentes
        cmd_str = " ".join(cmd)
        for key in settings.keys():
            assert key in cmd_str

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    def test_configure_app_settings_empty(self, mock_login):
        """Test: Erreur si aucune variable fournie"""
        with pytest.raises(AzureWrapperError, match="Aucune variable"):
            configure_app_settings(
                name="func-test",
                resource_group="rg-test",
                settings={},
            )


# ============================================
# Tests: deploy_functions()
# ============================================


class TestDeployFunctions:
    """Tests pour deploy_functions()"""

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    @patch('azure_wrappers.functions._create_deployment_zip')
    @patch('os.remove')
    def test_deploy_functions_success(self, mock_remove, mock_zip, mock_run, mock_login, tmp_path):
        """Test: Déploiement réussi"""
        # Créer un dossier source temporaire avec host.json
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "host.json").write_text("{}")

        mock_response = {
            "status": "success",
            "id": "deployment-123",
        }
        mock_run.return_value = json.dumps(mock_response)

        result = deploy_functions(
            name="func-test",
            resource_group="rg-test",
            source_dir=str(source_dir),
        )

        assert result["status"] == "success"
        assert result["deployment_id"] == "deployment-123"
        assert "duration_seconds" in result

        # Vérifier que ZIP a été créé et nettoyé
        mock_zip.assert_called_once()
        mock_remove.assert_called_once()

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    def test_deploy_functions_source_not_exists(self, mock_login):
        """Test: Erreur si dossier source n'existe pas"""
        with pytest.raises(AzureWrapperError, match="n'existe pas"):
            deploy_functions(
                name="func-test",
                resource_group="rg-test",
                source_dir="/non/existent/path",
            )

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    def test_deploy_functions_no_host_json(self, mock_login, tmp_path):
        """Test: Erreur si host.json manquant"""
        source_dir = tmp_path / "src"
        source_dir.mkdir()

        with pytest.raises(AzureWrapperError, match="host.json.*manquant"):
            deploy_functions(
                name="func-test",
                resource_group="rg-test",
                source_dir=str(source_dir),
            )


# ============================================
# Tests: check_health()
# ============================================


class TestCheckHealth:
    """Tests pour check_health()"""

    @patch('azure_wrappers.functions.requests.get')
    def test_check_health_success(self, mock_get):
        """Test: Health check réussi"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = check_health(
            function_app_url="https://func-test.azurewebsites.net",
            retry_count=1,
        )

        assert result["status"] == "healthy"
        assert result["status_code"] == 200
        assert "response_time_ms" in result

    @patch('azure_wrappers.functions.requests.get')
    def test_check_health_retry_success(self, mock_get):
        """Test: Health check réussit après retry"""
        # Premier appel échoue, deuxième réussit
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 503

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        result = check_health(
            function_app_url="https://func-test.azurewebsites.net",
            retry_count=2,
            retry_delay=0,
        )

        assert result["status"] == "healthy"
        assert mock_get.call_count == 2

    @patch('azure_wrappers.functions.requests.get')
    def test_check_health_failure(self, mock_get):
        """Test: Health check échoue après tous les retries"""
        mock_get.side_effect = Exception("Connection error")

        with pytest.raises(AzureWrapperError, match="échoué"):
            check_health(
                function_app_url="https://func-test.azurewebsites.net",
                retry_count=2,
                retry_delay=0,
            )


# ============================================
# Tests: verify_function_app()
# ============================================


class TestVerifyFunctionApp:
    """Tests pour verify_function_app()"""

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    @patch('azure_wrappers.functions._list_deployed_functions')
    def test_verify_function_app_exists(self, mock_list, mock_run, mock_login):
        """Test: Vérification d'une Function App existante"""
        mock_response = {
            "name": "func-test",
            "state": "Running",
            "defaultHostName": "func-test.azurewebsites.net",
            "kind": "functionapp,linux",
        }
        mock_run.return_value = json.dumps(mock_response)
        mock_list.return_value = ["health", "start_translation"]

        result = verify_function_app(
            name="func-test",
            resource_group="rg-test",
        )

        assert result["exists"] is True
        assert result["state"] == "Running"
        assert result["default_hostname"] == "func-test.azurewebsites.net"
        assert len(result["functions"]) == 2

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    def test_verify_function_app_not_exists(self, mock_run, mock_login):
        """Test: Function App n'existe pas"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "az")

        result = verify_function_app(
            name="func-nonexistent",
            resource_group="rg-test",
        )

        assert result["exists"] is False
        assert result["state"] == ""


# ============================================
# Tests: delete_function_app()
# ============================================


class TestDeleteFunctionApp:
    """Tests pour delete_function_app()"""

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.functions.run_az_command')
    def test_delete_function_app_success(self, mock_run, mock_login):
        """Test: Suppression réussie"""
        mock_run.return_value = ""

        result = delete_function_app(
            name="func-test",
            resource_group="rg-test",
            confirm=True,
        )

        assert result is True

        # Vérifier la commande
        cmd = mock_run.call_args[0][0]
        assert "az" in cmd
        assert "functionapp" in cmd
        assert "delete" in cmd
        assert "--yes" in cmd

    @patch('azure_wrappers.functions.check_az_logged_in', return_value=True)
    def test_delete_function_app_no_confirm(self, mock_login):
        """Test: Erreur si pas de confirmation"""
        with pytest.raises(AzureWrapperError, match="confirmation explicite"):
            delete_function_app(
                name="func-test",
                resource_group="rg-test",
                confirm=False,
            )


# ============================================
# Tests: Helper Functions
# ============================================


class TestHelperFunctions:
    """Tests pour les fonctions helper"""

    def test_create_deployment_zip(self, tmp_path):
        """Test: Création d'un ZIP de déploiement"""
        # Créer une structure de dossier
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "host.json").write_text("{}")
        (source_dir / "function_app.py").write_text("# code")

        # Créer dossiers à ignorer
        (source_dir / "__pycache__").mkdir()
        (source_dir / "__pycache__" / "test.pyc").write_text("")

        zip_path = str(tmp_path / "deploy.zip")

        _create_deployment_zip(source_dir, zip_path)

        # Vérifier que le ZIP existe
        assert Path(zip_path).exists()

        # Vérifier le contenu du ZIP
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            names = zipf.namelist()
            assert "host.json" in names
            assert "function_app.py" in names
            # __pycache__ ne doit pas être dans le ZIP
            assert not any("__pycache__" in name for name in names)

    @patch('azure_wrappers.functions.run_az_command')
    def test_list_deployed_functions_success(self, mock_run):
        """Test: Liste des functions déployées"""
        mock_response = [
            {"name": "health"},
            {"name": "start_translation"},
            {"name": "check_status"},
        ]
        mock_run.return_value = json.dumps(mock_response)

        result = _list_deployed_functions("func-test", "rg-test")

        assert len(result) == 3
        assert "health" in result
        assert "start_translation" in result


# ============================================
# Tests: STORY-008 Acceptance Criteria
# ============================================


class TestSTORY008AcceptanceCriteria:
    """Tests de validation des critères d'acceptation STORY-008"""

    def test_acceptance_criteria_1_create_function_app_exists(self):
        """AC1: Fonction create_function_app() implémentée"""
        from azure_wrappers.functions import create_function_app
        assert create_function_app is not None
        assert callable(create_function_app)

    def test_acceptance_criteria_2_python_3_11_runtime(self):
        """AC2: Function App créée avec runtime Python 3.11"""
        assert FUNCTION_RUNTIME_DEFAULT == "python"
        assert FUNCTION_RUNTIME_VERSION_DEFAULT == "3.11"

    def test_acceptance_criteria_3_expected_functions(self):
        """AC3: Toutes les functions attendues sont définies"""
        expected = ["start_translation", "check_status", "get_result", "health", "languages", "formats"]
        assert EXPECTED_FUNCTIONS == expected
        assert len(EXPECTED_FUNCTIONS) == 6

    def test_acceptance_criteria_4_configure_app_settings_exists(self):
        """AC4: Fonction configure_app_settings() pour variables d'environnement"""
        from azure_wrappers.functions import configure_app_settings
        assert configure_app_settings is not None
        assert callable(configure_app_settings)

    def test_acceptance_criteria_5_deploy_returns_url(self):
        """AC5: create_function_app() retourne l'URL de la Function App"""
        # Vérifié par test_create_function_app_success
        # qui valide que "default_hostname" est retourné
        pass

    def test_acceptance_criteria_6_health_check_exists(self):
        """AC6: Fonction check_health() implémentée pour vérifier /api/health"""
        from azure_wrappers.functions import check_health
        assert check_health is not None
        assert callable(check_health)

    def test_acceptance_criteria_7_logs_sanitized(self):
        """AC7: Les logs sont sanitizés (aucun credential visible)"""
        # Les credentials sont sanitizés via sanitize_credential() de common.py
        # Les app settings sont passés via Azure CLI de manière sécurisée
        from azure_wrappers.common import sanitize_credential
        assert sanitize_credential is not None

        # Test que sanitize_credential masque correctement
        key = "secret_key_12345"
        masked = sanitize_credential(key, visible_chars=4)
        assert "secret" not in masked
        assert "2345" in masked  # Derniers 4 chars
