"""
Panneau d'affichage et d'édition hexadécimal
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QPushButton, QScrollArea, QFrame,
    QSpinBox, QComboBox, QLineEdit, QGroupBox,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat, QSyntaxHighlighter
import re

class HexHighlighter(QSyntaxHighlighter):
    """Syntax highlighter pour l'affichage hexadécimal"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor(255, 255, 200))  # Jaune clair
        
        self.selection_format = QTextCharFormat()
        self.selection_format.setBackground(QColor(200, 230, 255))  # Bleu clair
        
        self.current_highlight = None
    
    def highlightBlock(self, text):
        """Surligne le bloc de texte"""
        if self.current_highlight is not None:
            start, length = self.current_highlight
            if 0 <= start < len(text):
                end = min(start + length, len(text))
                self.setFormat(start, end - start, self.highlight_format)

class HexPanel(QWidget):
    """Panneau d'affichage et d'édition hexadécimal"""
    
    # Signaux
    data_modified = pyqtSignal()
    offset_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.data = None
        self.current_offset = 0
        self.selection_start = None
        self.selection_end = None
        self.bytes_per_line = 16
        self.display_mode = 'hex'  # 'hex', 'dec', 'bin'
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialise l'interface"""
        main_layout = QVBoxLayout()
        
        # Barre d'outils supérieure
        toolbar = QHBoxLayout()
        
        # Navigation
        toolbar.addWidget(QLabel("Aller à:"))
        self.offset_input = QLineEdit()
        self.offset_input.setPlaceholderText("0x00000000")
        self.offset_input.setFixedWidth(100)
        toolbar.addWidget(self.offset_input)
        
        self.goto_button = QPushButton("Aller")
        self.goto_button.setFixedWidth(60)
        toolbar.addWidget(self.goto_button)
        
        toolbar.addWidget(QLabel(" | "))
        
        # Recherche
        toolbar.addWidget(QLabel("Rechercher:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Hex ou texte")
        self.search_input.setFixedWidth(150)
        toolbar.addWidget(self.search_input)
        
        self.search_button = QPushButton("Rechercher")
        self.search_button.setFixedWidth(100)
        toolbar.addWidget(self.search_button)
        
        toolbar.addStretch()
        
        # Options d'affichage
        toolbar.addWidget(QLabel("Bytes/ligne:"))
        self.bytes_combo = QComboBox()
        self.bytes_combo.addItems(["8", "16", "32", "48"])
        self.bytes_combo.setCurrentText("16")
        self.bytes_combo.setFixedWidth(60)
        toolbar.addWidget(self.bytes_combo)
        
        main_layout.addLayout(toolbar)
        
        # Zone d'affichage principale
        display_frame = QFrame()
        display_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        display_layout = QHBoxLayout()
        
        # Colonne des offsets
        self.offset_display = QTextEdit()
        self.offset_display.setFont(QFont("Consolas", 10))
        self.offset_display.setReadOnly(True)
        self.offset_display.setMaximumWidth(100)
        self.offset_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        display_layout.addWidget(self.offset_display)
        
        # Colonne hexadécimale
        self.hex_display = QTextEdit()
        self.hex_display.setFont(QFont("Consolas", 10))
        self.hex_display.setAcceptRichText(False)
        
        # Highlighter
        self.highlighter = HexHighlighter(self.hex_document())
        
        # Connecter les changements de sélection
        self.hex_display.selectionChanged.connect(self.on_selection_changed)
        display_layout.addWidget(self.hex_display)
        
        # Colonne ASCII
        self.ascii_display = QTextEdit()
        self.ascii_display.setFont(QFont("Consolas", 10))
        self.ascii_display.setReadOnly(True)
        self.ascii_display.setMaximumWidth(300)
        self.ascii_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        display_layout.addWidget(self.ascii_display)
        
        # Synchroniser les scrollbars
        self.hex_display.verticalScrollBar().valueChanged.connect(
            self.sync_scrollbars
        )
        
        display_frame.setLayout(display_layout)
        main_layout.addWidget(display_frame)
        
        # Barre d'information inférieure
        info_layout = QHBoxLayout()
        
        self.position_label = QLabel("Offset: 0x00000000 (0)")
        self.position_label.setFixedWidth(200)
        info_layout.addWidget(self.position_label)
        
        self.size_label = QLabel("Taille: 0 octets")
        self.size_label.setFixedWidth(150)
        info_layout.addWidget(self.size_label)
        
        self.selection_label = QLabel("Sélection: Aucune")
        self.selection_label.setFixedWidth(200)
        info_layout.addWidget(self.selection_label)
        
        self.value_label = QLabel("Valeur: -")
        self.value_label.setFixedWidth(200)
        info_layout.addWidget(self.value_label)
        
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout)
        
        # Panneau d'édition
        edit_group = QGroupBox("Édition")
        edit_layout = QGridLayout()
        
        # Éditeur de valeur
        edit_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "uint8", "int8", "uint16", "int16",
            "uint32", "int32", "uint64", "int64",
            "float", "double", "string"
        ])
        edit_layout.addWidget(self.type_combo, 0, 1)
        
        edit_layout.addWidget(QLabel("Valeur:"), 1, 0)
        self.value_edit = QLineEdit()
        edit_layout.addWidget(self.value_edit, 1, 1)
        
        self.write_button = QPushButton("Écrire")
        self.write_button.setFixedWidth(80)
        edit_layout.addWidget(self.write_button, 1, 2)
        
        edit_layout.addWidget(QLabel("Endianness:"), 0, 3)
        self.endian_combo = QComboBox()
        self.endian_combo.addItems(["Little-endian", "Big-endian"])
        edit_layout.addWidget(self.endian_combo, 0, 4)
        
        # Boutons d'action
        self.fill_button = QPushButton("Remplir...")
        self.fill_button.setFixedWidth(80)
        edit_layout.addWidget(self.fill_button, 1, 3)
        
        self.export_button = QPushButton("Exporter...")
        self.export_button.setFixedWidth(80)
        edit_layout.addWidget(self.export_button, 1, 4)
        
        edit_group.setLayout(edit_layout)
        main_layout.addWidget(edit_group)
        
        self.setLayout(main_layout)
    
    def setup_connections(self):
        """Configure les connections des signaux"""
        self.goto_button.clicked.connect(self.goto_offset)
        self.search_button.clicked.connect(self.search_data)
        self.bytes_combo.currentTextChanged.connect(self.change_bytes_per_line)
        self.write_button.clicked.connect(self.write_value)
        self.fill_button.clicked.connect(self.fill_data)
        self.export_button.clicked.connect(self.export_data)
        
        # Navigation avec clavier
        self.offset_input.returnPressed.connect(self.goto_offset)
        self.search_input.returnPressed.connect(self.search_data)
        
        # Mise à jour en temps réel
        self.hex_display.cursorPositionChanged.connect(self.update_position_info)
    
    def hex_document(self):
        """Retourne le document QTextDocument"""
        return self.hex_display.document()
    
    def set_data(self, data):
        """Définit les données à afficher"""
        self.data = data
        self.refresh_display()
        
        if data:
            self.size_label.setText(f"Taille: {len(data):,} octets")
        else:
            self.size_label.setText("Taille: 0 octets")
    
    def refresh_display(self):
        """Rafraîchit l'affichage"""
        if not self.data:
            self.offset_display.clear()
            self.hex_display.clear()
            self.ascii_display.clear()
            return
        
        # Calculer les lignes
        lines = []
        offset_lines = []
        ascii_lines = []
        
        for i in range(0, len(self.data), self.bytes_per_line):
            chunk = self.data[i:i + self.bytes_per_line]
            
            # Ligne offset
            offset_lines.append(f"{i:08X}")
            
            # Ligne hex
            hex_parts = []
            for j, byte in enumerate(chunk):
                hex_parts.append(f"{byte:02X}")
            
            # Remplir avec espaces si ligne incomplète
            while len(hex_parts) < self.bytes_per_line:
                hex_parts.append("  ")
            
            # Grouper par 8 bytes
            hex_line = ""
            for k in range(0, self.bytes_per_line, 8):
                group = hex_parts[k:k+8]
                hex_line += ' '.join(group) + '  '
            
            lines.append(hex_line.strip())
            
            # Ligne ASCII
            ascii_line = ""
            for byte in chunk:
                if 32 <= byte < 127:
                    ascii_line += chr(byte)
                else:
                    ascii_line += '.'
            
            # Remplir avec espaces
            ascii_line += ' ' * (self.bytes_per_line - len(chunk))
            ascii_lines.append(ascii_line)
        
        # Mettre à jour les displays
        self.offset_display.setText('\n'.join(offset_lines))
        self.hex_display.setText('\n'.join(lines))
        self.ascii_display.setText('\n'.join(ascii_lines))
        
        # Synchroniser les hauteurs
        self.sync_display_heights()
    
    def sync_display_heights(self):
        """Synchronise les hauteurs des displays"""
        # Tous ont le même nombre de lignes, donc même hauteur
        pass
    
    def sync_scrollbars(self, value):
        """Synchronise les scrollbars des différents displays"""
        self.offset_display.verticalScrollBar().setValue(value)
        self.ascii_display.verticalScrollBar().setValue(value)
    
    def update_position_info(self):
        """Met à jour les informations de position"""
        cursor = self.hex_display.textCursor()
        text = cursor.block().text()
        position_in_block = cursor.positionInBlock()
        
        # Trouver l'offset réel
        line_number = cursor.blockNumber()
        byte_pos = self.find_byte_position(text, position_in_block)
        
        if byte_pos is not None:
            offset = line_number * self.bytes_per_line + byte_pos
            self.current_offset = offset
            
            # Mettre à jour les labels
            self.position_label.setText(f"Offset: 0x{offset:08X} ({offset})")
            
            # Afficher la valeur à cette position
            if offset < len(self.data):
                byte_value = self.data[offset]
                self.value_label.setText(f"Valeur: 0x{byte_value:02X} ({byte_value})")
            
            # Émettre le signal
            self.offset_changed.emit(offset)
    
    def find_byte_position(self, line_text, cursor_pos):
        """
        Trouve la position du byte dans la ligne hex
        
        Args:
            line_text: Texte de la ligne
            cursor_pos: Position du curseur dans la ligne
            
        Returns:
            Position du byte (0-15) ou None
        """
        # Supprimer les espaces multiples
        cleaned = ' '.join(line_text.split())
        
        # Compter les espaces avant le curseur
        spaces_before = line_text[:cursor_pos].count(' ')
        
        # Position dans le texte nettoyé
        pos_in_cleaned = cursor_pos - spaces_before
        
        # Chaque byte prend 2 caractères + 1 espace (sauf dernier)
        byte_pos = pos_in_cleaned // 3
        
        # Vérifier les limites
        if byte_pos < 0 or byte_pos >= self.bytes_per_line:
            return None
        
        return byte_pos
    
    def on_selection_changed(self):
        """Quand la sélection change dans l'éditeur hex"""
        cursor = self.hex_display.textCursor()
        
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            
            # Convertir en offsets réels
            start_block = self.hex_display.document().findBlock(start)
            end_block = self.hex_display.document().findBlock(end)
            
            start_line = start_block.blockNumber()
            start_pos_in_block = start - start_block.position()
            
            end_line = end_block.blockNumber()
            end_pos_in_block = end - end_block.position()
            
            # Trouver les positions des bytes
            start_byte = self.find_byte_position(start_block.text(), start_pos_in_block)
            end_byte = self.find_byte_position(end_block.text(), end_pos_in_block)
            
            if start_byte is not None and end_byte is not None:
                start_offset = start_line * self.bytes_per_line + start_byte
                end_offset = end_line * self.bytes_per_line + end_byte
                
                # Assurer l'ordre
                if start_offset > end_offset:
                    start_offset, end_offset = end_offset, start_offset
                
                self.selection_start = start_offset
                self.selection_end = end_offset
                
                size = end_offset - start_offset + 1
                self.selection_label.setText(f"Sélection: {size} octet(s)")
                
                # Afficher la valeur sélectionnée
                if size <= 8:  # Afficher seulement pour les petites sélections
                    selected_data = self.data[start_offset:end_offset+1]
                    hex_str = ' '.join(f"{b:02X}" for b in selected_data)
                    self.value_label.setText(f"Sélection: {hex_str}")
    
    def goto_offset(self):
        """Va à l'offset spécifié"""
        if not self.data:
            return
        
        offset_text = self.offset_input.text().strip()
        
        try:
            # Supporter différents formats
            if offset_text.startswith('0x'):
                offset = int(offset_text, 16)
            else:
                offset = int(offset_text)
            
            # Vérifier les limites
            if offset < 0 or offset >= len(self.data):
                QMessageBox.warning(self, "Erreur", 
                                  f"Offset hors limites: 0x{offset:08X}")
                return
            
            # Calculer la ligne et la position
            line = offset // self.bytes_per_line
            column = offset % self.bytes_per_line
            
            # Convertir en position dans le texte
            text_cursor = self.hex_display.textCursor()
            
            # Aller à la ligne
            document = self.hex_display.document()
            block = document.findBlockByLineNumber(line)
            
            # Position dans la ligne: 3 caractères par byte (2 hex + 1 espace)
            text_pos = block.position() + column * 3
            
            # Déplacer le curseur
            text_cursor.setPosition(text_pos)
            self.hex_display.setTextCursor(text_cursor)
            self.hex_display.setFocus()
            
            # Faire défiler pour rendre visible
            self.hex_display.centerCursor()
            
            # Mettre à jour le label
            self.position_label.setText(f"Offset: 0x{offset:08X} ({offset})")
            
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Format d'offset invalide")
    
    def search_data(self):
        """Recherche du texte ou hex dans les données"""
        if not self.data:
            return
        
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        # Essayer d'interpréter comme hex d'abord
        search_bytes = None
        
        try:
            # Supprimer les espaces
            hex_text = search_text.replace(' ', '')
            
            # Si c'est du texte clair, encoder
            if all(c in '0123456789ABCDEFabcdef' for c in hex_text):
                if len(hex_text) % 2 == 1:
                    hex_text = '0' + hex_text
                search_bytes = bytes.fromhex(hex_text)
            else:
                # Traiter comme texte
                search_bytes = search_text.encode('utf-8')
        
        except:
            QMessageBox.warning(self, "Erreur", "Terme de recherche invalide")
            return
        
        # Rechercher à partir de la position courante + 1
        start_pos = self.current_offset + 1 if self.current_offset < len(self.data) - 1 else 0
        
        # Rechercher
        found_pos = self.data.find(search_bytes, start_pos)
        
        if found_pos == -1 and start_pos > 0:
            # Rechercher depuis le début
            found_pos = self.data.find(search_bytes, 0)
        
        if found_pos != -1:
            # Aller à la position trouvée
            self.offset_input.setText(f"0x{found_pos:08X}")
            self.goto_offset()
            
            # Surligner
            self.highlight_selection(found_pos, len(search_bytes))
            
            QMessageBox.information(self, "Recherche", 
                                  f"Trouvé à l'offset 0x{found_pos:08X}")
        else:
            QMessageBox.information(self, "Recherche", "Non trouvé")
    
    def highlight_selection(self, start, length):
        """Surligne une sélection dans l'éditeur hex"""
        self.current_highlight = (start, length)
        self.highlighter.rehighlight()
    
    def change_bytes_per_line(self, value):
        """Change le nombre de bytes par ligne"""
        self.bytes_per_line = int(value)
        if self.data:
            self.refresh_display()
    
    def write_value(self):
        """Écrit une valeur à la position courante"""
        if not self.data or self.current_offset >= len(self.data):
            return
        
        value_text = self.value_edit.text().strip()
        if not value_text:
            return
        
        value_type = self.type_combo.currentText()
        little_endian = self.endian_combo.currentText() == "Little-endian"
        
        try:
            # Convertir selon le type
            if value_type in ['uint8', 'int8', 'uint16', 'int16', 
                            'uint32', 'int32', 'uint64', 'int64']:
                # Entier
                base = 10
                if value_text.startswith('0x'):
                    base = 16
                elif value_text.startswith('0b'):
                    base = 2
                
                value = int(value_text, base) if base != 10 else int(value_text)
                
                # Déterminer la taille
                size_map = {
                    'uint8': 1, 'int8': 1,
                    'uint16': 2, 'int16': 2,
                    'uint32': 4, 'int32': 4,
                    'uint64': 8, 'int64': 8
                }
                
                size = size_map[value_type]
                signed = value_type.startswith('int')
                
                # Packer la valeur
                from utils.hex_utils import hex_utils
                new_bytes = hex_utils.write_int(
                    value, size, signed, little_endian
                )
            
            elif value_type in ['float', 'double']:
                # Flottant
                value = float(value_text)
                
                if value_type == 'float':
                    fmt = '<f' if little_endian else '>f'
                    new_bytes = struct.pack(fmt, value)
                else:
                    fmt = '<d' if little_endian else '>d'
                    new_bytes = struct.pack(fmt, value)
            
            elif value_type == 'string':
                # String
                new_bytes = value_text.encode('utf-8')
            
            # Vérifier qu'on a la place
            if self.current_offset + len(new_bytes) > len(self.data):
                QMessageBox.warning(self, "Erreur", "Pas assez de place")
                return
            
            # Écrire les bytes
            self.data[self.current_offset:self.current_offset + len(new_bytes)] = new_bytes
            
            # Rafraîchir l'affichage
            self.refresh_display()
            
            # Émettre le signal de modification
            self.data_modified.emit()
            
            QMessageBox.information(self, "Succès", "Valeur écrite")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'écriture: {str(e)}")
    
    def fill_data(self):
        """Remplit une zone avec une valeur"""
        # À implémenter
        QMessageBox.information(self, "Info", "Fonction à implémenter")
    
    def export_data(self):
        """Exporte les données sélectionnées"""
        # À implémenter
        QMessageBox.information(self, "Info", "Fonction à implémenter")
