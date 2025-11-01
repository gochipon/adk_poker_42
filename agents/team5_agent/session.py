from google.adk.sessions import InMemorySessionService

# Define constants
APP_NAME = "team5_agent"
SESSION_ID_STATEFUL = "session_state_team5_agent"
USER_ID_STATEFUL = "user_team5_agent"

# Create a NEW session service instance
session_service_stateful = InMemorySessionService()

# Define initial state data - user prefers Celsius initially
initial_state = {
    "hand_range": None,  # Initialize last weather report as None
}

# For notebook usage: explicitly create the session with initial state and verify it
# Usage example in a notebook cell:
#   session_stateful = await create_session()
# This mirrors the official tutorial's style and ensures state initialization.
async def create_session():
    session_stateful = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
        state=initial_state,
    )
    print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

    retrieved_session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
    )
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("Error: Could not retrieve session.")
    return session_stateful


# For plain Python scripts (non-notebook), provide a synchronous initializer
def create_session_sync():
    """Create the demo session synchronously for script execution.

    This wraps the async create_session() with asyncio.run so that users can
    initialize the session without managing an event loop explicitly.
    """
    import asyncio

    return asyncio.run(create_session())
