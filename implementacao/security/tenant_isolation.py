"""
Tenant Isolation Module for GraphRAG in Financial Institutions.

Implements multi-tenant data isolation at the Neo4j graph database level,
ensuring that queries from one tenant cannot access data belonging to
another tenant. This is critical for regulatory compliance (LGPD Art. 46,
GDPR Art. 32) in financial environments where departments (compliance,
audit, risk) must maintain strict data boundaries.

Defense mechanisms implemented:
  - D2: Tenant isolation via tenant_id property on all Neo4j nodes
  - D3: Post-retrieval result filtering by tenant permissions

References:
  - RAG Security Threat Model (arXiv:2509.20324)
  - Privacy Risks in GraphRAG (arXiv:2508.17222)
  - SAG - Provably Secure RAG (arXiv:2508.01084)
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TenantRole(str, Enum):
    """Role-based access control levels for tenant isolation."""
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDITOR = "auditor"
    ANALYST = "analyst"
    VIEWER = "viewer"


@dataclass
class SecurityContext:
    """Security context for authenticated requests.

    Carries tenant identity and permissions through the retrieval pipeline,
    enabling both query-time filtering (D2) and post-retrieval validation (D3).
    """
    user_id: str
    tenant_id: str
    role: TenantRole
    permissions: list[str] = field(default_factory=list)
    allowed_entity_types: list[str] = field(default_factory=list)

    def can_access_tenant(self, target_tenant_id: str) -> bool:
        """Check if this context permits access to target tenant data."""
        if self.role == TenantRole.ADMIN:
            return True
        return self.tenant_id == target_tenant_id

    def can_access_entity_type(self, entity_type: str) -> bool:
        """Check if this context permits access to a specific entity type."""
        if self.role == TenantRole.ADMIN:
            return True
        if not self.allowed_entity_types:
            return True
        return entity_type in self.allowed_entity_types


class TenantIsolationManager:
    """Manages tenant isolation for Neo4j graph queries.

    Ensures all Cypher queries are scoped to the authenticated tenant,
    preventing cross-tenant data leakage (Threat T1). Implements both
    query-level injection of tenant_id constraints and post-retrieval
    validation of result sets.

    Architecture:
        1. Query Injection: All Cypher queries are rewritten to include
           tenant_id filters on every node pattern.
        2. Post-Retrieval Filtering: Results are validated against the
           security context before being returned to the caller.
        3. Audit Logging: All access attempts (successful and denied)
           are logged for compliance (D5).
    """

    # Cypher query to initialize tenant_id on existing nodes
    MIGRATION_QUERY = """
    MATCH (n) WHERE n.tenant_id IS NULL
    SET n.tenant_id = $default_tenant_id
    RETURN count(n) AS migrated_count
    """

    # Cypher query to create tenant isolation constraint
    CONSTRAINT_QUERY = """
    CREATE INDEX tenant_isolation_idx IF NOT EXISTS
    FOR (n:Entity)
    ON (n.tenant_id)
    """

    def __init__(self, neo4j_driver: Any, default_tenant_id: str = "default"):
        """Initialize tenant isolation manager.

        Args:
            neo4j_driver: Neo4j driver instance for database operations.
            default_tenant_id: Tenant ID assigned to existing nodes
                without tenant_id property during migration.
        """
        self.driver = neo4j_driver
        self.default_tenant_id = default_tenant_id
        self._initialized = False

    async def initialize(self) -> dict:
        """Run migration to add tenant_id to all existing nodes.

        Returns:
            Dictionary with migration statistics.
        """
        stats = {"migrated_nodes": 0, "index_created": False}

        async with self.driver.session() as session:
            # Migrate existing nodes
            result = await session.run(
                self.MIGRATION_QUERY,
                default_tenant_id=self.default_tenant_id,
            )
            record = await result.single()
            stats["migrated_nodes"] = record["migrated_count"]

            # Create index for efficient tenant filtering
            await session.run(self.CONSTRAINT_QUERY)
            stats["index_created"] = True

        self._initialized = True
        logger.info(
            "Tenant isolation initialized: %d nodes migrated",
            stats["migrated_nodes"],
        )
        return stats

    def inject_tenant_filter(
        self,
        cypher_query: str,
        security_context: SecurityContext,
    ) -> tuple[str, dict]:
        """Inject tenant_id filter into a Cypher query.

        Rewrites MATCH patterns to include tenant_id constraints,
        ensuring queries only traverse nodes belonging to the
        authenticated tenant.

        Args:
            cypher_query: Original Cypher query string.
            security_context: Authenticated user's security context.

        Returns:
            Tuple of (modified_query, parameters) with tenant filter injected.

        Example:
            Input:  MATCH (n)-[r]->(m) RETURN n, r, m
            Output: MATCH (n {tenant_id: $tenant_id})-[r]->(m {tenant_id: $tenant_id})
                    RETURN n, r, m
        """
        tenant_id = security_context.tenant_id
        params = {"tenant_id": tenant_id}

        filtered_query = self._rewrite_match_patterns(cypher_query)

        logger.debug(
            "Tenant filter injected for tenant=%s, user=%s",
            tenant_id,
            security_context.user_id,
        )
        return filtered_query, params

    def _rewrite_match_patterns(self, query: str) -> str:
        """Rewrite MATCH clause node patterns to include tenant_id filter.

        Handles patterns like:
            (n)           -> (n {tenant_id: $tenant_id})
            (n:Label)     -> (n:Label {tenant_id: $tenant_id})
            (n:Label {x}) -> (n:Label {x, tenant_id: $tenant_id})
        """
        # Pattern: node reference with optional label and optional properties
        # (varname) or (varname:Label) or (varname:Label {props})
        node_pattern = re.compile(
            r'\((\w+)'           # (variable_name
            r'(:\w+)?'           # optional :Label
            r'(\s*\{[^}]*\})?'   # optional {properties}
            r'\)'                # closing )
        )

        def _add_tenant_filter(match: re.Match) -> str:
            var_name = match.group(1)
            label = match.group(2) or ""
            props = match.group(3) or ""

            if props:
                # Add tenant_id to existing properties
                props = props.rstrip("}").rstrip() + ", tenant_id: $tenant_id}"
            else:
                props = " {tenant_id: $tenant_id}"

            return f"({var_name}{label}{props})"

        # Only rewrite patterns after MATCH or OPTIONAL MATCH keywords
        lines = query.split("\n")
        rewritten_lines = []

        for line in lines:
            stripped = line.strip().upper()
            if stripped.startswith("MATCH") or stripped.startswith("OPTIONAL MATCH"):
                rewritten_lines.append(node_pattern.sub(_add_tenant_filter, line))
            else:
                rewritten_lines.append(line)

        return "\n".join(rewritten_lines)

    def filter_results(
        self,
        results: list[dict],
        security_context: SecurityContext,
    ) -> list[dict]:
        """Post-retrieval filtering of query results by tenant permissions.

        Validates that every result belongs to the authenticated tenant
        and that the user's role permits access to the entity types
        returned. This is a defense-in-depth measure (D3) that catches
        any bypass of query-level filtering.

        Args:
            results: List of result dictionaries from Neo4j query.
            security_context: Authenticated user's security context.

        Returns:
            Filtered list containing only permitted results.
        """
        filtered = []
        denied_count = 0

        for result in results:
            tenant_id = result.get("tenant_id", result.get("n.tenant_id"))
            entity_type = result.get("type", result.get("n.type", ""))

            # Check tenant access
            if tenant_id and not security_context.can_access_tenant(tenant_id):
                denied_count += 1
                logger.warning(
                    "Cross-tenant access denied: user=%s (tenant=%s) "
                    "attempted to access tenant=%s",
                    security_context.user_id,
                    security_context.tenant_id,
                    tenant_id,
                )
                continue

            # Check entity type access
            if entity_type and not security_context.can_access_entity_type(
                entity_type
            ):
                denied_count += 1
                logger.info(
                    "Entity type access denied: user=%s, type=%s",
                    security_context.user_id,
                    entity_type,
                )
                continue

            filtered.append(result)

        if denied_count > 0:
            logger.info(
                "Post-retrieval filter: %d/%d results denied for user=%s",
                denied_count,
                len(results),
                security_context.user_id,
            )

        return filtered

    def validate_response(
        self,
        response_text: str,
        security_context: SecurityContext,
        known_tenant_entities: Optional[dict[str, list[str]]] = None,
    ) -> dict:
        """Validate that a generated response does not leak cross-tenant data.

        Scans the response text for references to entities belonging to
        other tenants. This is the final defense layer before returning
        a response to the user.

        Args:
            response_text: Generated response text to validate.
            security_context: Authenticated user's security context.
            known_tenant_entities: Mapping of tenant_id -> list of entity
                names. Used to detect cross-tenant entity mentions.

        Returns:
            Validation result with is_safe flag and details.
        """
        if not known_tenant_entities:
            return {"is_safe": True, "leaked_entities": [], "details": "No entity registry provided"}

        leaked = []
        for tenant_id, entities in known_tenant_entities.items():
            if security_context.can_access_tenant(tenant_id):
                continue
            for entity_name in entities:
                if entity_name.lower() in response_text.lower():
                    leaked.append({
                        "entity": entity_name,
                        "source_tenant": tenant_id,
                    })

        is_safe = len(leaked) == 0

        if not is_safe:
            logger.warning(
                "Response validation FAILED: %d leaked entities detected "
                "for user=%s (tenant=%s)",
                len(leaked),
                security_context.user_id,
                security_context.tenant_id,
            )

        return {
            "is_safe": is_safe,
            "leaked_entities": leaked,
            "details": (
                "Response is clean"
                if is_safe
                else f"{len(leaked)} cross-tenant entity references detected"
            ),
        }

    def create_tenant_node_query(
        self,
        entity_type: str,
        properties: dict,
        tenant_id: str,
    ) -> tuple[str, dict]:
        """Generate a MERGE query that includes tenant_id for new nodes.

        Args:
            entity_type: Neo4j node label (e.g., 'Regulation', 'Company').
            properties: Node properties dictionary.
            tenant_id: Tenant identifier to assign to the node.

        Returns:
            Tuple of (cypher_query, parameters).
        """
        props = {**properties, "tenant_id": tenant_id}
        prop_keys = ", ".join(f"{k}: ${k}" for k in props)

        query = f"MERGE (n:{entity_type} {{name: $name, tenant_id: $tenant_id}}) SET n += {{{prop_keys}}} RETURN n"

        return query, props

    def get_tenant_subgraph_query(self, tenant_id: str) -> tuple[str, dict]:
        """Generate a query to retrieve the complete subgraph for a tenant.

        Used for tenant-scoped analytics and graph visualization.
        """
        query = """
        MATCH (n {tenant_id: $tenant_id})-[r]->(m {tenant_id: $tenant_id})
        RETURN n, r, m
        """
        return query, {"tenant_id": tenant_id}

    def get_tenant_stats_query(self, tenant_id: str) -> tuple[str, dict]:
        """Generate a query for tenant-specific graph statistics."""
        query = """
        MATCH (n {tenant_id: $tenant_id})
        WITH labels(n) AS node_labels, count(n) AS cnt
        UNWIND node_labels AS label
        RETURN label, sum(cnt) AS node_count
        ORDER BY node_count DESC
        """
        return query, {"tenant_id": tenant_id}


class InputSanitizer:
    """Sanitizes user input to prevent query manipulation attacks (T5).

    Validates and cleans query inputs before they reach the Cypher query
    builder, preventing injection of malicious patterns.
    """

    # Patterns that could indicate Cypher injection attempts
    DANGEROUS_PATTERNS = [
        r"(?i)\bDELETE\b",
        r"(?i)\bDETACH\b",
        r"(?i)\bDROP\b",
        r"(?i)\bCREATE\s+INDEX\b",
        r"(?i)\bCALL\s+\{",
        r"(?i)\bCALL\s+db\.",
        r"(?i)\bCALL\s+apoc\.",
        r"(?i)\bLOAD\s+CSV\b",
        r"(?i)\bUSING\s+PERIODIC\b",
        r"(?i)\bFOREACH\b",
        r"//",               # Cypher comments
        r"/\*",              # Block comments
    ]

    # Maximum query length to prevent resource exhaustion
    MAX_QUERY_LENGTH = 2000

    @classmethod
    def sanitize_query(cls, user_query: str) -> tuple[str, list[str]]:
        """Sanitize user query input.

        Args:
            user_query: Raw user query string.

        Returns:
            Tuple of (sanitized_query, warnings).
        """
        warnings = []

        if not user_query or not user_query.strip():
            return "", ["Empty query"]

        # Length check
        if len(user_query) > cls.MAX_QUERY_LENGTH:
            user_query = user_query[: cls.MAX_QUERY_LENGTH]
            warnings.append(
                f"Query truncated to {cls.MAX_QUERY_LENGTH} characters"
            )

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, user_query):
                warnings.append(f"Suspicious pattern detected: {pattern}")
                logger.warning(
                    "Input sanitization: dangerous pattern detected in query: %s",
                    pattern,
                )

        # Strip control characters
        sanitized = "".join(
            c for c in user_query if c.isprintable() or c in ("\n", "\t")
        )

        return sanitized, warnings

    @classmethod
    def sanitize_entity_name(cls, entity_name: str) -> str:
        """Sanitize entity name for safe use in Cypher queries.

        Args:
            entity_name: Raw entity name string.

        Returns:
            Sanitized entity name safe for parameterized queries.
        """
        # Remove any Cypher-special characters
        sanitized = re.sub(r"[{}()\[\];`]", "", entity_name)
        # Collapse whitespace
        sanitized = re.sub(r"\s+", " ", sanitized).strip()
        return sanitized[:200]  # Max entity name length


class AuditLogger:
    """Structured audit logging for security events (D5).

    Logs all security-relevant events to PostgreSQL for compliance
    with LGPD Art. 18 (right to access logs), Basel III Pillar 3
    (disclosure requirements), and SOX Section 404 (internal controls).
    """

    @staticmethod
    def log_access_attempt(
        security_context: SecurityContext,
        query: str,
        result_count: int,
        filtered_count: int,
        success: bool,
    ) -> dict:
        """Create structured audit log entry for an access attempt.

        Returns:
            Dictionary suitable for insertion into usage_logs table.
        """
        entry = {
            "user_id": security_context.user_id,
            "tenant_id": security_context.tenant_id,
            "role": security_context.role.value,
            "query_hash": hash(query) & 0xFFFFFFFF,
            "result_count": result_count,
            "filtered_count": filtered_count,
            "access_granted": success,
            "event_type": "graph_access",
        }

        log_level = logging.INFO if success else logging.WARNING
        logger.log(
            log_level,
            "Audit: user=%s tenant=%s role=%s results=%d filtered=%d granted=%s",
            entry["user_id"],
            entry["tenant_id"],
            entry["role"],
            result_count,
            filtered_count,
            success,
        )
        return entry

    @staticmethod
    def log_security_event(
        event_type: str,
        security_context: SecurityContext,
        details: str,
    ) -> dict:
        """Log a security event (failed validation, suspicious activity, etc.)."""
        entry = {
            "user_id": security_context.user_id,
            "tenant_id": security_context.tenant_id,
            "event_type": event_type,
            "details": details,
            "severity": "high" if "denied" in details.lower() else "medium",
        }

        logger.warning(
            "Security event [%s]: user=%s tenant=%s - %s",
            event_type,
            entry["user_id"],
            entry["tenant_id"],
            details,
        )
        return entry
