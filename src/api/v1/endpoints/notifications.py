"""
Using background tasks for async operations.
"""

from fastapi import BackgroundTasks


async def send_email_notification(user_email: str, subject: str, body: str):
    """
    Send email in background.
    This doesn't block the API response.
    """
    # Email sending logic here
    await email_service.send(user_email, subject, body)


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register user and send welcome email in background.
    """
    user = await auth_service.register(
        email=data.email, password=data.password, full_name=data.full_name
    )

    # Add background task (doesn't block response)
    background_tasks.add_task(
        send_email_notification,
        user_email=user.email,
        subject="Welcome!",
        body=f"Welcome {user.full_name}!",
    )

    return UserResponse.from_domain(user)
