"""Wrapper around Firebase Firestore for opportunity data."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterable

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client

from django.conf import settings


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FirestoreOpportunity:
    """Normalized structure for an opportunity document."""

    id: str
    title: str
    summary: str
    bucket: str | None
    tags: list[str]
    funding_amount: str | None
    deadline: str | None
    location: str | None
    eligibility: list[str]
    url: str | None
    raw: dict[str, Any]

    @classmethod
    def from_snapshot(cls, snapshot: Any) -> "FirestoreOpportunity":
        data = snapshot.to_dict() if snapshot else {}
        return cls(
            id=str(getattr(snapshot, "id", "")),
            title=data.get("title") or data.get("name") or "Untitled opportunity",
            summary=data.get("summary") or data.get("description") or "",
            bucket=data.get("bucket"),
            tags=_ensure_list(data.get("tags")),
            funding_amount=data.get("funding_amount") or data.get("amount"),
            deadline=data.get("deadline"),
            location=data.get("location"),
            eligibility=_ensure_list(data.get("eligibility")),
            url=data.get("url") or data.get("website") or data.get("application_url"),
            raw=data,
        )


@dataclass(slots=True)
class FirestoreProfile:
    """Normalized structure for a profile document."""

    id: str
    focus_areas: list[str]
    location: str | None
    organization_type: str | None
    annual_budget_usd: int | None
    target_beneficiaries: list[str]
    keywords: list[str]
    matching_bucket: str | None
    data: dict[str, Any]

    @classmethod
    def from_snapshot(cls, snapshot: Any) -> "FirestoreProfile" | None:
        if not snapshot or not snapshot.exists:
            return None
        data = snapshot.to_dict() or {}
        return cls(
            id=str(getattr(snapshot, "id", "")),
            focus_areas=_ensure_list(data.get("focus_areas")),
            location=data.get("location"),
            organization_type=data.get("organization_type"),
            annual_budget_usd=_safe_int(data.get("annual_budget_usd")),
            target_beneficiaries=_ensure_list(data.get("target_beneficiaries")),
            keywords=_ensure_list(data.get("keywords")),
            matching_bucket=data.get("matching_bucket"),
            data=data,
        )


class FirestoreService:
    """Small facade to access Firestore with resiliency."""

    def __init__(self) -> None:
        self.project_id = settings.FIREBASE_PROJECT_ID
        self.opportunities_collection = settings.FIREBASE_OPPORTUNITIES_COLLECTION
        self.profiles_collection = settings.FIREBASE_PROFILES_COLLECTION

    @cached_property
    def client(self) -> Client:
        if not firebase_admin._apps:
            cred = self._load_credentials()
            if cred:
                firebase_admin.initialize_app(cred, {"projectId": self.project_id})
            else:  # pragma: no cover - fallback scenario
                firebase_admin.initialize_app(options={"projectId": self.project_id})
        return firestore.client()

    def get_profile(self, firebase_uid: str) -> FirestoreProfile | None:
        try:
            snapshot = (
                self.client.collection(self.profiles_collection)
                .document(firebase_uid)
                .get()
            )
            return FirestoreProfile.from_snapshot(snapshot)
        except Exception:  # pragma: no cover - Firestore failure path
            logger.exception("Could not fetch profile %s from Firestore", firebase_uid)
            return None

    def get_opportunities(
        self,
        *,
        bucket: str | None = None,
        limit: int | None = None,
    ) -> list[FirestoreOpportunity]:
        limit = limit or settings.MATCHING_MAX_RESULTS
        try:
            collection = self.client.collection(self.opportunities_collection)
            query = collection
            if bucket:
                query = query.where("bucket", "==", bucket)
            snapshots = query.limit(limit).stream()
            return [FirestoreOpportunity.from_snapshot(doc) for doc in snapshots]
        except Exception:  # pragma: no cover - Firestore failure path
            logger.exception("Failed to stream opportunities from Firestore")
            return []

    def record_user_action(
        self,
        firebase_uid: str,
        opportunity_id: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        payload = payload or {}
        try:
            collection = (
                self.client.collection(self.profiles_collection)
                .document(firebase_uid)
                .collection(action.capitalize())
            )
            collection.document(opportunity_id).set(payload, merge=True)
        except Exception:  # pragma: no cover - Firestore failure path
            logger.exception("Failed to record %s action for %s", action, firebase_uid)

    def get_user_action_ids(self, firebase_uid: str, action: str) -> set[str]:
        try:
            collection = (
                self.client.collection(self.profiles_collection)
                .document(firebase_uid)
                .collection(action.capitalize())
            )
            return {doc.id for doc in collection.stream()}
        except Exception:  # pragma: no cover - Firestore failure path
            logger.exception("Failed to read %s collection for %s", action, firebase_uid)
            return set()

    def _load_credentials(self) -> credentials.Base:  # pragma: no cover - environment dependent
        json_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        inline_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
        if json_path and os.path.exists(json_path):
            return credentials.Certificate(json_path)
        if inline_json:
            data = json.loads(inline_json)
            return credentials.Certificate(data)
        return credentials.ApplicationDefault()


def _ensure_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, (set, tuple)):
        return list(value)
    if isinstance(value, str) and value:
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
