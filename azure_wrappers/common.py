"""
Common utilities for Azure Wrappers

Ce module contient les fonctions communes utilisées par tous les wrappers Azure:
- Gestion d'erreurs
- Sanitisation des credentials
- Validation des paramètres
- Exécution sécurisée des commandes Azure CLI
"""

import subprocess
import json
import re
from typing import Dict, Any, Optional, List


class AzureWrapperError(Exception):
    """Exception personnalisée pour les erreurs des wrappers Azure"""
    pass


def sanitize_credential(credential: str, visible_chars: int = 4) -> str:
    """
    Masque un credential en ne laissant visible que les derniers caractères

    Args:
        credential: Le credential à masquer (clé API, secret, token, etc.)
        visible_chars: Nombre de caractères à laisser visibles à la fin

    Returns:
        Credential masqué (ex: "****************ABCD")

    Example:
        >>> sanitize_credential("sk-1234567890abcdefghijklmnop", 4)
        "****************mnop"
    """
    if not credential or len(credential) <= visible_chars:
        return "*" * 16

    masked_length = len(credential) - visible_chars
    return ("*" * min(masked_length, 16)) + credential[-visible_chars:]


def run_az_command(
    command: List[str],
    capture_output: bool = True,
    check: bool = True,
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Exécute une commande Azure CLI de manière sécurisée

    Args:
        command: Liste des arguments de la commande (ex: ["az", "group", "list"])
        capture_output: Capturer stdout et stderr
        check: Lever une exception si le code de retour != 0
        timeout: Timeout en secondes (défaut: 5 minutes)

    Returns:
        Dict avec:
            - returncode: Code de retour
            - stdout: Sortie standard (si capture_output=True)
            - stderr: Sortie erreur (si capture_output=True)
            - success: Boolean indiquant le succès

    Raises:
        AzureWrapperError: Si la commande échoue et check=True
    """
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=False,  # On gère check manuellement
            timeout=timeout,
        )

        success = result.returncode == 0

        if check and not success:
            # Extraire un message d'erreur utile du stderr
            error_msg = result.stderr.strip() if result.stderr else "Erreur inconnue"
            raise AzureWrapperError(
                f"Commande Azure CLI échouée (code: {result.returncode}): {error_msg}"
            )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "success": success,
        }

    except subprocess.TimeoutExpired as e:
        raise AzureWrapperError(
            f"Timeout ({timeout}s) dépassé pour la commande Azure CLI"
        ) from e

    except FileNotFoundError as e:
        raise AzureWrapperError(
            "Azure CLI n'est pas installé ou n'est pas dans le PATH. "
            "Installez Azure CLI: https://learn.microsoft.com/cli/azure/install-azure-cli"
        ) from e

    except Exception as e:
        raise AzureWrapperError(
            f"Erreur inattendue lors de l'exécution de la commande Azure CLI: {str(e)}"
        ) from e


def validate_resource_name(name: str, resource_type: str = "resource") -> None:
    """
    Valide qu'un nom de ressource Azure respecte les conventions de nommage

    Args:
        name: Nom de la ressource à valider
        resource_type: Type de ressource (pour message d'erreur plus clair)

    Raises:
        AzureWrapperError: Si le nom est invalide

    Rules:
        - Alphanumérique et tirets uniquement
        - Commence et finit par une lettre ou un chiffre
        - 3-63 caractères (dépend du type mais 3-63 est sûr pour la plupart)
    """
    if not name:
        raise AzureWrapperError(f"Le nom de {resource_type} ne peut pas être vide")

    if len(name) < 3:
        raise AzureWrapperError(
            f"Le nom de {resource_type} doit contenir au moins 3 caractères (fourni: '{name}')"
        )

    if len(name) > 63:
        raise AzureWrapperError(
            f"Le nom de {resource_type} ne peut pas dépasser 63 caractères (fourni: {len(name)} caractères)"
        )

    # Pattern: commence et finit par alphanumérique, contient seulement alphanum et tirets
    if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", name, re.IGNORECASE):
        raise AzureWrapperError(
            f"Le nom de {resource_type} '{name}' est invalide. "
            "Il doit commencer et finir par une lettre ou un chiffre, "
            "et contenir uniquement des lettres, chiffres et tirets."
        )


def validate_azure_region(region: str) -> None:
    """
    Valide qu'une région Azure est dans un format acceptable

    Args:
        region: Région Azure (ex: "francecentral", "westeurope")

    Raises:
        AzureWrapperError: Si la région est invalide

    Note:
        Cette validation est basique (format). Pour vérifier que la région
        existe vraiment, utiliser: az account list-locations
    """
    if not region:
        raise AzureWrapperError("La région Azure ne peut pas être vide")

    # Les régions Azure sont généralement en minuscules sans espaces
    if not re.match(r"^[a-z0-9]+$", region):
        raise AzureWrapperError(
            f"La région Azure '{region}' semble invalide. "
            "Format attendu: minuscules sans espaces (ex: 'francecentral', 'westeurope')"
        )


def parse_az_json_output(stdout: str) -> Any:
    """
    Parse la sortie JSON d'une commande Azure CLI

    Args:
        stdout: Sortie standard de la commande az (format JSON)

    Returns:
        Objet Python (dict, list, etc.) parsé depuis JSON

    Raises:
        AzureWrapperError: Si le parsing JSON échoue
    """
    if not stdout or not stdout.strip():
        raise AzureWrapperError("Sortie JSON vide de la commande Azure CLI")

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise AzureWrapperError(
            f"Impossible de parser la sortie JSON de Azure CLI: {e}\n"
            f"Sortie reçue (premiers 200 chars): {stdout[:200]}"
        ) from e


def check_az_logged_in() -> bool:
    """
    Vérifie si l'utilisateur est connecté à Azure CLI

    Returns:
        True si connecté, False sinon

    Note:
        Ne lève pas d'exception, retourne simplement un booléen
    """
    try:
        result = run_az_command(
            ["az", "account", "show"],
            check=False,
        )
        return result["success"]
    except Exception:
        return False


def get_current_subscription() -> Optional[Dict[str, Any]]:
    """
    Récupère la subscription Azure actuellement sélectionnée

    Returns:
        Dict avec les infos de subscription (id, name, tenantId, etc.)
        ou None si non connecté

    Example:
        {
            "id": "12345678-1234-1234-1234-123456789012",
            "name": "Ma Subscription",
            "tenantId": "87654321-4321-4321-4321-210987654321",
            "state": "Enabled",
            ...
        }
    """
    try:
        result = run_az_command(
            ["az", "account", "show"],
            check=True,
        )
        return parse_az_json_output(result["stdout"])
    except AzureWrapperError:
        return None
