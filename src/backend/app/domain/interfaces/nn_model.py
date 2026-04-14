from __future__ import annotations

from pathlib import Path
from typing import Protocol

import torch


class NNModel(Protocol):
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        ...

    def save(self, path: str | Path) -> None:
        ...

    @classmethod
    def load(cls, path: str | Path, **kwargs) -> NNModel:
        ...
