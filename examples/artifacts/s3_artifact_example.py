import asyncio
import os
import warnings
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from adk_extra_services.artifacts import S3ArtifactService
from csv_agent import csv_agent


APP_NAME = "s3_artifact_example"
USER_ID = "example_user"
SESSION_ID = "session1"


def load_env():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(dotenv_path):
        warnings.warn(
            f'Missing .env file at {dotenv_path}. See .env.example for an example.'
        )
    else:
        load_dotenv(dotenv_path, override=True, verbose=True)

        
async def main():
    session_service = InMemorySessionService()
    artifact_service = S3ArtifactService(
        bucket_name="test-bucket"
    )
    # Or you can pass the credentials explicitly:
    # artifact_service = S3ArtifactService(
    #     bucket_name="test-bucket",
    #     endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    #     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    #     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    #     region_name=os.getenv("AWS_REGION"),
    # )

    runner = Runner(
        agent=csv_agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service
    )

    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    user_prompt = "Write a CSV row 'name,age,city' and save it as 'sample.csv'"
    print(f">>> Sending to agent: {user_prompt}")
    user_content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text
    print("Agent response:", final_response)

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("Session state:", session.state)


if __name__ == "__main__":
    load_env()
    asyncio.run(main())