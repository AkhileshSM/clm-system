from abc import ABC, abstractmethod
from typing import List
from ...models.schemas import Engineer

class SprintsDataProvider(ABC):
    @abstractmethod
    async def get_engineers(self) -> List[Engineer]:
        """Fetch current sprint data for all engineers."""
        pass

    @abstractmethod
    async def get_engineer_by_id(self, engineer_id: str) -> Engineer:
        """Fetch detailed data for a specific engineer."""
        pass
