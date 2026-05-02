"""
MCP Client - Intégration avec le serveur MCP pour les outils médicaux.
Ce module gère la connexion et l'utilisation des outils exposés via MCP.
"""
import httpx
import json
from typing import Any, Dict, Optional
import os

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Appelle un outil exposé par le serveur MCP.
    
    Args:
        tool_name: Nom de l'outil à appeler
        arguments: Arguments à passer à l'outil
    
    Returns:
        Résultat de l'appel à l'outil
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/call",
                json={
                    "tool": tool_name,
                    "arguments": arguments
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            # Fallback si le serveur MCP n'est pas disponible
            return {"error": "MCP server unavailable", "fallback": True}
        except Exception as e:
            return {"error": str(e)}


async def get_medical_reference(condition: str) -> Dict[str, Any]:
    """
    Récupère des informations de référence médicale via MCP.
    """
    return await call_mcp_tool("get_medical_reference", {"condition": condition})


async def check_drug_interactions(medications: list) -> Dict[str, Any]:
    """
    Vérifie les interactions médicamenteuses via MCP.
    """
    return await call_mcp_tool("check_drug_interactions", {"medications": medications})


async def get_icd_codes(symptoms: list) -> Dict[str, Any]:
    """
    Obtient les codes CIM-10 associés aux symptômes via MCP.
    """
    return await call_mcp_tool("get_icd_codes", {"symptoms": symptoms})
