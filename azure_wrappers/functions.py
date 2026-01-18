"""
Azure Functions Wrapper - Déploiement Azure Functions App

Ce module fournit des wrappers Python pour automatiser le déploiement
d'Azure Functions App via Azure CLI.

Author: Aux Petits Oignons Team
Version: 1.2.0
Story: STORY-008 (Wrapper Python Azure CLI - Déploiement Azure Functions)
"""

import json
import os
import subprocess
import time
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import requests

from .common import (
    run_az_command,
    validate_resource_name,
    AzureWrapperError,
    check_az_logged_in,
    sanitize_credential,
)

# ============================================
# Constants
# ============================================

FUNCTION_RUNTIME_DEFAULT = "python"
FUNCTION_RUNTIME_VERSION_DEFAULT = "3.11"
FUNCTION_OS_DEFAULT = "Linux"
FUNCTION_SKU_DEFAULT = "Y1"  # Consumption Plan (Serverless)
FUNCTION_PLAN_DEFAULT = "Consumption"

# Functions à déployer (6 functions)
EXPECTED_FUNCTIONS = [
    "start_translation",
    "check_status",
    "get_result",
    "health",
    "languages",
    "formats",
]

# ============================================
# Function App Creation
# ============================================


def create_function_app(
    name: str,
    resource_group: str,
    storage_account: str,
    region: str = "francecentral",
    runtime: str = FUNCTION_RUNTIME_DEFAULT,
    runtime_version: str = FUNCTION_RUNTIME_VERSION_DEFAULT,
    tags: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Crée une Azure Function App avec runtime Python 3.11.

    Args:
        name: Nom de la Function App (doit être globalement unique)
        resource_group: Nom du Resource Group
        storage_account: Nom du Storage Account (requis par Functions)
        region: Région Azure (défaut: francecentral)
        runtime: Runtime de la Function App (défaut: python)
        runtime_version: Version du runtime (défaut: 3.11)
        tags: Tags à appliquer à la ressource

    Returns:
        Dict avec:
            - name: Nom de la Function App
            - id: Resource ID complet
            - default_hostname: URL par défaut (*.azurewebsites.net)
            - state: État de provisioning
            - runtime: Runtime configuré
            - runtime_version: Version du runtime
            - region: Région de déploiement
            - storage_account: Storage Account associé

    Raises:
        AzureWrapperError: Si création échoue
    """
    if not check_az_logged_in():
        raise AzureWrapperError("Vous devez être connecté à Azure CLI")

    validate_resource_name(name, "Function App")

    # Vérifier que le Storage Account est fourni
    if not storage_account:
        raise AzureWrapperError("Un Storage Account est requis pour créer une Function App")

    # Step 1: Créer la Function App avec Consumption Plan
    cmd = [
        "az", "functionapp", "create",
        "--name", name,
        "--resource-group", resource_group,
        "--storage-account", storage_account,
        "--runtime", runtime,
        "--runtime-version", runtime_version,
        "--functions-version", "4",
        "--os-type", FUNCTION_OS_DEFAULT,
        "--consumption-plan-location", region,
        "--output", "json",
    ]

    # Ajouter les tags si fournis
    if tags:
        tags_str = " ".join([f"{k}={v}" for k, v in tags.items()])
        cmd.extend(["--tags", tags_str])

    try:
        result = run_az_command(cmd)
        data = json.loads(result["stdout"])

        # Extraire les informations principales
        function_app_info = {
            "name": data.get("name", name),
            "id": data.get("id", ""),
            "default_hostname": data.get("defaultHostName", ""),
            "state": data.get("state", ""),
            "runtime": runtime,
            "runtime_version": runtime_version,
            "region": region,
            "storage_account": storage_account,
        }

        return function_app_info

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)

        # Gestion des erreurs spécifiques
        if "WebsiteAlreadyExists" in error_msg or "AlreadyExists" in error_msg:
            raise AzureWrapperError(f"La Function App '{name}' existe déjà")
        elif "ResourceGroupNotFound" in error_msg:
            raise AzureWrapperError(f"Le Resource Group '{resource_group}' n'existe pas")
        elif "StorageAccountNotFound" in error_msg:
            raise AzureWrapperError(f"Le Storage Account '{storage_account}' n'existe pas")
        elif "QuotaExceeded" in error_msg or "Quota" in error_msg:
            raise AzureWrapperError("Quota Azure dépassé pour les Function Apps")
        else:
            raise AzureWrapperError(f"Échec de création de la Function App: {error_msg}")


# ============================================
# App Settings Configuration
# ============================================


def configure_app_settings(
    name: str,
    resource_group: str,
    settings: Dict[str, str],
) -> bool:
    """
    Configure les variables d'environnement (app settings) d'une Function App.

    Args:
        name: Nom de la Function App
        resource_group: Nom du Resource Group
        settings: Dictionnaire des variables d'environnement à configurer
                  Ex: {"KEY": "value", "AZURE_ACCOUNT_NAME": "storage123"}

    Returns:
        True si configuration réussie

    Raises:
        AzureWrapperError: Si configuration échoue
    """
    if not check_az_logged_in():
        raise AzureWrapperError("Vous devez être connecté à Azure CLI")

    if not settings:
        raise AzureWrapperError("Aucune variable d'environnement fournie")

    # Construire les settings au format Azure CLI
    # Format: "KEY1=value1" "KEY2=value2"
    settings_list = [f"{k}={v}" for k, v in settings.items()]

    cmd = [
        "az", "functionapp", "config", "appsettings", "set",
        "--name", name,
        "--resource-group", resource_group,
        "--settings",
    ] + settings_list

    try:
        run_az_command(cmd)
        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise AzureWrapperError(f"Échec de configuration des app settings: {error_msg}")


# ============================================
# Function Deployment
# ============================================


def deploy_functions(
    name: str,
    resource_group: str,
    source_dir: str,
    timeout: int = 600,
) -> Dict[str, Any]:
    """
    Déploie les Azure Functions depuis un dossier local.

    Cette fonction:
    1. Crée un fichier ZIP du code source
    2. Déploie le ZIP via Azure CLI
    3. Attend que le déploiement soit terminé

    Args:
        name: Nom de la Function App
        resource_group: Nom du Resource Group
        source_dir: Chemin vers le dossier contenant le code (ex: /app/src)
        timeout: Timeout maximum pour le déploiement (secondes, défaut: 600)

    Returns:
        Dict avec:
            - status: État du déploiement (success/failed)
            - deployment_id: ID du déploiement
            - duration_seconds: Durée du déploiement

    Raises:
        AzureWrapperError: Si déploiement échoue
    """
    if not check_az_logged_in():
        raise AzureWrapperError("Vous devez être connecté à Azure CLI")

    # Vérifier que le dossier source existe
    source_path = Path(source_dir)
    if not source_path.exists():
        raise AzureWrapperError(f"Le dossier source '{source_dir}' n'existe pas")

    # Vérifier qu'il y a un host.json (fichier requis pour Azure Functions)
    if not (source_path / "host.json").exists():
        raise AzureWrapperError(f"Le fichier 'host.json' est manquant dans {source_dir}")

    start_time = time.time()

    try:
        # Step 1: Créer un fichier ZIP du code source
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
            zip_path = tmp_zip.name

        _create_deployment_zip(source_path, zip_path)

        # Step 2: Déployer le ZIP
        cmd = [
            "az", "functionapp", "deployment", "source", "config-zip",
            "--name", name,
            "--resource-group", resource_group,
            "--src", zip_path,
            "--timeout", str(timeout),
            "--output", "json",
        ]

        result = run_az_command(cmd)
        data = json.loads(result["stdout"])

        # Nettoyer le fichier ZIP temporaire
        os.remove(zip_path)

        duration = time.time() - start_time

        return {
            "status": data.get("status", "success"),
            "deployment_id": data.get("id", ""),
            "duration_seconds": round(duration, 2),
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)

        # Nettoyer le ZIP en cas d'erreur
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)

        if "DeploymentFailed" in error_msg:
            raise AzureWrapperError(f"Déploiement échoué: {error_msg}")
        elif "Timeout" in error_msg:
            raise AzureWrapperError(f"Timeout de déploiement (>{timeout}s): {error_msg}")
        else:
            raise AzureWrapperError(f"Échec de déploiement: {error_msg}")


def _create_deployment_zip(source_dir: Path, zip_path: str) -> None:
    """
    Crée un fichier ZIP du code source pour le déploiement.

    Ignore les dossiers: __pycache__, .git, .venv, venv, tests, .pytest_cache

    Args:
        source_dir: Chemin vers le dossier source
        zip_path: Chemin où créer le fichier ZIP
    """
    ignored_dirs = {"__pycache__", ".git", ".venv", "venv", "tests", ".pytest_cache", "node_modules"}

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob("*"):
            # Ignorer les dossiers spécifiques
            if any(ignored in file_path.parts for ignored in ignored_dirs):
                continue

            # Ignorer les fichiers .pyc
            if file_path.suffix == ".pyc":
                continue

            # Ajouter uniquement les fichiers
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)


# ============================================
# Health Check
# ============================================


def check_health(
    function_app_url: str,
    timeout: int = 30,
    retry_count: int = 3,
    retry_delay: int = 5,
) -> Dict[str, Any]:
    """
    Vérifie le health endpoint d'une Function App.

    Fait des retries car la Function App peut prendre du temps à démarrer
    après le déploiement.

    Args:
        function_app_url: URL de base de la Function App (ex: https://myapp.azurewebsites.net)
        timeout: Timeout pour chaque requête (secondes, défaut: 30)
        retry_count: Nombre de tentatives (défaut: 3)
        retry_delay: Délai entre les tentatives (secondes, défaut: 5)

    Returns:
        Dict avec:
            - status: État du health check (healthy/unhealthy)
            - status_code: Code HTTP retourné
            - response_time_ms: Temps de réponse en millisecondes
            - message: Message descriptif

    Raises:
        AzureWrapperError: Si health check échoue après tous les retries
    """
    # Construire l'URL du health endpoint
    health_url = f"{function_app_url.rstrip('/')}/api/health"

    last_error = None

    for attempt in range(1, retry_count + 1):
        try:
            start_time = time.time()
            response = requests.get(health_url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # en ms

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "status_code": 200,
                    "response_time_ms": round(response_time, 2),
                    "message": "Health check réussi",
                }
            else:
                last_error = f"Status code {response.status_code}"

        except requests.exceptions.Timeout:
            last_error = f"Timeout après {timeout}s"
        except requests.exceptions.ConnectionError:
            last_error = "Erreur de connexion"
        except Exception as e:
            last_error = str(e)

        # Retry si ce n'est pas la dernière tentative
        if attempt < retry_count:
            time.sleep(retry_delay)

    # Échec après tous les retries
    raise AzureWrapperError(
        f"Health check échoué après {retry_count} tentatives: {last_error}"
    )


# ============================================
# Function App Verification
# ============================================


def verify_function_app(
    name: str,
    resource_group: str,
) -> Dict[str, Any]:
    """
    Vérifie qu'une Function App existe et récupère ses informations.

    Args:
        name: Nom de la Function App
        resource_group: Nom du Resource Group

    Returns:
        Dict avec:
            - exists: True si existe
            - state: État de la Function App
            - default_hostname: URL par défaut
            - runtime: Runtime configuré
            - functions: Liste des functions déployées

    Raises:
        AzureWrapperError: Si vérification échoue
    """
    if not check_az_logged_in():
        raise AzureWrapperError("Vous devez être connecté à Azure CLI")

    cmd = [
        "az", "functionapp", "show",
        "--name", name,
        "--resource-group", resource_group,
        "--output", "json",
    ]

    try:
        result = run_az_command(cmd)
        data = json.loads(result["stdout"])

        # Lister les functions déployées
        functions_list = _list_deployed_functions(name, resource_group)

        return {
            "exists": True,
            "state": data.get("state", ""),
            "default_hostname": data.get("defaultHostName", ""),
            "runtime": data.get("kind", ""),
            "functions": functions_list,
        }

    except subprocess.CalledProcessError:
        return {
            "exists": False,
            "state": "",
            "default_hostname": "",
            "runtime": "",
            "functions": [],
        }


def _list_deployed_functions(name: str, resource_group: str) -> List[str]:
    """
    Liste les functions déployées dans une Function App.

    Args:
        name: Nom de la Function App
        resource_group: Nom du Resource Group

    Returns:
        Liste des noms de functions
    """
    cmd = [
        "az", "functionapp", "function", "list",
        "--name", name,
        "--resource-group", resource_group,
        "--output", "json",
    ]

    try:
        result = run_az_command(cmd)
        data = json.loads(result["stdout"])
        return [f.get("name", "") for f in data]
    except:
        return []


# ============================================
# Function App Deletion
# ============================================


def delete_function_app(
    name: str,
    resource_group: str,
    confirm: bool = False,
) -> bool:
    """
    Supprime une Function App.

    Args:
        name: Nom de la Function App
        resource_group: Nom du Resource Group
        confirm: Confirmation explicite requise (sécurité)

    Returns:
        True si suppression réussie

    Raises:
        AzureWrapperError: Si suppression échoue ou confirmation manquante
    """
    if not check_az_logged_in():
        raise AzureWrapperError("Vous devez être connecté à Azure CLI")

    if not confirm:
        raise AzureWrapperError(
            "La suppression d'une Function App nécessite une confirmation explicite (confirm=True)"
        )

    cmd = [
        "az", "functionapp", "delete",
        "--name", name,
        "--resource-group", resource_group,
        "--yes",
    ]

    try:
        run_az_command(cmd)
        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)

        if "ResourceNotFound" in error_msg:
            raise AzureWrapperError(f"La Function App '{name}' n'existe pas")
        else:
            raise AzureWrapperError(f"Échec de suppression: {error_msg}")
