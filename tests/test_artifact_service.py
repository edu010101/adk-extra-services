# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the artifact service."""

import enum

import pytest
from google.genai import types

from adk_extra_services.artifacts import S3ArtifactService, LocalFolderArtifactService

Enum = enum.Enum


class ArtifactServiceType(Enum):
    S3 = "S3"
    LOCAL = "LOCAL"


def mock_s3_artifact_service():
    """Mocks an S3 client for testing S3ArtifactService."""

    class MockBody:

        def __init__(self, content):
            self._content = content

        def read(self):
            return self._content

    class MockS3Client:

        def __init__(self):
            self.store = {}

        class exceptions:

            class NoSuchKey(Exception):
                pass

        def put_object(self, Bucket, Key, Body, ContentType):
            self.store[Key] = (Body, ContentType)

        def get_object(self, Bucket, Key):
            if Key not in self.store:
                raise MockS3Client.exceptions.NoSuchKey()
            body, mime = self.store[Key]
            return {"Body": MockBody(body), "ContentType": mime}

        def delete_object(self, Bucket, Key):
            self.store.pop(Key, None)

        def get_paginator(self, operation_name):
            class Paginator:

                def paginate(self, Bucket, Prefix):
                    keys = [k for k in client.store.keys() if k.startswith(Prefix)]
                    yield {"Contents": [{"Key": k} for k in keys]}

            client = self
            return Paginator()

    svc = S3ArtifactService(bucket_name="test_bucket")
    svc.s3_client = MockS3Client()
    return svc


def get_artifact_service(service_type: ArtifactServiceType, tmp_path):
    """Returns an artifact service instance based on type."""
    if service_type == ArtifactServiceType.S3:
        return mock_s3_artifact_service()
    if service_type == ArtifactServiceType.LOCAL:
        return LocalFolderArtifactService(base_path=tmp_path)
    raise ValueError(f"Unsupported service type: {service_type}")


@pytest.mark.asyncio
@pytest.mark.parametrize("service_type", [ArtifactServiceType.S3, ArtifactServiceType.LOCAL])
async def test_load_empty(service_type, tmp_path):
    """Tests loading an artifact when none exists."""
    artifact_service = get_artifact_service(service_type, tmp_path)
    assert not await artifact_service.load_artifact(
        app_name="test_app",
        user_id="test_user",
        session_id="session_id",
        filename="filename",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("service_type", [ArtifactServiceType.S3, ArtifactServiceType.LOCAL])
async def test_save_load_delete(service_type, tmp_path):
    """Tests saving, loading, and deleting an artifact."""
    artifact_service = get_artifact_service(service_type, tmp_path)
    artifact = types.Part.from_bytes(data=b"test_data", mime_type="text/plain")
    app_name = "app0"
    user_id = "user0"
    session_id = "123"
    filename = "file456"

    await artifact_service.save_artifact(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
        artifact=artifact,
    )
    assert (
        await artifact_service.load_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=filename,
        )
        == artifact
    )

    await artifact_service.delete_artifact(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
    )
    assert not await artifact_service.load_artifact(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("service_type", [ArtifactServiceType.S3, ArtifactServiceType.LOCAL])
async def test_list_keys(service_type, tmp_path):
    """Tests listing keys in the artifact service."""
    artifact_service = get_artifact_service(service_type, tmp_path)
    artifact = types.Part.from_bytes(data=b"test_data", mime_type="text/plain")
    app_name = "app0"
    user_id = "user0"
    session_id = "123"
    filename = "filename"
    filenames = [filename + str(i) for i in range(5)]

    for f in filenames:
        await artifact_service.save_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=f,
            artifact=artifact,
        )

    assert (
        await artifact_service.list_artifact_keys(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        == filenames
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("service_type", [ArtifactServiceType.S3, ArtifactServiceType.LOCAL])
async def test_list_versions(service_type, tmp_path):
    """Tests listing versions of an artifact."""
    artifact_service = get_artifact_service(service_type, tmp_path)

    app_name = "app0"
    user_id = "user0"
    session_id = "123"
    filename = "filename"
    versions = [
        types.Part.from_bytes(
            data=i.to_bytes(2, byteorder="big"), mime_type="text/plain"
        )
        for i in range(3)
    ]

    for i in range(3):
        await artifact_service.save_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=filename,
            artifact=versions[i],
        )

    response_versions = await artifact_service.list_versions(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
    )

    assert response_versions == list(range(3))
