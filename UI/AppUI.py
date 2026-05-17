from .BaseUI import BaseUI
from .AttributeUI import AttributeUI
from .SidebarUI import SidebarUI
from Logic.AppLogic import AppLogic

class AppUI(BaseUI, AttributeUI, SidebarUI):
    def __init__(self, root):
        super().__init__(root)
        self.logic = AppLogic()
        self.current_op = None
        self.current_res_cv = None
        self.active_sliders = {}
        
        self.setup_base_layout()
        self.setup_sidebar()
        self.setup_action_panel()
