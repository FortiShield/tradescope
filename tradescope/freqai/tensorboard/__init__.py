# ensure users can still use a non-torch freqai version
try:
    from tradescope.freqai.tensorboard.tensorboard import TensorBoardCallback, TensorboardLogger
    TBLogger = TensorboardLogger
    TBCallback = TensorBoardCallback
except ModuleNotFoundError:
    from tradescope.freqai.tensorboard.base_tensorboard import (BaseTensorBoardCallback,
                                                                BaseTensorboardLogger)
    TBLogger = BaseTensorboardLogger  # type: ignore
    TBCallback = BaseTensorBoardCallback  # type: ignore

__all__ = (
    "TBLogger",
    "TBCallback"
)
