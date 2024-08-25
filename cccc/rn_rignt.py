    def show_update_box_context_menu(self, position):
        """显示自定义的右键菜单"""
        menu = QMenu(self)
        clear_action = menu.addAction("清空")
        action = menu.exec(self.update_box.mapToGlobal(position))
        if action == clear_action:
            self.update_box.clear()
            
self.update_box = QTextEdit(self)
self.update_box.setReadOnly(True)
self.update_box.setContextMenuPolicy(Qt.CustomContextMenu)
self.update_box.customContextMenuRequested.connect(self.show_update_box_context_menu)