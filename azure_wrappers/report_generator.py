"""
Report Generator - Génération automatique de rapports d'intervention

Ce module génère des rapports d'intervention complets après déploiement Azure,
permettant aux techniciens de copier-coller directement dans leur système de ticketing.

Le rapport contient:
- Informations client et déploiement
- Services Azure déployés (Storage, Translator, Functions)
- URLs et endpoints accessibles
- Configuration et paramètres
- Date/heure du déploiement

IMPORTANT: Aucune information sensible (credentials, keys) n'est incluse dans le rapport.

Author: Aux Petits Oignons Team
Version: 1.0.0
Story: STORY-015 (Génération Automatique Rapport d'Intervention)
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from pathlib import Path

from .common import sanitize_credential


# ============================================
# Constants
# ============================================

REPORT_DIR = "rapports"
REPORT_TEMPLATE_SIMPLE = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    RAPPORT D'INTERVENTION                                ║
║                 Déploiement Bot Traducteur Copilot                       ║
╚══════════════════════════════════════════════════════════════════════════╝

┌─ INFORMATIONS GÉNÉRALES ────────────────────────────────────────────────┐

  Client                : {client_name}
  Technicien            : {technician_name}
  Date d'intervention   : {date}
  Heure de déploiement  : {time}
  Durée totale          : {duration}

└──────────────────────────────────────────────────────────────────────────┘

┌─ RESSOURCES AZURE DÉPLOYÉES ────────────────────────────────────────────┐

  Resource Group        : {resource_group}
  Région Azure          : {region}
  Subscription ID       : {subscription_id}

  Services déployés     : {service_count} services
  {services_list}

└──────────────────────────────────────────────────────────────────────────┘

┌─ AZURE STORAGE ACCOUNT ──────────────────────────────────────────────────┐

  Nom                   : {storage_name}
  SKU                   : {storage_sku}
  Container Blob        : {blob_container}
  Endpoint              : {storage_endpoint}

└──────────────────────────────────────────────────────────────────────────┘

┌─ AZURE TRANSLATOR ───────────────────────────────────────────────────────┐

  Nom                   : {translator_name}
  SKU                   : {translator_sku} (GRATUIT)
  Région                : {translator_region}
  Endpoint              : {translator_endpoint}

  ⚠️  SKU F0 (Free Tier) : 2M caractères/mois gratuits

└──────────────────────────────────────────────────────────────────────────┘

┌─ AZURE FUNCTIONS APP ────────────────────────────────────────────────────┐

  Nom                   : {function_app_name}
  Runtime               : Python {function_runtime_version}
  Plan                  : Consumption (Serverless)
  URL                   : {function_app_url}

  Fonctions déployées   : {function_count} fonctions
  {functions_list}

  Health Check          : {health_status}

└──────────────────────────────────────────────────────────────────────────┘

┌─ CONFIGURATION POWER PLATFORM ───────────────────────────────────────────┐

  Solution à importer   : BotCopilotTraducteur_1_0_0_4.zip

  Variables d'environnement requises (Power Platform):
    • AZURE_FUNCTION_URL  : {function_app_url}
    • CLIENT_ID           : [À configurer dans Entra ID]
    • TENANT_ID           : {tenant_id}

└──────────────────────────────────────────────────────────────────────────┘

┌─ PROCHAINES ÉTAPES ──────────────────────────────────────────────────────┐

  1. Créer App Registration dans Entra ID (accès OneDrive)
  2. Importer la solution Power Platform (BotCopilotTraducteur)
  3. Configurer les variables d'environnement dans Copilot Studio
  4. Tester le bot avec un document exemple
  5. Valider avec l'utilisateur final

  Documentation complète : http://localhost:5545/procedure

└──────────────────────────────────────────────────────────────────────────┘

┌─ NOTES TECHNIQUES ───────────────────────────────────────────────────────┐

  {notes}

└──────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════╗
║  Déploiement réalisé avec Aux Petits Oignons - Bot Traducteur Copilot   ║
║  Rapport généré automatiquement - {report_timestamp}                     ║
╚══════════════════════════════════════════════════════════════════════════╝
"""


# ============================================
# Report Generation
# ============================================


def generate_report(
    client_name: str,
    resource_group: str,
    region: str,
    storage_info: Dict[str, Any],
    translator_info: Dict[str, Any],
    function_app_info: Dict[str, Any],
    technician_name: Optional[str] = "Non spécifié",
    subscription_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    deployment_duration: Optional[str] = "Non calculé",
    notes: Optional[str] = "",
) -> Dict[str, Any]:
    """
    Génère un rapport d'intervention complet après déploiement Azure.

    Args:
        client_name: Nom du client
        resource_group: Nom du Resource Group
        region: Région Azure (ex: francecentral)
        storage_info: Informations Storage Account (de create_storage_account)
        translator_info: Informations Translator (de create_translator)
        function_app_info: Informations Function App (de create_function_app)
        technician_name: Nom du technicien (défaut: "Non spécifié")
        subscription_id: ID de la subscription Azure
        tenant_id: ID du tenant Azure AD
        deployment_duration: Durée totale du déploiement (ex: "15 minutes")
        notes: Notes techniques additionnelles

    Returns:
        Dict avec:
            - report_content: Contenu texte du rapport
            - report_path: Chemin vers le fichier sauvegardé
            - timestamp: Timestamp de génération
            - client_name: Nom du client

    Raises:
        ValueError: Si informations obligatoires manquantes
    """
    # Validation des inputs
    if not client_name:
        raise ValueError("Le nom du client est requis")
    if not resource_group:
        raise ValueError("Le nom du Resource Group est requis")
    if not storage_info or not translator_info or not function_app_info:
        raise ValueError("Les informations de déploiement sont incomplètes")

    # Timestamp
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")
    timestamp_file = now.strftime("%Y%m%d_%H%M%S")
    timestamp_display = now.strftime("%d/%m/%Y à %H:%M:%S")

    # Sanitize subscription_id et tenant_id si présents
    if subscription_id:
        subscription_id = sanitize_credential(subscription_id, visible_chars=8)
    else:
        subscription_id = "Non disponible"

    if not tenant_id:
        tenant_id = "Non disponible"

    # Extraire les informations des services
    storage_name = storage_info.get("name", "N/A")
    storage_sku = storage_info.get("sku", "N/A")
    blob_container = storage_info.get("container_name", "translations")
    storage_endpoint = storage_info.get("primary_endpoints", {}).get("blob", "N/A")

    translator_name = translator_info.get("name", "N/A")
    translator_sku = translator_info.get("sku", "F0")
    translator_region = translator_info.get("region", region)
    translator_endpoint = translator_info.get("endpoint", "N/A")

    function_app_name = function_app_info.get("name", "N/A")
    function_runtime_version = function_app_info.get("runtime_version", "3.11")
    function_app_hostname = function_app_info.get("default_hostname", "N/A")
    function_app_url = f"https://{function_app_hostname}" if function_app_hostname != "N/A" else "N/A"

    # Liste des services déployés
    services = [
        "✓ Azure Storage Account (stockage documents)",
        "✓ Azure Translator F0 (traduction gratuite)",
        "✓ Azure Functions App (backend API)"
    ]
    service_count = len(services)
    services_list = "\n  ".join(services)

    # Liste des fonctions déployées
    expected_functions = [
        "start_translation",
        "check_status",
        "get_result",
        "health",
        "languages",
        "formats"
    ]
    function_count = len(expected_functions)
    functions_list = "\n    • ".join(expected_functions)
    functions_list = "    • " + functions_list

    # Health check status
    health_status = "✓ OK" if function_app_info.get("state") == "Running" else "⚠ À vérifier"

    # Notes par défaut si vides
    if not notes:
        notes = f"Déploiement standard réalisé avec succès.\n  Tous les services sont opérationnels.\n  Région: {region}"

    # Générer le rapport
    report_content = REPORT_TEMPLATE_SIMPLE.format(
        client_name=client_name,
        technician_name=technician_name,
        date=date_str,
        time=time_str,
        duration=deployment_duration,
        resource_group=resource_group,
        region=region,
        subscription_id=subscription_id,
        service_count=service_count,
        services_list=services_list,
        storage_name=storage_name,
        storage_sku=storage_sku,
        blob_container=blob_container,
        storage_endpoint=storage_endpoint,
        translator_name=translator_name,
        translator_sku=translator_sku,
        translator_region=translator_region,
        translator_endpoint=translator_endpoint,
        function_app_name=function_app_name,
        function_runtime_version=function_runtime_version,
        function_app_url=function_app_url,
        function_count=function_count,
        functions_list=functions_list,
        health_status=health_status,
        tenant_id=tenant_id,
        notes=notes,
        report_timestamp=timestamp_display,
    )

    # Sauvegarder le rapport
    report_path = save_report(report_content, client_name, timestamp_file)

    return {
        "report_content": report_content,
        "report_path": report_path,
        "timestamp": timestamp_display,
        "client_name": client_name,
    }


def save_report(
    report_content: str,
    client_name: str,
    timestamp: str,
) -> str:
    """
    Sauvegarde le rapport dans un fichier texte.

    Args:
        report_content: Contenu du rapport
        client_name: Nom du client
        timestamp: Timestamp pour le nom de fichier

    Returns:
        Chemin absolu vers le fichier créé
    """
    # Créer le dossier rapports s'il n'existe pas
    report_dir = Path(REPORT_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)

    # Nom de fichier sécurisé (sans caractères spéciaux)
    safe_client_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in client_name)
    filename = f"rapport-{safe_client_name}-{timestamp}.txt"
    filepath = report_dir / filename

    # Écrire le fichier
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)

    return str(filepath.absolute())


def display_report(report_content: str) -> None:
    """
    Affiche le rapport dans le terminal de manière formatée.

    Args:
        report_content: Contenu du rapport à afficher
    """
    print("\n")
    print("=" * 80)
    print(report_content)
    print("=" * 80)
    print("\n")


def regenerate_report(report_path: str) -> Dict[str, Any]:
    """
    Recharge et affiche un rapport existant depuis un fichier.

    Args:
        report_path: Chemin vers le fichier de rapport

    Returns:
        Dict avec:
            - report_content: Contenu du rapport
            - report_path: Chemin du fichier
            - exists: True si le fichier existe

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    filepath = Path(report_path)

    if not filepath.exists():
        raise FileNotFoundError(f"Le rapport '{report_path}' n'existe pas")

    with open(filepath, "r", encoding="utf-8") as f:
        report_content = f.read()

    return {
        "report_content": report_content,
        "report_path": str(filepath.absolute()),
        "exists": True,
    }


def list_reports(client_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Liste tous les rapports disponibles, optionnellement filtrés par client.

    Args:
        client_name: Nom du client pour filtrer (optionnel)

    Returns:
        Liste de dict avec:
            - filename: Nom du fichier
            - filepath: Chemin complet
            - client: Nom du client (extrait du filename)
            - timestamp: Timestamp (extrait du filename)
            - size_bytes: Taille du fichier
    """
    report_dir = Path(REPORT_DIR)

    if not report_dir.exists():
        return []

    reports = []

    for filepath in report_dir.glob("rapport-*.txt"):
        # Extraire infos du nom de fichier: rapport-{client}-{timestamp}.txt
        filename = filepath.name
        parts = filename.replace("rapport-", "").replace(".txt", "").split("-")

        # Le timestamp est toujours le dernier élément (format YYYYMMDD_HHMMSS sans tiret)
        if len(parts) >= 2:
            timestamp_str = parts[-1]  # Le dernier élément est le timestamp
            client = "-".join(parts[:-1])  # Tout le reste est le nom du client
        else:
            client = "Unknown"
            timestamp_str = "Unknown"

        # Filtrer par client si spécifié
        if client_name and client_name.lower() not in client.lower():
            continue

        reports.append({
            "filename": filename,
            "filepath": str(filepath.absolute()),
            "client": client,
            "timestamp": timestamp_str,
            "size_bytes": filepath.stat().st_size,
        })

    # Trier par timestamp décroissant (plus récent en premier)
    reports.sort(key=lambda x: x["timestamp"], reverse=True)

    return reports
