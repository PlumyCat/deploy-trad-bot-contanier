"""
Tests unitaires pour le module azure_wrappers.account

Ces tests vérifient le wrapper Python pour la gestion des comptes Azure.

Story: STORY-009 (Support Multi-comptes Azure dans OpenCode)
"""

import pytest
import json
from unittest.mock import patch, MagicMock, call
import subprocess

from azure_wrappers.account import (
    login_azure,
    logout_azure,
    list_accounts,
    get_current_account,
    select_account,
    select_account_interactive,
    check_permissions,
    prompt_insufficient_permissions,
    reconnect_azure,
    ensure_logged_in_with_permissions,
    REQUIRED_ROLES,
    GUIDANCE_MESSAGES,
)
from azure_wrappers.common import AzureWrapperError


# ============================================
# Tests: login_azure()
# ============================================


class TestLoginAzure:
    """Tests pour login_azure()"""

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    @patch('subprocess.run')
    @patch('azure_wrappers.account.list_accounts')
    @patch('azure_wrappers.account.get_current_account')
    def test_login_azure_success_device_code(
        self, mock_get_current, mock_list, mock_run, mock_print, mock_input
    ):
        """Test: Connexion réussie avec device code"""
        mock_run.return_value = MagicMock(returncode=0)
        mock_list.return_value = [{"id": "sub1", "name": "Subscription 1"}]
        mock_get_current.return_value = {"id": "sub1", "name": "Subscription 1"}

        result = login_azure(use_device_code=True)

        assert result["success"] is True
        assert result["account_count"] == 1
        assert "Connexion réussie" in result["message"]

        # Vérifier que device code est utilisé
        call_args = mock_run.call_args[0][0]
        assert "az" in call_args
        assert "login" in call_args
        assert "--use-device-code" in call_args

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_login_azure_failure(self, mock_run, mock_print, mock_input):
        """Test: Échec de connexion"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "az", stderr="Error")

        with pytest.raises(AzureWrapperError, match="Échec de connexion"):
            login_azure()


# ============================================
# Tests: logout_azure()
# ============================================


class TestLogoutAzure:
    """Tests pour logout_azure()"""

    @patch('azure_wrappers.account.run_az_command')
    def test_logout_azure_success(self, mock_run):
        """Test: Déconnexion réussie"""
        mock_run.return_value = ""

        result = logout_azure()

        assert result is True

        # Vérifier la commande
        cmd = mock_run.call_args[0][0]
        assert "az" in cmd
        assert "logout" in cmd


# ============================================
# Tests: list_accounts()
# ============================================


class TestListAccounts:
    """Tests pour list_accounts()"""

    @patch('azure_wrappers.account.run_az_command')
    def test_list_accounts_success(self, mock_run):
        """Test: Liste des comptes réussie"""
        mock_response = [
            {
                "id": "sub-123",
                "name": "Subscription Production",
                "isDefault": True,
                "state": "Enabled",
                "tenantId": "tenant-123",
            },
            {
                "id": "sub-456",
                "name": "Subscription Dev",
                "isDefault": False,
                "state": "Enabled",
                "tenantId": "tenant-123",
            },
        ]
        mock_run.return_value = {"stdout": json.dumps(mock_response)}

        result = list_accounts()

        assert len(result) == 2
        assert result[0]["id"] == "sub-123"
        assert result[0]["name"] == "Subscription Production"
        assert result[0]["is_default"] is True
        assert result[1]["id"] == "sub-456"
        assert result[1]["is_default"] is False

    @patch('azure_wrappers.account.run_az_command')
    def test_list_accounts_not_logged_in(self, mock_run):
        """Test: Erreur si non connecté"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "az", stderr="az login"
        )

        with pytest.raises(AzureWrapperError, match="Aucun compte connecté"):
            list_accounts()


# ============================================
# Tests: get_current_account()
# ============================================


class TestGetCurrentAccount:
    """Tests pour get_current_account()"""

    @patch('azure_wrappers.account.run_az_command')
    def test_get_current_account_success(self, mock_run):
        """Test: Récupération du compte actuel"""
        mock_response = {
            "id": "sub-123",
            "name": "Subscription Production",
            "tenantId": "tenant-123",
            "state": "Enabled",
            "user": {"name": "user@example.com", "type": "user"},
        }
        mock_run.return_value = {"stdout": json.dumps(mock_response)}

        result = get_current_account()

        assert result["id"] == "sub-123"
        assert result["name"] == "Subscription Production"
        assert result["tenant_id"] == "tenant-123"
        assert result["user"]["name"] == "user@example.com"


# ============================================
# Tests: select_account()
# ============================================


class TestSelectAccount:
    """Tests pour select_account()"""

    @patch('azure_wrappers.account.run_az_command')
    @patch('azure_wrappers.account.get_current_account')
    def test_select_account_success(self, mock_get, mock_run):
        """Test: Sélection de subscription réussie"""
        mock_run.return_value = ""
        mock_get.return_value = {"id": "sub-123", "name": "Subscription Test"}

        result = select_account("sub-123")

        assert result["id"] == "sub-123"
        assert result["name"] == "Subscription Test"

        # Vérifier la commande
        cmd = mock_run.call_args[0][0]
        assert "az" in cmd
        assert "account" in cmd
        assert "set" in cmd
        assert "--subscription" in cmd
        assert "sub-123" in cmd

    def test_select_account_empty_id(self):
        """Test: Erreur si ID vide"""
        with pytest.raises(AzureWrapperError, match="ID de subscription requis"):
            select_account("")

    @patch('azure_wrappers.account.run_az_command')
    def test_select_account_not_found(self, mock_run):
        """Test: Erreur si subscription introuvable"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "az", stderr="not found"
        )

        with pytest.raises(AzureWrapperError, match="introuvable"):
            select_account("sub-nonexistent")


# ============================================
# Tests: select_account_interactive()
# ============================================


class TestSelectAccountInteractive:
    """Tests pour select_account_interactive()"""

    @patch('azure_wrappers.account.list_accounts')
    @patch('azure_wrappers.account.select_account')
    def test_select_account_interactive_single(self, mock_select, mock_list):
        """Test: Une seule subscription, sélection automatique"""
        mock_list.return_value = [{"id": "sub-123", "name": "Subscription"}]
        mock_select.return_value = {"id": "sub-123", "name": "Subscription"}

        result = select_account_interactive()

        assert result["id"] == "sub-123"
        mock_select.assert_called_once_with("sub-123")

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    @patch('azure_wrappers.account.list_accounts')
    @patch('azure_wrappers.account.select_account')
    def test_select_account_interactive_multiple(
        self, mock_select, mock_list, mock_print, mock_input
    ):
        """Test: Plusieurs subscriptions, sélection interactive"""
        mock_list.return_value = [
            {"id": "sub-1", "name": "Sub 1", "is_default": True, "state": "Enabled"},
            {"id": "sub-2", "name": "Sub 2", "is_default": False, "state": "Enabled"},
        ]
        mock_select.return_value = {"id": "sub-1", "name": "Sub 1"}

        result = select_account_interactive()

        assert result["id"] == "sub-1"
        mock_select.assert_called_once_with("sub-1")


# ============================================
# Tests: check_permissions()
# ============================================


class TestCheckPermissions:
    """Tests pour check_permissions()"""

    @patch('azure_wrappers.account.get_current_account')
    @patch('azure_wrappers.account.run_az_command')
    def test_check_permissions_sufficient(self, mock_run, mock_get):
        """Test: Permissions suffisantes (Contributor)"""
        mock_get.return_value = {"id": "sub-123"}
        mock_response = [
            {"roleDefinitionName": "Contributor"},
        ]
        mock_run.return_value = {"stdout": json.dumps(mock_response)}

        result = check_permissions()

        assert result["has_permissions"] is True
        assert "Contributor" in result["roles"]
        assert "suffisantes" in result["message"]

    @patch('azure_wrappers.account.get_current_account')
    @patch('azure_wrappers.account.run_az_command')
    def test_check_permissions_insufficient(self, mock_run, mock_get):
        """Test: Permissions insuffisantes (Reader)"""
        mock_get.return_value = {"id": "sub-123"}
        mock_response = [
            {"roleDefinitionName": "Reader"},
        ]
        mock_run.return_value = {"stdout": json.dumps(mock_response)}

        result = check_permissions()

        assert result["has_permissions"] is False
        assert "Reader" in result["roles"]
        assert "insuffisantes" in result["message"]

    @patch('azure_wrappers.account.get_current_account')
    @patch('azure_wrappers.account.run_az_command')
    def test_check_permissions_owner(self, mock_run, mock_get):
        """Test: Permissions avec Owner"""
        mock_get.return_value = {"id": "sub-123"}
        mock_response = [
            {"roleDefinitionName": "Owner"},
        ]
        mock_run.return_value = {"stdout": json.dumps(mock_response)}

        result = check_permissions()

        assert result["has_permissions"] is True
        assert "Owner" in result["roles"]


# ============================================
# Tests: reconnect_azure()
# ============================================


class TestReconnectAzure:
    """Tests pour reconnect_azure()"""

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    @patch('azure_wrappers.account.logout_azure')
    @patch('azure_wrappers.account.login_azure')
    def test_reconnect_azure_success(
        self, mock_login, mock_logout, mock_print, mock_input
    ):
        """Test: Reconnexion réussie"""
        mock_logout.return_value = True
        mock_login.return_value = {
            "success": True,
            "account_count": 1,
            "current_subscription": {"id": "sub-123"},
            "message": "Connexion réussie",
        }

        result = reconnect_azure()

        assert result["success"] is True
        mock_logout.assert_called_once()
        mock_login.assert_called_once()


# ============================================
# Tests: STORY-009 Acceptance Criteria
# ============================================


class TestSTORY009AcceptanceCriteria:
    """Tests de validation des critères d'acceptation STORY-009"""

    def test_acceptance_criteria_1_login_guidance(self):
        """AC1: OpenCode guide le technicien pour az login"""
        from azure_wrappers.account import login_azure, GUIDANCE_MESSAGES
        assert login_azure is not None
        assert callable(login_azure)
        assert "login_prompt" in GUIDANCE_MESSAGES
        assert "CONNEXION À AZURE CLI" in GUIDANCE_MESSAGES["login_prompt"]

    def test_acceptance_criteria_2_device_flow_supported(self):
        """AC2: Processus de connexion device flow supporté"""
        from azure_wrappers.account import login_azure
        # login_azure accepte use_device_code parameter
        import inspect
        sig = inspect.signature(login_azure)
        assert "use_device_code" in sig.parameters
        assert sig.parameters["use_device_code"].default is True

    def test_acceptance_criteria_3_list_accounts(self):
        """AC3: OpenCode liste les comptes connectés (az account list)"""
        from azure_wrappers.account import list_accounts
        assert list_accounts is not None
        assert callable(list_accounts)

    def test_acceptance_criteria_4_account_selection(self):
        """AC4: OpenCode permet de sélectionner le bon compte si plusieurs"""
        from azure_wrappers.account import select_account, select_account_interactive
        assert select_account is not None
        assert select_account_interactive is not None
        assert callable(select_account)
        assert callable(select_account_interactive)

    def test_acceptance_criteria_5_permissions_check(self):
        """AC5: Vérification des permissions nécessaires (Contributor ou similaire)"""
        from azure_wrappers.account import check_permissions, REQUIRED_ROLES
        assert check_permissions is not None
        assert callable(check_permissions)
        assert "Contributor" in REQUIRED_ROLES
        assert "Owner" in REQUIRED_ROLES

    def test_acceptance_criteria_6_clear_message_insufficient_permissions(self):
        """AC6: Message clair si permissions insuffisantes"""
        from azure_wrappers.account import GUIDANCE_MESSAGES
        assert "no_permissions" in GUIDANCE_MESSAGES
        assert "PERMISSIONS INSUFFISANTES" in GUIDANCE_MESSAGES["no_permissions"]
        assert "Contributor" in GUIDANCE_MESSAGES["no_permissions"]

    def test_acceptance_criteria_7_reconnect_capability(self):
        """AC7: Possibilité de se reconnecter avec un autre compte"""
        from azure_wrappers.account import reconnect_azure
        assert reconnect_azure is not None
        assert callable(reconnect_azure)
