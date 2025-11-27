"""Herramientas para protocolos de seguridad y prevencion de crisis."""
import re
from typing import Any, Dict, List, Pattern

from models import SafetyProtocolResult


def _default_levels() -> Dict[str, Dict[str, Any]]:
    """Configuracion base de patrones, mensajes y escalamiento."""
    return {
        "high": {
            "label": "🔴 Alto",
            "description": "Mencion directa de suicidio o intencion explicita de autolesion.",
            "examples": ["Voy a matarme", "Ya tengo el plan hecho"],
            "patterns": [
                r"\bme quiero morir\b",
                r"\bno quiero vivir\b",
                r"\bquitarme la vida\b",
                r"\bterminar con mi vida\b",
                r"\bno vale la pena vivir\b",
                r"\bvoy a suicidarme\b",
                r"\btengo un plan para suicidarme\b",
                r"\bsuicidarme\b",
                r"\bsuicidio\b",
                r"\bplaneo suicidarme\b",
                r"\bend my life\b",
                r"\bkill myself\b",
                r"\bi want to die\b",
            ],
            "response": (
                "Gracias por compartir lo que sientes. Vamos a priorizar tu seguridad ahora mismo. Comunicate"
                " de inmediato con los servicios de emergencia 123 en Colombia o con la Linea 106 (Bogota)."
                " Si estas en otra region, llama o escribe a la Linea Calma 3009125231 o consulta"
                " https://www.iasp.info/resources/Crisis_Centres/ para ubicar apoyo presencial. Indica donde"
                " te encuentras y pide a alguien de confianza que permanezca contigo mientras llega ayuda."
            ),
            "resources": [
                "Linea 123 - emergencias en Colombia",
                "Linea 106 - atencion en salud mental (Bogota)",
                "Linea Calma (WhatsApp 3009125231)",
                "https://www.iasp.info/resources/Crisis_Centres/ - centros de crisis internacionales",
            ],
            "recommendations": [
                "Contactar inmediatamente a los servicios de emergencia disponibles en tu zona.",
                "Compartir tu ubicacion actual para coordinar apoyo en sitio.",
                "Buscar compania de una persona de confianza mientras llega ayuda profesional.",
            ],
            "alert_required": True,
            "priority": 0,
        },
        "moderate": {
            "label": "🟡 Moderado",
            "description": "Expresiones de desesperanza o deseos de desaparecer sin un plan explicito.",
            "examples": ["Ya no quiero seguir asi", "Preferiria no despertar"],
            "patterns": [
                r"\bya no quiero seguir asi\b",
                r"\bno encuentro salida\b",
                r"\bno veo sentido a la vida\b",
                r"\bpreferiria desaparecer\b",
                r"\bquisiera dormirme y no despertar\b",
                r"\bestoy cansado de vivir\b",
                r"\bno puedo mas\b",
                r"\bthoughts of death\b",
                r"\bending it all\b",
            ],
            "response": (
                "Gracias por abrirte sobre lo que estas viviendo. Estos mensajes muestran un dolor profundo y"
                " es importante que recibas acompanamiento profesional cuanto antes. Agenda una consulta con"
                " un psicologo o psiquiatra y comparte exactamente lo que mencionaste aqui. Puedes comunicarte"
                " con la Linea 106 o la Linea Calma 3009125231 para orientacion inmediata, y habla hoy con alguien"
                " de tu confianza para no atravesar esto en soledad."
            ),
            "resources": [
                "Linea 106 - atencion en salud mental (Bogota)",
                "Linea Calma (WhatsApp 3009125231)",
                "https://www.iasp.info/resources/Crisis_Centres/ - centros de crisis internacionales",
            ],
            "recommendations": [
                "Contactar a un profesional de salud mental y programar una cita prioritaria.",
                "Utilizar lineas de apoyo emocional como la 106 o Linea Calma para acompañamiento inmediato.",
                "Informar a una persona de confianza sobre los pensamientos que estas teniendo hoy.",
            ],
            "alert_required": False,
            "priority": 1,
        },
        "low": {
            "label": "🟢 Bajo",
            "description": "Expresiones de tristeza, agotamiento o soledad sin ideacion suicida.",
            "examples": ["Estoy muy triste ultimamente", "Me siento muy solo"],
            "patterns": [
                r"\bestoy deprimido\b",
                r"\bsiento mucha tristeza\b",
                r"\bestoy muy solo\b",
                r"\bestoy muy sola\b",
                r"\bno tengo ganas de nada\b",
                r"\bestoy perdiendo la esperanza\b",
                r"\bestoy muy cansado emocionalmente\b",
            ],
            "response": (
                "Lamento que estes pasando por este momento dificil. Hablar de tu tristeza es un paso valioso."
                " Te sugiero agendar una orientacion con el equipo de bienestar o un profesional de confianza,"
                " y trabajar en estrategias de autocuidado. Puedo compartirte ejercicios de respiracion,"
                " tecnicas de afrontamiento y materiales para que no te sientas solo/a en este proceso."
            ),
            "resources": [
                "Programa de bienestar u orientacion psicologica de tu institucion",
                "Articulo OMS: autocuidado y salud mental (https://www.who.int/es/health-topics/mental-health)",
                "Guia de ejercicios de respiracion y relajacion (https://www.apa.org/topics/stress/tips)",
            ],
            "recommendations": [
                "Hablar con una persona de confianza sobre lo que estas sintiendo.",
                "Agendar una sesion con orientacion psicologica o bienestar universitario.",
                "Practicar ejercicios de autocuidado y registrar cambios en estado de animo.",
            ],
            "alert_required": False,
            "priority": 2,
        },
    }


DEFAULT_RESOURCES = [
    "Linea 123 - emergencias en Colombia",
    "Linea 106 - atencion en salud mental (Bogota)",
    "Linea Calma (WhatsApp 3009125231)",
    "https://www.iasp.info/resources/Crisis_Centres/ - busqueda de centros de crisis internacionales",
]


class SafetyProtocol:
    """Gestiona la deteccion y respuesta de protocolos de crisis."""

    def __init__(self, levels: Dict[str, Dict[str, List[str]]] = None, resources: List[str] = None):
        self.levels = levels or _default_levels()
        self.resources = resources or DEFAULT_RESOURCES
        self._compiled: Dict[str, List[Pattern[str]]] = {
            level: [re.compile(pattern, re.IGNORECASE) for pattern in data.get("patterns", [])]
            for level, data in self.levels.items()
        }

        self._severity_order = self._compute_severity_order()

    def evaluate(self, message: str) -> SafetyProtocolResult:
        """Analiza el mensaje y retorna la accion de seguridad necesaria."""
        if not message:
            return SafetyProtocolResult(triggered=False)

        matched_terms: List[str] = []
        detected_level = ""

        for level in self._severity_order:
            patterns = self._compiled.get(level, [])
            level_matches: List[str] = []
            for pattern in patterns:
                match = pattern.search(message)
                if match:
                    level_matches.append(match.group(0))
            if level_matches:
                detected_level = level
                matched_terms = level_matches
                break

        if not detected_level:
            return SafetyProtocolResult(triggered=False)

        level_data = self.levels.get(detected_level, {})
        response = self._build_response(detected_level, level_data)
        return SafetyProtocolResult(
            triggered=True,
            severity=detected_level,
            message=response,
            matched_terms=matched_terms,
            label=level_data.get("label", ""),
            recommendations=level_data.get("recommendations", []) or [],
            alert_required=bool(level_data.get("alert_required", False)),
        )

    def _build_response(self, level: str, level_data: Dict[str, Any]) -> str:
        """Compone el mensaje de contencion y recursos."""
        base = level_data.get("response")
        if not base:
            base = (
                "Gracias por contarme como te sientes. Es fundamental que busques apoyo profesional y te"
                " acerques a los servicios de emergencia o a una persona de confianza."
            )

        level_resources = list(level_data.get("resources", []) or [])
        if self.resources:
            for resource in self.resources:
                if resource not in level_resources:
                    level_resources.append(resource)

        if level_resources:
            resources_text = " Recursos de apoyo: " + "; ".join(level_resources) + "."
            base = base.strip() + resources_text

        return base.strip()

    def update_levels(self, new_levels: Dict[str, Dict[str, Any]]) -> None:
        """Permite reemplazar la configuracion para escalamientos futuros."""
        if not new_levels:
            return
        self.levels = new_levels
        self._compiled = {
            level: [re.compile(pattern, re.IGNORECASE) for pattern in data.get("patterns", [])]
            for level, data in self.levels.items()
        }
        self._severity_order = self._compute_severity_order()

    def update_resources(self, resources: List[str]) -> None:
        """Actualiza el listado base de recursos profesionales."""
        if resources is None:
            return
        self.resources = resources

    def _compute_severity_order(self) -> List[str]:
        """Ordena los niveles por prioridad declarada."""
        return sorted(
            self.levels.keys(),
            key=lambda level: self.levels[level].get("priority", 999),
        )
