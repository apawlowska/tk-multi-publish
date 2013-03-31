"""
Copyright (c) 2013 Shotgun Software, Inc
----------------------------------------------------
"""

from tank.platform.qt import QtCore, QtGui
from .ui.publish_ui import Ui_publish_form

class PublishUI(QtGui.QWidget):
    """
    Implementation of the main publish UI
    """

    # signals
    publish = QtCore.Signal()
    #closed = QtCore.Signal()
    
    def __init__(self, app, handler):
        """
        Construction
        """
        QtGui.QWidget.__init__(self)
        self._app = app
        self._handler = handler
    
        self._tasks = []
        
        # TODO - temp selection mechanism - should be 
        # retrieved from task list in UI
        self._selected_tasks = []
        
        # set up the UI
        self._ui = Ui_publish_form() 
        self._ui.setupUi(self)
        
        self._ui.publish_btn.clicked.connect(self._on_publish)
        self._ui.cancel_btn.clicked.connect(self._on_cancel)
        
        self._ui.select_all_btn.clicked.connect(self._on_select_all)
        self._ui.select_req_only_btn.clicked.connect(self._on_select_req_only)
        self._ui.select_random_btn.clicked.connect(self._on_select_random)
        
        self._update_ui()
        
    @property
    def selected_tasks(self):
        """
        The currently selected tasks
        """
        return self._selected_tasks
    
    @property
    def shotgun_task(self):
        """
        The shotgun task that the publish should be linked to
        """
        return self._shotgun_task
    
    @property
    def thumbnail(self):
        """
        The thumbnail to use for the publish
        """
        return None
    
    @property
    def comment(self):
        """
        The comment to use for the publish
        """
        return ""
        
    def reload(self):
        """
        Load UI with data provided by the handler:
        """
        self._tasks = self._handler.get_tasks()
        
        for task in self._tasks:
            if task.output.selected:
                self._selected_tasks.append(task)
        
        self._update_ui()
        
    def update_tasks(self):
        """
        Placeholder to update UI for all tasks without reloading
        - UI will ultimately update via a signal from the task
        itself
        """
        self._update_ui()
        
    def _on_publish(self):
        """
        Slot called when the publish button in the dialog is clicked
        """
        self.publish.emit()
        
    def _on_cancel(self):
        """
        Slot called when the cancel button in the dialog is clicked
        """
        self.window().close()
    
    # (AD) - temp for proxy UI
    def _on_select_all(self):
        self._selected_tasks = self._tasks
        self._update_ui()
        
    def _on_select_req_only(self):
        self._selected_tasks = []
        for task in self._tasks:
            if task.output.required:
                self._selected_tasks.append(task)
        self._update_ui()

    def _on_select_random(self):
        import random
        self._selected_tasks = []
        for task in self._tasks:
            if task.output.required:
                self._selected_tasks.append(task)
            else:
                if random.random() > 0.5:
                    self._selected_tasks.append(task)
        self._update_ui()
 
    def _update_ui(self):
        """
        Update the UI following a change to the data
        """
        msg = ""
        
        if not self._tasks:
            msg = "Nothing to publish!"
        else:
            selected_char = [[" ", "X"], [" ", "R"]]
            error_char = ["", "(!)"]

            group_info = {}
            group_order = []
            for task in self._tasks:
                if task.output.display_group not in group_order:
                    group_order.append(task.output.display_group)
                    
                group_info.setdefault(task.output.display_group, dict())
                group_info[task.output.display_group].setdefault("outputs", set()).add(task.output)
                group_info[task.output.display_group].setdefault("selected_outputs", set())
                group_info[task.output.display_group].setdefault("error_outputs", set())
                group_info[task.output.display_group].setdefault("items", set()).add(task.item)
                group_info[task.output.display_group].setdefault("selected_items", set())
                group_info[task.output.display_group].setdefault("error_items", set())
                group_info[task.output.display_group].setdefault("errors", list())
                if task in self._selected_tasks:
                    group_info[task.output.display_group]["selected_outputs"].add(task.output)
                    group_info[task.output.display_group]["selected_items"].add(task.item)
                if task.pre_publish_errors:
                    group_info[task.output.display_group]["error_outputs"].add(task.output)
                    group_info[task.output.display_group]["error_items"].add(task.item)
                    group_info[task.output.display_group]["errors"].extend(task.pre_publish_errors)
                    
            msg = "Select things to publish...\n\n"
            for g in group_order:
                msg += "\n  %s" % g
                info = group_info[g]
                
                msg += "\n    Outputs:"
                any_output_is_required = False
                for output in info["outputs"]:
                    is_selected = output in info["selected_outputs"]
                    is_required = output.required
                    has_errors = output in info["error_outputs"]
                    if is_required:
                        any_output_is_required = True
                    msg += "\n      - [%s] %s %s" % (selected_char[is_required][is_selected], output.display_name, error_char[has_errors])
                    
                msg += "\n    Items:"
                for item in info["items"]:
                    is_selected = item in info["selected_items"]
                    has_errors = item in info["error_items"]
                    msg += "\n      - [%s] %s %s" % (selected_char[any_output_is_required][is_selected], item.name, error_char[has_errors])
                    
                errors = info["errors"]
                if errors:
                    msg += "\n    %d Errors:" % len(errors)
                    for ei, error in enumerate(errors):
                        msg += "\n      (%d) - %s" % (ei+1, error)
                    
            
        self._ui.publish_details.setText(msg)
        
        
        
        
        
        
        
        
        
        
        
        
        