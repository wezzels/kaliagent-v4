"""
Permission System for Collaboration
====================================

Role-based access control for workspaces and resources.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class Permission(str, Enum):
    """Available permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


class Role(str, Enum):
    """User roles."""
    VIEWER = "viewer"  # Read-only
    EDITOR = "editor"  # Read + write
    CONTRIBUTOR = "contributor"  # Read + write + delete
    OWNER = "owner"  # All permissions


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.VIEWER: {Permission.READ},
    Role.EDITOR: {Permission.READ, Permission.WRITE},
    Role.CONTRIBUTOR: {Permission.READ, Permission.WRITE, Permission.DELETE},
    Role.OWNER: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE, Permission.ADMIN},
}


@dataclass
class AccessGrant:
    """Access grant for a participant."""

    grant_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    participant_id: str = ""
    resource_id: str = ""  # Empty for workspace-level
    role: Role = Role.VIEWER
    granted_by: str = ""
    granted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if this grant includes a permission."""
        role_perms = ROLE_PERMISSIONS.get(self.role, set())
        return permission in role_perms

    def is_expired(self) -> bool:
        """Check if grant has expired."""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "grant_id": self.grant_id,
            "participant_id": self.participant_id,
            "resource_id": self.resource_id,
            "role": self.role.value,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
        }


class PermissionManager:
    """Manages permissions for workspaces and resources."""

    def __init__(self):
        self._grants: Dict[str, AccessGrant] = {}  # grant_id -> grant
        self._participant_roles: Dict[str, Dict[str, Role]] = {}  # participant_id -> {resource_id: role}
        self._default_role: Role = Role.VIEWER

    def set_default_role(self, role: Role):
        """Set default role for new participants."""
        self._default_role = role

    def grant_access(self, participant_id: str, role: Role,
                    resource_id: str = "", granted_by: str = "",
                    duration_minutes: Optional[int] = None) -> AccessGrant:
        """Grant access to a participant."""
        expires_at = None
        if duration_minutes:
            from datetime import timedelta
            expires_at = (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat()

        grant = AccessGrant(
            participant_id=participant_id,
            resource_id=resource_id,
            role=role,
            granted_by=granted_by,
            expires_at=expires_at,
        )

        self._grants[grant.grant_id] = grant

        # Update participant roles
        if participant_id not in self._participant_roles:
            self._participant_roles[participant_id] = {}
        self._participant_roles[participant_id][resource_id] = role

        return grant

    def revoke_access(self, grant_id: str) -> bool:
        """Revoke an access grant."""
        if grant_id not in self._grants:
            return False

        grant = self._grants[grant_id]

        # Remove from participant roles
        if grant.participant_id in self._participant_roles:
            if grant.resource_id in self._participant_roles[grant.participant_id]:
                del self._participant_roles[grant.participant_id][grant.resource_id]

        del self._grants[grant_id]
        return True

    def update_role(self, participant_id: str, role: Role,
                   resource_id: str = "") -> bool:
        """Update a participant's role."""
        if participant_id not in self._participant_roles:
            return False

        if resource_id not in self._participant_roles[participant_id]:
            return False

        self._participant_roles[participant_id][resource_id] = role

        # Update grant
        for grant in self._grants.values():
            if grant.participant_id == participant_id and grant.resource_id == resource_id:
                grant.role = role
                break

        return True

    def get_role(self, participant_id: str,
                resource_id: str = "") -> Role:
        """Get participant's role for a resource."""
        if participant_id not in self._participant_roles:
            return self._default_role

        # Check resource-specific role
        if resource_id and resource_id in self._participant_roles[participant_id]:
            return self._participant_roles[participant_id][resource_id]

        # Check workspace-level role
        if "" in self._participant_roles[participant_id]:
            return self._participant_roles[participant_id][""]

        return self._default_role

    def has_permission(self, participant_id: str, permission: Permission,
                      resource_id: str = "") -> bool:
        """Check if participant has a permission."""
        role = self.get_role(participant_id, resource_id)
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return permission in role_perms

    def get_participants(self, resource_id: str = "") -> Dict[str, Role]:
        """Get all participants with their roles."""
        result = {}

        for participant_id, roles in self._participant_roles.items():
            if resource_id:
                if resource_id in roles:
                    result[participant_id] = roles[resource_id]
            else:
                # Get highest role
                if "" in roles:
                    result[participant_id] = roles[""]
                elif roles:
                    result[participant_id] = max(roles.values(), key=lambda r: len(ROLE_PERMISSIONS.get(r, set())))

        return result

    def get_grants(self, participant_id: Optional[str] = None,
                  resource_id: Optional[str] = None) -> List[AccessGrant]:
        """Get grants, optionally filtered."""
        grants = list(self._grants.values())

        if participant_id:
            grants = [g for g in grants if g.participant_id == participant_id]

        if resource_id is not None:
            grants = [g for g in grants if g.resource_id == resource_id]

        # Filter expired
        grants = [g for g in grants if not g.is_expired()]

        return grants

    def cleanup_expired(self):
        """Remove expired grants."""
        expired = [g.grant_id for g in self._grants.values() if g.is_expired()]

        for grant_id in expired:
            self.revoke_access(grant_id)

        return len(expired)

    def get_state(self) -> Dict[str, Any]:
        """Get permission manager state."""
        return {
            "total_grants": len(self._grants),
            "active_participants": len(self._participant_roles),
            "default_role": self._default_role.value,
        }
