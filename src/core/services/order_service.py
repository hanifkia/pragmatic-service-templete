"""
Service that coordinates multiple repositories.

This demonstrates how services orchestrate between different entities.
"""


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        user_repo: UserRepository,
        cache: CacheRepository,
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.user_repo = user_repo
        self.cache = cache

    async def create_order(self, user_id: str, product_ids: List[str]) -> Order:
        """
        Create an order with business logic across multiple entities.

        Business Rules:
            1. User must exist and be active
            2. All products must exist and be in stock
            3. Calculate total price
            4. Invalidate user's cart cache
        """
        # Validate user
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid user")

        # Validate and get products
        products = []
        total_price = 0.0
        for product_id in product_ids:
            product = await self.product_repo.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")
            products.append(product)
            total_price += product.price

        # Create order
        order = Order(
            id=None,
            user_id=user_id,
            product_ids=product_ids,
            total_price=total_price,
            status="pending",
        )

        created_order = await self.order_repo.create(order)

        # Invalidate cache
        await self.cache.delete(f"cart:{user_id}")

        return created_order
