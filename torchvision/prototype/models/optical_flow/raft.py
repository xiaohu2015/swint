from typing import Optional

from torch.nn.modules.batchnorm import BatchNorm2d
from torch.nn.modules.instancenorm import InstanceNorm2d
from torchvision.models.optical_flow import RAFT
from torchvision.models.optical_flow.raft import _raft, BottleneckBlock, ResidualBlock
from torchvision.prototype.transforms import RaftEval
from torchvision.transforms.functional import InterpolationMode

from .._api import WeightsEnum
from .._api import Weights
from .._utils import handle_legacy_interface


__all__ = (
    "RAFT",
    "raft_large",
    "raft_small",
    "Raft_Large_Weights",
    "Raft_Small_Weights",
)


_COMMON_META = {"interpolation": InterpolationMode.BILINEAR}


class Raft_Large_Weights(WeightsEnum):
    C_T_V1 = Weights(
        # Chairs + Things, ported from original paper repo (raft-things.pth)
        url="https://download.pytorch.org/models/raft_large_C_T_V1-22a6c225.pth",
        transforms=RaftEval,
        meta={
            **_COMMON_META,
            "recipe": "https://github.com/princeton-vl/RAFT",
            "sintel_train_cleanpass_epe": 1.4411,
            "sintel_train_finalpass_epe": 2.7894,
        },
    )

    C_T_V2 = Weights(
        # Chairs + Things
        url="https://download.pytorch.org/models/raft_large_C_T_V2-1bb1363a.pth",
        transforms=RaftEval,
        meta={
            **_COMMON_META,
            "recipe": "https://github.com/pytorch/vision/tree/main/references/optical_flow",
            "sintel_train_cleanpass_epe": 1.3822,
            "sintel_train_finalpass_epe": 2.7161,
        },
    )

    # C_T_SKHT_V1 = Weights(
    #     # Chairs + Things + Sintel fine-tuning, i.e.:
    #     # Chairs + Things + (Sintel + Kitti + HD1K + Things_clean)
    #     # Corresponds to the C+T+S+K+H on paper with fine-tuning on Sintel
    #     url="",
    #     transforms=RaftEval,
    #     meta={
    #         "recipe": "",
    #         "epe": -1234,
    #     },
    # )

    # C_T_SKHT_K_V1 = Weights(
    #     # Chairs + Things + Sintel fine-tuning + Kitti fine-tuning i.e.:
    #     # Chairs + Things + (Sintel + Kitti + HD1K + Things_clean) + Kitti
    #     # Same as CT_SKHT with extra fine-tuning on Kitti
    #     # Corresponds to the C+T+S+K+H on paper with fine-tuning on Sintel and then on Kitti
    #     url="",
    #     transforms=RaftEval,
    #     meta={
    #         "recipe": "",
    #         "epe": -1234,
    #     },
    # )

    default = C_T_V2


class Raft_Small_Weights(WeightsEnum):
    C_T_V1 = Weights(
        # Chairs + Things, ported from original paper repo (raft-small.pth)
        url="https://download.pytorch.org/models/raft_small_C_T_V1-ad48884c.pth",
        transforms=RaftEval,
        meta={
            **_COMMON_META,
            "recipe": "https://github.com/princeton-vl/RAFT",
            "sintel_train_cleanpass_epe": 2.1231,
            "sintel_train_finalpass_epe": 3.2790,
        },
    )

    default = C_T_V1  # TODO: Change to V2 once we upload our own weights


@handle_legacy_interface(weights=("pretrained", Raft_Large_Weights.C_T_V2))
def raft_large(*, weights: Optional[Raft_Large_Weights] = None, progress=True, **kwargs):
    """RAFT model from
    `RAFT: Recurrent All Pairs Field Transforms for Optical Flow <https://arxiv.org/abs/2003.12039>`_.

    Args:
        weights(Raft_Large_weights, optional): pretrained weights to use.
        progress (bool): If True, displays a progress bar of the download to stderr
        kwargs (dict): Parameters that will be passed to the :class:`~torchvision.models.optical_flow.RAFT` class
            to override any default.

    Returns:
        nn.Module: The model.
    """

    weights = Raft_Large_Weights.verify(weights)

    model = _raft(
        # Feature encoder
        feature_encoder_layers=(64, 64, 96, 128, 256),
        feature_encoder_block=ResidualBlock,
        feature_encoder_norm_layer=InstanceNorm2d,
        # Context encoder
        context_encoder_layers=(64, 64, 96, 128, 256),
        context_encoder_block=ResidualBlock,
        context_encoder_norm_layer=BatchNorm2d,
        # Correlation block
        corr_block_num_levels=4,
        corr_block_radius=4,
        # Motion encoder
        motion_encoder_corr_layers=(256, 192),
        motion_encoder_flow_layers=(128, 64),
        motion_encoder_out_channels=128,
        # Recurrent block
        recurrent_block_hidden_state_size=128,
        recurrent_block_kernel_size=((1, 5), (5, 1)),
        recurrent_block_padding=((0, 2), (2, 0)),
        # Flow head
        flow_head_hidden_size=256,
        # Mask predictor
        use_mask_predictor=True,
        **kwargs,
    )

    if weights is not None:
        model.load_state_dict(weights.get_state_dict(progress=progress))

    return model


# TODO: change to V2 once we upload our own weights
@handle_legacy_interface(weights=("pretrained", Raft_Small_Weights.C_T_V1))
def raft_small(*, weights: Optional[Raft_Small_Weights] = None, progress=True, **kwargs):
    """RAFT "small" model from
    `RAFT: Recurrent All Pairs Field Transforms for Optical Flow <https://arxiv.org/abs/2003.12039>`_.

    Args:
        weights(Raft_Small_weights, optinal): TODO not implemented yet
        progress (bool): If True, displays a progress bar of the download to stderr
        kwargs (dict): Parameters that will be passed to the :class:`~torchvision.models.optical_flow.RAFT` class
            to override any default.

    Returns:
        nn.Module: The model.

    """

    weights = Raft_Small_Weights.verify(weights)

    model = _raft(
        # Feature encoder
        feature_encoder_layers=(32, 32, 64, 96, 128),
        feature_encoder_block=BottleneckBlock,
        feature_encoder_norm_layer=InstanceNorm2d,
        # Context encoder
        context_encoder_layers=(32, 32, 64, 96, 160),
        context_encoder_block=BottleneckBlock,
        context_encoder_norm_layer=None,
        # Correlation block
        corr_block_num_levels=4,
        corr_block_radius=3,
        # Motion encoder
        motion_encoder_corr_layers=(96,),
        motion_encoder_flow_layers=(64, 32),
        motion_encoder_out_channels=82,
        # Recurrent block
        recurrent_block_hidden_state_size=96,
        recurrent_block_kernel_size=(3,),
        recurrent_block_padding=(1,),
        # Flow head
        flow_head_hidden_size=128,
        # Mask predictor
        use_mask_predictor=False,
        **kwargs,
    )

    if weights is not None:
        model.load_state_dict(weights.get_state_dict(progress=progress))
    return model