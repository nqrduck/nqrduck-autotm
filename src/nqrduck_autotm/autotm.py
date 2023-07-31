from nqrduck.module.module import Module
from .model import AutoTMModel
from .view import AutoTMView
from .controller import AutoTMController

AutoTM = Module(AutoTMModel, AutoTMView, AutoTMController)