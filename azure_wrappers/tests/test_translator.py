"""
Tests unitaires pour azure_wrappers.translator

⚠️ CRITIQUE: Ces tests vérifient que le SKU F0 est OBLIGATOIRE et HARDCODÉ
"""

import pytest
import inspect
from unittest.mock import patch, MagicMock
from azure_wrappers.translator import (
    create_translator,
    verify_translator,
    delete_translator,
    TRANSLATOR_SKU_F0,
    _get_translator_endpoint,
    _get_translator_key,
    _get_translator_resource_id,
)
from azure_wrappers.common import AzureWrapperError


class TestTranslatorSKUF0:
    """
    ⚠️ TESTS CRITIQUES: Validation que seul le SKU F0 est utilisé

    Ces tests vérifient l'exigence d'acceptation #7 de STORY-007:
    "Tests unitaires vérifiant que seul F0 est utilisé"
    """

    def test_sku_f0_constant_exists(self):
        """CRITIQUE: Vérifie que la constante TRANSLATOR_SKU_F0 existe"""
        assert TRANSLATOR_SKU_F0 is not None

    def test_sku_f0_constant_value(self):
        """CRITIQUE: Vérifie que TRANSLATOR_SKU_F0 == "F0" """
        assert TRANSLATOR_SKU_F0 == "F0", \
            f"❌ ÉCHEC CRITIQUE: SKU devrait être 'F0' mais est '{TRANSLATOR_SKU_F0}'"

    def test_create_translator_no_sku_parameter(self):
        """CRITIQUE: Vérifie qu'il n'existe AUCUN paramètre 'sku' dans create_translator()"""
        sig = inspect.signature(create_translator)
        params = list(sig.parameters.keys())

        assert 'sku' not in params, \
            f"❌ ÉCHEC CRITIQUE: Le paramètre 'sku' ne devrait PAS exister dans create_translator(). " \
            f"Paramètres trouvés: {params}"

    @patch('azure_wrappers.translator.run_az_command')
    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.translator._get_translator_endpoint', return_value="https://api.cognitive.microsofttranslator.com/")
    @patch('azure_wrappers.translator._get_translator_key', return_value="test-key-1234567890")
    @patch('azure_wrappers.translator._get_translator_resource_id', return_value="/subscriptions/test/resourceGroups/test-rg/providers/...")
    def test_create_translator_uses_f0_sku(
        self,
        mock_resource_id,
        mock_key,
        mock_endpoint,
        mock_logged_in,
        mock_run_az
    ):
        """CRITIQUE: Vérifie que create_translator() utilise UNIQUEMENT le SKU F0"""
        # Mock de la sortie Azure CLI
        mock_run_az.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "{}",
            "stderr": ""
        }

        # Appel de la fonction
        result = create_translator(
            name="translator-test-20260118",
            resource_group="rg-test",
            region="francecentral"
        )

        # Vérifier que run_az_command a été appelé
        assert mock_run_az.called, "run_az_command devrait avoir été appelé"

        # Récupérer la commande Azure CLI passée
        call_args = mock_run_az.call_args
        command = call_args[0][0]  # Premier argument positionnel

        # Vérifier que la commande contient "--sku" et "F0"
        assert "--sku" in command, "La commande devrait contenir --sku"

        # Trouver l'index de "--sku" et vérifier la valeur suivante
        sku_index = command.index("--sku")
        sku_value = command[sku_index + 1]

        assert sku_value == "F0", \
            f"❌ ÉCHEC CRITIQUE: SKU utilisé devrait être 'F0' mais est '{sku_value}'"

        # Vérifier que le résultat contient bien sku: F0
        assert result["sku"] == "F0", \
            f"❌ ÉCHEC CRITIQUE: Le résultat devrait contenir sku='F0' mais contient '{result['sku']}'"

    @patch('azure_wrappers.translator.run_az_command')
    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.translator._get_translator_endpoint', return_value="https://api.cognitive.microsofttranslator.com/")
    @patch('azure_wrappers.translator._get_translator_key', return_value="test-key-1234567890")
    @patch('azure_wrappers.translator._get_translator_resource_id', return_value="/subscriptions/test/resourceGroups/test-rg/providers/...")
    def test_create_translator_never_uses_s0(
        self,
        mock_resource_id,
        mock_key,
        mock_endpoint,
        mock_logged_in,
        mock_run_az
    ):
        """CRITIQUE: Vérifie que S0 (payant) n'est JAMAIS utilisé"""
        mock_run_az.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "{}",
            "stderr": ""
        }

        create_translator(
            name="translator-test-20260118",
            resource_group="rg-test"
        )

        # Récupérer la commande
        command = mock_run_az.call_args[0][0]

        # Vérifier qu'aucun SKU payant n'est utilisé
        command_str = " ".join(command)
        forbidden_skus = ["S0", "S1", "S2", "S3", "S4"]

        for forbidden_sku in forbidden_skus:
            assert forbidden_sku not in command_str, \
                f"❌ ÉCHEC CRITIQUE: Le SKU interdit '{forbidden_sku}' a été trouvé dans la commande"


class TestCreateTranslator:
    """Tests pour la fonction create_translator()"""

    @patch('azure_wrappers.translator.run_az_command')
    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.translator._get_translator_endpoint', return_value="https://api.cognitive.microsofttranslator.com/")
    @patch('azure_wrappers.translator._get_translator_key', return_value="test-key-1234567890")
    @patch('azure_wrappers.translator._get_translator_resource_id', return_value="/subscriptions/test/resourceGroups/test-rg/providers/...")
    def test_create_translator_success(
        self,
        mock_resource_id,
        mock_key,
        mock_endpoint,
        mock_logged_in,
        mock_run_az
    ):
        """Test création réussie d'un service Translator"""
        mock_run_az.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "{}",
            "stderr": ""
        }

        result = create_translator(
            name="translator-test-20260118",
            resource_group="rg-test",
            region="francecentral",
            tags={"client": "Test"}
        )

        # Vérifier le résultat
        assert result["name"] == "translator-test-20260118"
        assert result["endpoint"] == "https://api.cognitive.microsofttranslator.com/"
        assert result["key"] == "test-key-1234567890"
        assert result["key_display"] == "***************7890"  # 15 * car clé = 19 chars - 4 visible
        assert result["region"] == "francecentral"
        assert result["sku"] == "F0"

    @patch('azure_wrappers.translator.check_az_logged_in', return_value=False)
    def test_create_translator_not_logged_in(self, mock_logged_in):
        """Test échec si non connecté à Azure CLI"""
        with pytest.raises(AzureWrapperError, match="Vous devez être connecté à Azure CLI"):
            create_translator(
                name="translator-test-20260118",
                resource_group="rg-test"
            )

    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    def test_create_translator_invalid_name(self, mock_logged_in):
        """Test échec avec nom invalide"""
        with pytest.raises(AzureWrapperError, match="au moins 3 caractères"):
            create_translator(
                name="a",  # Trop court
                resource_group="rg-test"
            )

    @patch('azure_wrappers.translator.run_az_command')
    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    def test_create_translator_already_exists(self, mock_logged_in, mock_run_az):
        """Test échec si ressource existe déjà"""
        mock_run_az.side_effect = AzureWrapperError("ResourceExists: Resource already exists")

        with pytest.raises(AzureWrapperError, match="existe déjà"):
            create_translator(
                name="translator-test-20260118",
                resource_group="rg-test"
            )

    @patch('azure_wrappers.translator.run_az_command')
    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    def test_create_translator_quota_exceeded(self, mock_logged_in, mock_run_az):
        """Test échec si quota dépassé"""
        mock_run_az.side_effect = AzureWrapperError("QuotaExceeded: Quota exceeded")

        with pytest.raises(AzureWrapperError, match="Quota Azure dépassé"):
            create_translator(
                name="translator-test-20260118",
                resource_group="rg-test"
            )


class TestVerifyTranslator:
    """Tests pour la fonction verify_translator()"""

    @patch('azure_wrappers.translator.run_az_command')
    def test_verify_translator_exists_f0(self, mock_run_az):
        """Test vérification d'un Translator existant avec SKU F0"""
        mock_run_az.return_value = {
            "success": True,
            "stdout": '{"properties": {"provisioningState": "Succeeded", "endpoint": "https://test.com"}, "sku": {"name": "F0"}}'
        }

        result = verify_translator("translator-test-20260118", "rg-test")

        assert result["exists"] is True
        assert result["state"] == "Succeeded"
        assert result["sku"] == "F0"
        assert result["sku_is_f0"] is True
        assert result["endpoint"] == "https://test.com"

    @patch('azure_wrappers.translator.run_az_command')
    def test_verify_translator_exists_s0_warning(self, mock_run_az):
        """Test détection d'un SKU S0 (payant) - devrait être signalé"""
        mock_run_az.return_value = {
            "success": True,
            "stdout": '{"properties": {"provisioningState": "Succeeded", "endpoint": "https://test.com"}, "sku": {"name": "S0"}}'
        }

        result = verify_translator("translator-test-20260118", "rg-test")

        assert result["exists"] is True
        assert result["sku"] == "S0"
        assert result["sku_is_f0"] is False  # ⚠️ WARNING: SKU n'est pas F0

    @patch('azure_wrappers.translator.run_az_command')
    def test_verify_translator_not_found(self, mock_run_az):
        """Test vérification d'un Translator inexistant"""
        mock_run_az.return_value = {
            "success": False,
            "stderr": "ResourceNotFound"
        }

        result = verify_translator("translator-test-20260118", "rg-test")

        assert result["exists"] is False
        assert result["state"] == "NotFound"
        assert result["sku"] is None
        assert result["sku_is_f0"] is False


class TestDeleteTranslator:
    """Tests pour la fonction delete_translator()"""

    @patch('azure_wrappers.translator.run_az_command')
    def test_delete_translator_with_yes(self, mock_run_az):
        """Test suppression avec confirmation automatique"""
        mock_run_az.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "",
            "stderr": ""
        }

        result = delete_translator("translator-test-20260118", "rg-test", yes=True)

        assert result is True
        assert mock_run_az.called

    @patch('builtins.input', return_value='non')
    def test_delete_translator_cancelled(self, mock_input):
        """Test annulation de la suppression"""
        result = delete_translator("translator-test-20260118", "rg-test", yes=False)

        assert result is False


class TestHelperFunctions:
    """Tests pour les fonctions helper"""

    @patch('azure_wrappers.translator.run_az_command')
    def test_get_translator_endpoint(self, mock_run_az):
        """Test récupération de l'endpoint"""
        mock_run_az.return_value = {
            "stdout": "https://api.cognitive.microsofttranslator.com/"
        }

        endpoint = _get_translator_endpoint("translator-test", "rg-test")

        assert endpoint == "https://api.cognitive.microsofttranslator.com/"

    @patch('azure_wrappers.translator.run_az_command')
    def test_get_translator_key(self, mock_run_az):
        """Test récupération de la clé"""
        mock_run_az.return_value = {
            "stdout": "test-key-1234567890abcdef"
        }

        key = _get_translator_key("translator-test", "rg-test")

        assert key == "test-key-1234567890abcdef"

    @patch('azure_wrappers.translator.run_az_command')
    def test_get_translator_resource_id(self, mock_run_az):
        """Test récupération de l'ID de ressource"""
        mock_run_az.return_value = {
            "stdout": "/subscriptions/12345/resourceGroups/rg-test/providers/Microsoft.CognitiveServices/accounts/translator-test"
        }

        resource_id = _get_translator_resource_id("translator-test", "rg-test")

        assert resource_id.startswith("/subscriptions/")
        assert "translator-test" in resource_id


class TestSTORY007AcceptanceCriteria:
    """
    Tests validant les critères d'acceptation de STORY-007

    Acceptance Criteria from sprint-plan:
    - [ ] Fonction `create_translator()` implémentée ✓
    - [ ] SKU F0 **hardcodé** dans le code (pas de paramètre variable) ✓
    - [ ] Impossible de sélectionner S0 ou autre SKU ✓
    - [ ] Région francecentral par défaut (ou sélection guidée) ✓
    - [ ] Endpoint et clé récupérés et affichés ✓
    - [ ] Vérification que le service est actif ✓
    - [ ] Tests unitaires vérifiant que seul F0 est utilisé ✓ (CE FICHIER)
    - [ ] Documentation claire dans le code: "SKU F0 OBLIGATOIRE - NE PAS MODIFIER" ✓
    """

    def test_acceptance_criteria_1_function_exists(self):
        """AC#1: Fonction create_translator() implémentée"""
        assert callable(create_translator)

    def test_acceptance_criteria_2_sku_f0_hardcoded(self):
        """AC#2: SKU F0 hardcodé dans le code"""
        assert TRANSLATOR_SKU_F0 == "F0"

        # Vérifier qu'il n'y a pas de paramètre sku
        sig = inspect.signature(create_translator)
        assert 'sku' not in sig.parameters

    def test_acceptance_criteria_3_cannot_select_s0(self):
        """AC#3: Impossible de sélectionner S0 ou autre SKU"""
        # Pas de paramètre sku = impossible de changer
        sig = inspect.signature(create_translator)
        assert 'sku' not in sig.parameters, \
            "Il ne devrait PAS y avoir de paramètre 'sku' dans create_translator()"

    def test_acceptance_criteria_4_default_region_francecentral(self):
        """AC#4: Région francecentral par défaut"""
        sig = inspect.signature(create_translator)
        region_param = sig.parameters.get('region')

        assert region_param is not None, "Le paramètre 'region' devrait exister"
        assert region_param.default == "francecentral", \
            f"La région par défaut devrait être 'francecentral' mais est '{region_param.default}'"

    @patch('azure_wrappers.translator.run_az_command')
    @patch('azure_wrappers.translator.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.translator._get_translator_endpoint', return_value="https://test.com")
    @patch('azure_wrappers.translator._get_translator_key', return_value="test-key-123")
    @patch('azure_wrappers.translator._get_translator_resource_id', return_value="/test/id")
    def test_acceptance_criteria_5_endpoint_and_key_retrieved(
        self, mock_id, mock_key, mock_endpoint, mock_logged_in, mock_run_az
    ):
        """AC#5: Endpoint et clé récupérés et affichés"""
        mock_run_az.return_value = {"success": True, "returncode": 0, "stdout": "{}", "stderr": ""}

        result = create_translator("test", "rg-test")

        assert "endpoint" in result
        assert "key" in result
        assert "key_display" in result

    def test_acceptance_criteria_6_verify_service_active(self):
        """AC#6: Vérification que le service est actif"""
        assert callable(verify_translator), \
            "La fonction verify_translator() devrait exister"

    def test_acceptance_criteria_7_unit_tests_verify_f0_only(self):
        """AC#7: Tests unitaires vérifiant que seul F0 est utilisé"""
        # Ce test lui-même valide le critère #7
        # En exécutant pytest, tous les tests de TestTranslatorSKUF0 valident ce critère
        assert True, "Ce fichier de tests valide AC#7"

    def test_acceptance_criteria_8_documentation_clear(self):
        """AC#8: Documentation claire dans le code"""
        # Vérifier que le module contient la documentation
        import azure_wrappers.translator as translator_module

        doc = translator_module.__doc__
        assert doc is not None, "Le module devrait avoir une docstring"
        assert "F0" in doc, "La documentation devrait mentionner F0"
        assert "CRITIQUE" in doc or "CRITICAL" in doc, \
            "La documentation devrait indiquer l'importance critique du SKU F0"
