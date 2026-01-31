"""
Boîte de dialogue pour éditer l'argent
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QGroupBox, QFormLayout,
    QRadioButton, QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt

class MoneyEditorDialog(QDialog):
    """Dialogue pour modifier l'argent du jeu"""
    
    def __init__(self, current_money, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Éditeur d'argent")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self.current_money = current_money
        self.selected_value = current_money
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout()
        
        # Groupe: Valeur actuelle
        current_group = QGroupBox("Valeur actuelle")
        current_layout = QFormLayout()
        
        current_label = QLabel(f"{self.current_money:,} €")
        current_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: green;")
        current_layout.addRow("Argent actuel:", current_label)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # Groupe: Nouvelle valeur
        edit_group = QGroupBox("Nouvelle valeur")
        edit_layout = QVBoxLayout()
        
        # Option: Saisie manuelle
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Montant:"))
        
        self.money_spinbox = QSpinBox()
        self.money_spinbox.setRange(-1000000000, 100000000000)
        self.money_spinbox.setValue(self.current_money)
        self.money_spinbox.setSingleStep(1000)
        self.money_spinbox.setSuffix(" €")
        self.money_spinbox.valueChanged.connect(self.on_value_changed)
        
        # Format avec séparateurs de milliers
        self.money_spinbox.setDisplayIntegerBase(10)
        
        manual_layout.addWidget(self.money_spinbox)
        manual_layout.addStretch()
        edit_layout.addLayout(manual_layout)
        
        # Options prédéfinies
        presets_group = QGroupBox("Présélections")
        presets_layout = QVBoxLayout()
        
        self.preset_buttons = QButtonGroup(self)
        presets = [
            ("Débutant", 100000),
            ("Normal", 500000),
            ("Aisé", 2000000),
            ("Millionnaire", 10000000),
            ("Milliardaire", 1000000000),
            ("Illimité", 999999999)
        ]
        
        for text, value in presets:
            radio = QRadioButton(f"{text} ({value:,} €)")
            radio.value = value
            self.preset_buttons.addButton(radio)
            presets_layout.addWidget(radio)
        
        self.preset_buttons.buttonClicked.connect(self.on_preset_selected)
        presets_group.setLayout(presets_layout)
        edit_layout.addWidget(presets_group)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Appliquer")
        self.apply_button.clicked.connect(self.accept)
        self.apply_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_value_changed(self, value):
        """Quand la valeur est changée manuellement"""
        self.selected_value = value
        
        # Désélectionner les presets
        for button in self.preset_buttons.buttons():
            button.setChecked(False)
    
    def on_preset_selected(self, button):
        """Quand un preset est sélectionné"""
        self.selected_value = button.value
        self.money_spinbox.setValue(button.value)
    
    def get_value(self):
        """Retourne la valeur sélectionnée"""
        return self.selected_value
    
    def accept(self):
        """Confirme la modification"""
        if self.selected_value == self.current_money:
            QMessageBox.information(self, "Information", 
                                  "La valeur n'a pas changé.")
            self.reject()
            return
        
        # Vérifier les limites
        if self.selected_value < -1000000000:
            QMessageBox.warning(self, "Attention", 
                              "La valeur est trop basse.")
            return
        
        if self.selected_value > 100000000000:
            reply = QMessageBox.question(
                self, "Confirmation",
                "Valeur très élevée. Êtes-vous sûr ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        super().accept()
