@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    List users with pagination.

    Example:
        GET /api/v1/users?page=1&page_size=10
    """
    skip = (page - 1) * page_size
    users = await user_service.list_users(skip=skip, limit=page_size)
    total = await user_service.count_users()

    return PaginatedResponse(
        items=[UserResponse.from_domain(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
