from __future__ import annotations

from pathlib import Path

import torch
from torch import nn

from app.domain.interfaces.nn_model import NNModel


class LSTMAutoencoder(nn.Module, NNModel):
    name = "lstm_autoencoder"

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        latent_dim: int = 32,
        num_layers: int = 1,
        dropout: float = 0.0

    ):
        super().__init__()

        if input_dim <= 0 or latent_dim <= 0 or hidden_dim <= 0:
            raise ValueError(
                "`input_dim`, `hidden_dim` and `latent_dim` must be positive integers.")

        if dropout < 0 or dropout >= 1:
            raise ValueError("`dropout` must be in range [0, 1).")

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.num_layers = num_layers
        self.dropout = dropout

        self.encoder = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=self.dropout if num_layers > 1 else 0.0,
        )

        self.fc_enc = nn.Linear(hidden_dim, latent_dim)
        self.fc_dec = nn.Linear(latent_dim, hidden_dim)

        self.decoder = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=self.dropout if num_layers > 1 else 0.0,
        )

        self.output_layer = nn.Linear(hidden_dim, input_dim)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_dim)
        # enc_out: (batch_size, seq_len, hidden_dim * num_directions)
        enc_out, _ = self.encoder(x)
        # (batch, seq_len, latent_dim)
        z_seq = self.fc_enc(enc_out)
        return z_seq

    def decode(self, z_seq: torch.Tensor) -> torch.Tensor:
        # z_seq: (batch, seq_len, latent_dim)
        # z_seq:(batch, seq_len, hidden_dim)
        dec_input = self.fc_dec(z_seq)
        # dec_out: (batch, seq_len, hidden_dim * directions)
        dec_out, _ = self.decoder(dec_input)
        return self.output_layer(dec_out)

    def forward(self, x: torch.Tensor, return_latent: bool = False) -> tuple[torch.Tensor, torch.Tensor] | torch.Tensor:
        # x: (batch, seq_len, input_dim) or (batch, input_dim) -> treated as seq_len=1
        if x.dim() == 2:
            x = x.unsqueeze(1)  # (batch, 1, input_dim)
        z_seq = self.encode(x)
        recon = self.decode(z_seq)
        return (recon, z_seq) if return_latent else recon

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        recon = self.forward(x)
        return torch.mean((x - recon) ** 2, dim=(1, 2))

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self.state_dict(),
                "input_dim": self.input_dim,
                "hidden_dim": self.hidden_dim,
                "latent_dim": self.latent_dim,
                "num_layers": self.num_layers,
                "dropout": self.dropout
            },
            path,
        )

    @classmethod
    def load(cls, path: str | Path, **kwargs) -> LSTMAutoencoder:
        data = torch.load(path, map_location=kwargs.get("device", "cpu"))
        model = cls(
            input_dim=data["input_dim"],
            hidden_dim=data["hidden_dim"],
            latent_dim=data["latent_dim"],
            num_layers=data["num_layers"],
            dropout=data["dropout"]
        )
        model.load_state_dict(data["state_dict"])
        return model
